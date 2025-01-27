# topic_modeling.py

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import plotly.express as px

def perform_lda_topic_modeling(df, num_topics=5):
    """
    Perform Latent Dirichlet Allocation (LDA) topic modeling on the text data.

    Parameters:
    - df (pd.DataFrame): The dataframe with a 'Text' column.
    - num_topics (int): Number of topics to extract.

    Returns:
    - topics: The topics extracted by LDA.
    - lda_model: The fitted LDA model.
    - vectorizer: The CountVectorizer used to convert the text into vectors.
    """
    # Convert the text data into a format suitable for LDA (e.g., Bag of Words)
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df['Text'])

    # Perform LDA
    lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda_model.fit(X)

    # Extract topics and their top words
    topics = []
    feature_names = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(lda_model.components_):
        top_words_idx = topic.argsort()[:-11:-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append((f"Topic {topic_idx+1}", top_words))

    return topics, lda_model, vectorizer

def plot_lda_topics(lda_model, vectorizer, num_topics=5):
    """
    Visualize the topics from the LDA model using a bar chart.
    """
    feature_names = vectorizer.get_feature_names_out()
    topic_word_matrix = lda_model.components_

    topic_words = []
    for i, topic in enumerate(topic_word_matrix):
        top_words_idx = topic.argsort()[:-11:-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topic_words.append(top_words)

    # Create a flat list of words with their corresponding topic index
    words = []
    for i, top_words in enumerate(topic_words):
        for word in top_words:
            words.append((i+1, word))

    # Create a DataFrame for visualization
    words_df = pd.DataFrame(words, columns=["Topic", "Word"])

    # Plot the data using Plotly
    fig = px.bar(words_df, x="Word", color="Topic", title="Top Words per Topic", labels={"Word": "Words"})
    fig.update_layout(xaxis_tickangle=-45)

    return fig
