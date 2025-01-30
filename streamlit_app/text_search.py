import spacy
import re
import streamlit as st

# Load the SpaCy NLP model (load once globally)
nlp = spacy.load("en_core_web_sm")

# Function to extract and highlight entities
def highlight_entities(text):
    """
    Extracts entities from text and highlights them using HTML span tags.
    """
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Sort entities by length (longer first) to avoid nested replacements
    highlighted_text = text
    for entity, label in sorted(entities, key=lambda x: len(x[0]), reverse=True):
        highlighted_text = re.sub(
            rf"\b{re.escape(entity)}\b",
            f"<span class='highlight {label.lower()}'>{entity}</span>",
            highlighted_text,
            flags=re.IGNORECASE
        )

    return highlighted_text, entities

