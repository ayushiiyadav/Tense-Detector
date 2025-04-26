from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)
CORS(app, resources={r"/detect-tense": {"origins": "http://127.0.0.1:5500"}})  # Enable CORS for the specified origin


def detect_tense(text):
    # Process text using spaCy
    doc = nlp(text)
    
    # Store tense information
    tenses = {"present": 0, "past": 0, "future": 0}
    
    # Flags to detect future and continuous aspects
    has_future_modal = False
    has_base_or_gerund_after_modal = False
    
    for i, token in enumerate(doc):
        if token.pos_ == "VERB" or token.pos_ == "AUX":  # Check for both verbs and auxiliary verbs
            if token.tag_ in ["VBP", "VBZ", "VBG"]:  # Present tense (including continuous forms)
                tenses["present"] += 1
            elif token.tag_ in ["VBD", "VBN"]:  # Past tense (simple past and past participle)
                tenses["past"] += 1
            elif token.tag_ == "MD":  # Modal verbs like 'will' or 'shall'
                if token.text.lower() in ["will", "shall"]:
                    has_future_modal = True
                    # Look ahead to check if a base form or gerund follows
                    if i + 1 < len(doc):
                        next_token = doc[i + 1]
                        if next_token.tag_ in ["VB", "VBG"]:  # Base form or gerund
                            has_base_or_gerund_after_modal = True
            # Check for other future markers
            elif token.text.lower() in ["is", "are", "am"] and i + 1 < len(doc) and doc[i + 1].text.lower() in ["going"]:
                if i + 2 < len(doc) and doc[i + 2].tag_ in ["VB", "VBG"]:
                    tenses["future"] += 1
                
    if has_future_modal and has_base_or_gerund_after_modal:
        tenses["future"] += 1

    # Determine the majority tense
    detected_tense = max(tenses, key=tenses.get)
    
    return detected_tense
@app.route('/detect-tense', methods=['POST'])
def detect_tense_api():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    tense = detect_tense(text)
    return jsonify({"tense": tense})

if __name__ == '__main__':
    app.run(debug=True)
