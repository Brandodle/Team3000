import streamlit as st
import pandas as pd
from generate_insights import generate_insights
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from extract_entities_relationships import process_data
from validate_data import validate_data
import ast
import string
from topic_modeling import perform_lda_topic_modeling, plot_lda_topics  # Import the LDA functions
from text_search import highlight_entities


# Set page configuration for wide layout & add custom CSS for styling
st.set_page_config(layout="wide")
st.markdown("""
    <style>
        /* Global Styling */
        body {
            background-color: #f5f5f5;
        }
        
        /* Titles & Headers */
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #004080;
        }
        
        .subheader {
            font-size: 24px;
            font-weight: bold;
            color: #004080;
        }
        
        /* Cards for Sections */
        .section {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        /* Styled Buttons */
        .stButton>button {
            background-color: #004080;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
        }
        
        /* Success Message Styling */
        .stAlert {
            background-color: #d1ecf1;
            color: #004085;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Function to resolve errors and clean the dataset
def resolve_errors(df):
    resolved_messages = []
    duplicates = df[df.duplicated(subset=['Text'], keep=False)]
    df = df.drop_duplicates(subset=['Text'])
    if not duplicates.empty:
        resolved_messages.append(f"✅ Removed {len(duplicates)} duplicate entries.")

    missing_values = df[df['Text'].isna()]
    if not missing_values.empty:
        df = df.dropna(subset=['Text'])
        resolved_messages.append(f"✅ Removed {len(missing_values)} rows with missing text values.")

    first_column_name = df.columns[0]
    df_combined = df.groupby(first_column_name)['Text'].apply(lambda x: ' '.join(x)).reset_index()
    resolved_messages.append(f"✅ Combined texts for rows with the same '{first_column_name}'.")

    return df_combined, resolved_messages

# Function to visualize entities
def visualize_entities(entity_counts):
    top_entities = entity_counts.most_common(10)
    entities = [f"{entity[0][0]} ({entity[0][1]})" for entity in top_entities]
    counts = [count for _, count in top_entities]
    fig = px.bar(
        x=entities, 
        y=counts, 
        labels={'x': 'Entities', 'y': 'Frequency'},
        title="Top 10 Entities",
        text=counts,
        color_discrete_sequence=['#004080']
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    return fig

# Function to visualize relationships
def visualize_relationships(all_relationships):
    G = nx.Graph()
    for rel in all_relationships:
        if isinstance(rel, tuple) and len(rel) == 3:
            subject, verb, obj = rel
            G.add_node(subject)
            G.add_node(obj)
            G.add_edge(subject, obj, label=verb)
    
    if len(G.nodes) == 0:
        st.warning("⚠️ No relationships found in the dataset.")
        return go.Figure()

    pos = nx.spring_layout(G)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#004080'),
        hoverinfo='none',
        mode='lines'
    ))
    fig.add_trace(go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        text=list(G.nodes()),
        textposition="top center",
        textfont=dict(color='black'),
        marker=dict(size=20, color='lightblue', line=dict(width=2, color='darkblue')),
        hoverinfo='text'
    ))
    fig.update_layout(
        title='Relationship Network',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    return fig

# Main function
def main():
    st.markdown('<h1 class="title">Entity and Relationship Dashboard</h1>', unsafe_allow_html=True)

    # File upload section
    uploaded_file = st.file_uploader("📂 Upload an Excel file", type=["xlsx"])
    if uploaded_file:
        input_file = "uploaded_file.xlsx"
        with open(input_file, "wb") as f:
            f.write(uploaded_file.getbuffer())

        df = pd.read_excel(input_file)

        # Step 1: Validate the data and show errors
        validation_log = validate_data(df)
        if not validation_log.empty:
            st.markdown('<div class="section"><h3 class="subheader">Validation Errors</h3></div>', unsafe_allow_html=True)
            st.write(validation_log)

        # Step 2: Automatically resolve the errors
        df, resolved_messages = resolve_errors(df)
        
        if resolved_messages:
            st.markdown('<div class="section"><h3 class="subheader">✅ Resolved Errors</h3></div>', unsafe_allow_html=True)
            for message in resolved_messages:
                st.success(message)

        # Save the updated DataFrame after resolving errors
        output_file = "resolved_file.xlsx"
        df.to_excel(output_file, index=False)

        # Download button for cleaned data
        with open(output_file, "rb") as file:
            st.download_button(label="⬇️ Download the cleaned Excel file",
                               data=file,
                               file_name="resolved_data.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Step 3: Process and analyze the cleaned data
        process_data(input_file, output_file)

        dataframe = pd.read_excel(output_file)
        dataframe["entities"] = dataframe["entities"].apply(ast.literal_eval)
        dataframe["relationships"] = dataframe["relationships"].apply(ast.literal_eval)

        all_entities = [entity for sublist in dataframe["entities"] for entity in sublist]
        all_relationships = [rel for sublist in dataframe["relationships"] for rel in sublist]

        entity_counts, relationship_counts = generate_insights(dataframe)

        # 2x2 Dashboard Layout
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        col5, col6 = st.columns(2)  # Third Row (Text Search + Empty Space)

        with col1:
            st.subheader("📊 Top 10 Entities")
            entity_fig = visualize_entities(entity_counts)
            st.plotly_chart(entity_fig, use_container_width=True)

        with col2:
            st.subheader("🔗 Relationship Network")
            relationship_fig = visualize_relationships(all_relationships)
            st.plotly_chart(relationship_fig, use_container_width=True)

        with col3:
            st.subheader("📂 Topic Modeling")
            num_topics = st.slider("Number of Topics", 2, 10, 5)
            topics, lda_model, vectorizer = perform_lda_topic_modeling(dataframe, num_topics)
            with st.expander("📌 View Topics", expanded=True):
                for topic, words in topics:
                    st.write(f"**{topic}:** {', '.join(words)}")

        with col4:
            st.subheader("📑 LDA Topic Visualization")
            lda_fig = plot_lda_topics(lda_model, vectorizer, num_topics)
            st.plotly_chart(lda_fig, use_container_width=True)

        with col5:
            st.subheader("🔍 Entity Search and Highlight Tool")

            # Text Input Box for User Search
            user_text = st.text_area("Enter text for entity extraction:", key="entity_search")

            if st.button("Highlight Entities", key="highlight_button"):
                if user_text.strip():  # Ensure text is not empty
                    highlighted_text, extracted_entities = highlight_entities(user_text)

                    # Display highlighted text
                    st.markdown(f"<div>{highlighted_text}</div>", unsafe_allow_html=True)

                    # Display extracted entities
                    st.subheader("Extracted Entities")
                    st.write(extracted_entities)
                else:
                    st.warning("⚠️ Please enter some text before clicking highlight.")

 
    # Custom CSS for styling highlights
    st.markdown("""
        <style>
            .highlight { font-weight: bold; padding: 2px 4px; border-radius: 3px; }
            .person { background-color: lightblue; }
            .org { background-color: yellow; }
            .gpe { background-color: lightgreen; }
            .date { background-color: orange; }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
