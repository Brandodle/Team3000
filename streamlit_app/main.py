import pandas as pd
import ast
from extract_entities_relationships import process_data
from generate_insights import generate_insights

# Function to clean relationships
def clean_relationships(relationships):
    cleaned_relationships = []
    for rel in relationships:
        subject, verb, object_ = rel
        # Filter out relationships with empty subjects or objects
        if subject.strip() and object_.strip():
            cleaned_relationships.append((subject, verb, object_))
        else:
            print(f"Skipping invalid relationship: {rel}")
    return cleaned_relationships

def clean_entities(entities):
    cleaned_entities = []
    for pair in entities:
        entity, label = pair
        # Filter out relationships with empty subjects or objects
        if entity.strip() and label.strip():
            cleaned_entities.append((entity, label))
        else:
            print(f"Skipping invalid relationship: {pair}")
    return cleaned_entities

# Process the data
input_file = "excerpts_parsed.xlsx"
dataframe = process_data(input_file)

# Clean the entities and relationships
all_entities = [ent for sublist in dataframe["entities"] for ent in sublist]
all_relationships = [rel for sublist in dataframe["relationships"] for rel in sublist]

cleaned_entities = clean_entities(all_entities)
cleaned_relationships = clean_relationships(all_relationships)

# Generate insights
entity_counts, relationship_counts = generate_insights(dataframe)

# Pass the processed DataFrame directly to Streamlit or for further analysis
