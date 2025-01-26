import matplotlib.pyplot as plt
import networkx as nx

def visualize_entities(entity_counts):
    # Bar chart for top entities
    top_entities = entity_counts.most_common(10)
    entities, counts = zip(*top_entities)
    plt.bar(entities, counts)
    plt.xticks(rotation=45)
    plt.xlabel("Entities")
    plt.ylabel("Frequency")
    plt.title("Top 10 Entities")
    plt.show()

def visualize_relationships(all_relationships):
    # Network graph for relationships
    G = nx.Graph()
    for relationship in all_relationships:
        if isinstance(relationship, tuple) and len(relationship) == 3:
            G.add_edge(relationship[0], relationship[2], label=relationship[1])
        else:
            print(f"Skipping invalid relationship: {relationship}")
    nx.draw(G, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold")
    plt.show()