# import spacy
# import pandas as pd

# # Load the SpaCy model
# nlp = spacy.load("en_core_web_sm")

# # Function to extract entities
# def extract_entities(text):
#     doc = nlp(text)
#     return [(ent.text, ent.label_) for ent in doc.ents]

# # Function to extract relationships
# def extract_relationships(text):
#     doc = nlp(text)
#     relationships = []
#     for sent in doc.sents:
#         for token in sent:
#             if token.pos_ == "VERB":
#                 subject = None
#                 object_ = None
#                 for child in token.children:
#                     if child.dep_ in ("nsubj", "nsubjpass"):
#                         subject = child.text
#                     elif child.dep_ in ("dobj", "attr", "prep"):
#                         object_ = child.text
#                 if subject and object_:
#                     relationships.append((subject, token.text, object_))
#     return relationships

# # Main function to process the data
# def process_data(input_file, output_file):
#     dataframe = pd.read_excel(input_file, usecols=[1])
#     dataframe["entities"] = dataframe["Text"].apply(extract_entities)
#     dataframe["relationships"] = dataframe["Text"].apply(extract_relationships)
#     dataframe.to_excel(output_file, index=False)


import spacy
import pandas as pd

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract entities
def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

# Function to extract relationships
def extract_relationships(text):
    doc = nlp(text)
    relationships = []
    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "VERB":
                subject = None
                object_ = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = child.text
                    elif child.dep_ in ("dobj", "attr", "prep"):
                        object_ = child.text
                if subject and object_:
                    relationships.append((subject, token.text, object_))
    return relationships

# Main function to process the data
def process_data(input_file, output_file):
    try:
        dataframe = pd.read_excel(input_file, usecols=[1])
        dataframe["Text"] = dataframe["Text"].fillna("")  # Handle missing values
        dataframe["entities"] = dataframe["Text"].apply(extract_entities)
        dataframe["relationships"] = dataframe["Text"].apply(extract_relationships)
        dataframe.to_excel(output_file, index=False)
        print(f"Data successfully processed and saved to {output_file}")
    except Exception as e:
        print(f"Error processing data: {e}")

# Test the functions
if __name__ == "__main__":
    input_file = "sample_input.xlsx"  # Your input file path
    output_file = "output_file.xlsx"  # Your desired output file path
    process_data(input_file, output_file)

