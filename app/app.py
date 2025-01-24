from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Serve the main HTML file
@app.route('/')
def home():
    return render_template('home.html')

# API endpoint to process data
@app.route('/api/process', methods=['POST'])
def process_data():
    data = request.json  # Receive JSON data from Vue.js
    input_text = data.get('text', '')
    # Process the input (this is where your NLP or other logic would go)
    response = {
        "message": "Processed successfully",
        "received_text": input_text
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
