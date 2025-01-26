from collections import Counter

def generate_insights(dataframe):
    # Count entities
    all_entities = [entity for sublist in dataframe["entities"] for entity in sublist]
    entity_counts = Counter(all_entities)

    # Count relationships
    all_relationships = [rel for sublist in dataframe["relationships"] for rel in sublist]
    relationship_counts = Counter(all_relationships)

    return entity_counts, relationship_counts