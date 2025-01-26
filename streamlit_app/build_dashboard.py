import streamlit as st
import pandas as pd
import ast
from generate_insights import generate_insights
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from extract_entities_relationships import process_data

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

# Main app
def main():
    st.title("Entity and Relationship Dashboard")

    # File upload section
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
    if uploaded_file:
        # Save the uploaded file temporarily
        input_file = "uploaded_file.xlsx"
        with open(input_file, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process the uploaded file
        output_file = "processed_excerpts.xlsx"
        process_data(input_file, output_file)

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
