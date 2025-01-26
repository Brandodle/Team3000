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
    dataframe = pd.read_excel(input_file, usecols=[1])
    dataframe["entities"] = dataframe["Text"].apply(extract_entities)
    dataframe["relationships"] = dataframe["Text"].apply(extract_relationships)
    dataframe.to_excel(output_file, index=False)