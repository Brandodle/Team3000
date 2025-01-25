from flask import Flask, request, jsonify, render_template
import pandas as pd
import spacy
import os
from collections import Counter

app = Flask(__name__, template_folder='templates', static_folder='static')
nlp = spacy.load("en_core_web_sm")  # Load SpaCy's pre-trained model

# Configure upload folder
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if file:
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return process_excel(file_path)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def process_excel(file_path):
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)
        
        # Combine all rows into a single text string
        text = ' '.join(df.astype(str).fillna('').apply(lambda x: ' '.join(x), axis=1))
        nlp.max_length = max(len(text), 1500000)  # Adjust SpaCy max_length to avoid exceeding limits

        # Perform NLP processing
        doc = nlp(text)

        # Extract entities
        entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

        # Extract relationships (e.g., subject-action-object)
        relationships = [
            {'subject': token.head.text, 'action': token.dep_, 'object': token.text}
            for token in doc
            if token.dep_ in ('nsubj', 'dobj')
        ]

        return jsonify({'entities': entities, 'relationships': relationships, 'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/insights', methods=['POST'])
def generate_insights():
    try:
        # Extract the text sent by the frontend
        text = request.json.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided for insights'}), 400

        doc = nlp(text)

        # Count entity types
        entity_counter = Counter([ent.label_ for ent in doc.ents])
        most_frequent_entity = entity_counter.most_common(1)[0] if entity_counter else ("None", 0)

        # Summarize relationships
        relationships = [
            {'subject': token.head.text, 'action': token.dep_, 'object': token.text}
            for token in doc
            if token.dep_ in ('nsubj', 'dobj')
        ]
        relationship_summary = Counter([f"{rel['subject']} -> {rel['action']} -> {rel['object']}" for rel in relationships])

        # Prepare insights
        insights = {
            'most_frequent_entity': most_frequent_entity,
            'entity_summary': dict(entity_counter),
            'relationship_summary': dict(relationship_summary.most_common(5))
        }

        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/network-data', methods=['POST'])
def network_data():
    try:
        text = request.json.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided for network data'}), 400

        doc = nlp(text)

        # Generate nodes and edges for network visualization
        nodes = []
        edges = []
        entity_set = set()

        for ent in doc.ents:
            if ent.text not in entity_set:
                nodes.append({'id': ent.text, 'label': ent.text, 'group': ent.label_})
                entity_set.add(ent.text)

        for token in doc:
            if token.dep_ in ('nsubj', 'dobj'):
                edges.append({'from': token.head.text, 'to': token.text, 'label': token.dep_})

        return jsonify({'nodes': nodes, 'edges': edges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
