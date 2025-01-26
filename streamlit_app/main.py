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
output_file = "processed_excerpts.xlsx"
process_data(input_file, output_file)

# Load the processed data
dataframe = pd.read_excel(output_file)

# Convert string representations of lists back to actual lists
dataframe["entities"] = dataframe["entities"].apply(ast.literal_eval)
dataframe["relationships"] = dataframe["relationships"].apply(ast.literal_eval)

# Flatten the relationships column
all_entities = [ent for sublist in dataframe["entities"] for ent in sublist]
all_relationships = [rel for sublist in dataframe["relationships"] for rel in sublist]

# Clean the relationships
cleaned_entities = clean_entities(all_entities)
cleaned_relationships = clean_relationships(all_relationships)

# Generate insights
entity_counts, relationship_counts = generate_insights(dataframe)

# Save insights to a file (optional)
with open("insights.txt", "w") as f:
    f.write("Top Entities:\n")
    for entity, count in entity_counts.most_common(10):
        f.write(f"{entity}: {count}\n")
    f.write("\nTop Relationships:\n")
    for relationship, count in relationship_counts.most_common(10):
        f.write(f"{relationship}: {count}\n")