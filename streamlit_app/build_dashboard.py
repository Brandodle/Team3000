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
        text=counts
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
    pos = nx.spring_layout(G)
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='red'),
        hoverinfo='none',
        mode='lines'
    ))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
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
        height=600
    )
    return fig

def resolve_errors(df):
    resolved_messages = []

    # 1. Resolve duplicates (exact duplicates in 'Text' column)
    duplicates = df[df.duplicated(subset=['Text'], keep=False)]
    df = df.drop_duplicates(subset=['Text'])
    if not duplicates.empty:
        resolved_messages.append(f"Removed {len(duplicates)} duplicate entries.")

    # 2. Resolve missing values (optional: remove rows with missing values in 'Text')
    missing_values = df[df['Text'].isna()]
    if not missing_values.empty:
        df = df.dropna(subset=['Text'])
        resolved_messages.append(f"Removed {len(missing_values)} rows with missing text values.")

    # 3. Resolve subset duplicates (keep the longer text)
    def clean_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = ' '.join(text.split())
        return text

    cleaned_texts = df['Text'].apply(clean_text).values

    rows_to_remove = set()
    for i in range(len(cleaned_texts)):
        for j in range(i + 1, len(cleaned_texts)):
            text_i = cleaned_texts[i]
            text_j = cleaned_texts[j]
            
            if text_i in text_j or text_j in text_i:
                if len(text_i) > len(text_j):
                    rows_to_remove.add(j)
                else:
                    rows_to_remove.add(i)

    df = df.drop(rows_to_remove)
    if rows_to_remove:
        resolved_messages.append(f"Removed {len(rows_to_remove)} rows due to subset duplicates.")

    # 4. Combine Text for rows where the first column is the same (using .iloc for the first column)
    first_column_name = df.columns[0]  # Get the name of the first column dynamically
    df_combined = df.groupby(first_column_name)['Text'].apply(lambda x: ' '.join(x)).reset_index()
    
    resolved_messages.append(f"Combined texts for rows with the same '{first_column_name}'.")
    
    return df_combined, resolved_messages


def main():
    st.title("Entity and Relationship Dashboard")

    # File upload section
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
    if uploaded_file:
        # Save the uploaded file temporarily
        input_file = "uploaded_file.xlsx"
        with open(input_file, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load the dataset
        df = pd.read_excel(input_file)

        # Step 1: Validate the data and show errors
        validation_log = validate_data(df)
        if not validation_log.empty:
            st.write("### Validation Errors")
            st.write(validation_log)

        # Step 2: Automatically resolve the errors
        df, resolved_messages = resolve_errors(df)
        
        # Display resolved messages to the user
        if resolved_messages:
            st.write("### Resolved Errors")
            for message in resolved_messages:
                st.success(message)

        # Save the updated DataFrame after resolving errors
        output_file = "resolved_file.xlsx"
        df.to_excel(output_file, index=False)

        # Allow the user to download the updated file
        st.download_button("Download the updated file", data=open(output_file, 'rb'), file_name="resolved_data.xlsx")

        # Step 3: Process and analyze the cleaned data
        # Now process the data using the `process_data` function
        # Pass both input_file and output_file to process_data
        process_data(input_file, output_file)  # This will process and save the file

        # Load processed data
        dataframe = pd.read_excel(output_file)
        dataframe["entities"] = dataframe["entities"].apply(ast.literal_eval)
        dataframe["relationships"] = dataframe["relationships"].apply(ast.literal_eval)

        # Flatten entities and relationships
        all_entities = [entity for sublist in dataframe["entities"] for entity in sublist]
        all_relationships = [rel for sublist in dataframe["relationships"] for rel in sublist]

        # Generate insights
        entity_counts, relationship_counts = generate_insights(dataframe)

        # Display entities
        st.write("### Entities")
        st.write(dataframe["entities"].explode().value_counts().reset_index().rename(columns={"index": "Entity", "entities": "Count"}))

        # Visualize top entities
        st.write("### Top 10 Entities (Interactive)")
        entity_fig = visualize_entities(entity_counts)
        st.plotly_chart(entity_fig, use_container_width=True)

        # Display relationships
        st.write("### Relationships")
        st.write(dataframe["relationships"].explode().value_counts().reset_index().rename(columns={"index": "Relationship", "relationships": "Count"}))

        # Visualize relationships
        st.write("### Relationship Network Graph")
        relationship_fig = visualize_relationships(all_relationships)
        st.plotly_chart(relationship_fig, use_container_width=True)
    else:
        st.write("Please upload a file to see the analysis.")

if __name__ == "__main__":
    main()