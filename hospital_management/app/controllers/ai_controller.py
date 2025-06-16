import os
import json
import requests
import wave
import joblib
import numpy as np

from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename
from vosk import Model, KaldiRecognizer

ai_bp = Blueprint('ai', __name__)

# -------------------------------
# ✅ Load Vosk speech model safely
# -------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
vosk_model_path = os.path.join(base_dir, "..", "..", "vosk-model-small-en-us-0.15")

if not os.path.exists(vosk_model_path):
    print(f"[ERROR] Vosk model not found at: {vosk_model_path}")
    model = None
else:
    model = Model(vosk_model_path)
    print(f"[INFO] Vosk model loaded from: {vosk_model_path}")

# 🔐 OpenRouter GPT-3.5 API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --------------------------------
# 1️⃣ Speech-to-Text Endpoint (Vosk)
# --------------------------------
@ai_bp.route('/ai/speech-to-text', methods=['POST'])
def speech_to_text():
    if model is None:
        return jsonify({"error": "Speech model not loaded"}), 500

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    filename = secure_filename(audio_file.filename)
    filepath = os.path.join("/tmp", filename)
    audio_file.save(filepath)

    wf = wave.open(filepath, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return jsonify({"error": "Audio must be mono WAV format (PCM)"}), 400

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            results.append(result.get("text", ""))
    final_result = json.loads(rec.FinalResult())
    results.append(final_result.get("text", ""))

    transcript = " ".join(results).strip().lower()

    return jsonify({"transcript": transcript})


# --------------------------------
# 2️⃣ Symptom Suggestion via GPT-3.5
# --------------------------------
def suggest_symptoms_from_llm(input_text):
    if not OPENROUTER_API_KEY:
        return ["Missing OpenRouter API key"]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Hospital-AI-Assistant"
    }

    prompt = (
        "You are a smart medical assistant.\n"
        f"A patient is having these symptoms \"{input_text}\" what are other possible symptoms he have: \n\n"
        "List 5 unique possible medical symptoms they might be referring to, one per line."
    )

    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code != 200:
            return [f"OpenRouter Error: {response.status_code}"]

        content = response.json()["choices"][0]["message"]["content"]
        
        import re
        # Strip numbers, bullets, quotes, and extra punctuation from beginning
        suggestions = [
            re.sub(r"^\W*\d*\W*", "", line.strip().lower()) for line in content.split("\n") if line.strip()
        ]
        return suggestions if suggestions else ["No symptoms identified"]
        return suggestions if suggestions else ["No symptoms identified"]

    except Exception as e:
        return [f"Error parsing LLM output: {str(e)}"]


# --------------------------------
# 3️⃣ Symptom Suggestion Endpoint
# --------------------------------
@ai_bp.route('/ai/symptom-suggest', methods=['POST'])
def symptom_suggest():
    data = request.get_json()
    input_text = data.get("input_text", "")

    if not input_text:
        return jsonify({"error": "input_text is required"}), 400

    related = suggest_symptoms_from_llm(input_text)
    return jsonify({
        "input_text": input_text,
        "related_symptoms": related
    })


# --------------------------------------------
# 4️⃣ Disease & Lab Test Prediction (ML Model)
# --------------------------------------------
ml_model_path = os.path.join(base_dir, "..", "..", "disease_model.joblib")
encoder_path = os.path.join(base_dir, "..", "..", "symptom_encoder.joblib")

ml_model = joblib.load(ml_model_path) if os.path.exists(ml_model_path) else None
symptom_encoder = joblib.load(encoder_path) if os.path.exists(encoder_path) else None

@ai_bp.route('/ai/predict-disease', methods=['POST'])
def predict_disease():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    print("[🩺] Received symptoms from frontend:", symptoms)

    if not ml_model or not symptom_encoder:
        print("[❌] ML model or encoder not loaded")
        return jsonify({"error": "ML model or encoder not loaded"}), 500

    if not symptoms or not isinstance(symptoms, list):
        return jsonify({"error": "No symptoms provided or invalid format"}), 400

    try:
        valid_symptoms = symptom_encoder.classes_.tolist()
        cleaned = [s for s in symptoms if s in valid_symptoms]
        print("[✅] Cleaned valid symptoms:", cleaned)

        if not cleaned:
            return jsonify({"error": "No valid symptoms found. Valid symptoms are: " + ', '.join(valid_symptoms)}), 400

        encoded = symptom_encoder.transform([cleaned])
        prediction = ml_model.predict(encoded)[0]
        disease = prediction
        tests = get_tests_for_disease(disease)

        save_prediction_history(cleaned, disease, tests)

        return jsonify({
            "disease": disease,
            "tests": tests
        })

    except Exception as e:
        print("[⚠️] Prediction Error:", str(e))
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


# --------------------------------------------
# 🧪 Map Diseases to Recommended Lab Tests
# --------------------------------------------
def get_tests_for_disease(disease):
    mapping = {
        "influenza": ["CBC", "Influenza Test", "Chest X-Ray"],
        "migraine": ["CT Scan", "MRI", "Neurological Exam"],
        "dengue": ["Dengue NS1 Antigen", "Platelet Count", "CBC"],
        "heart attack": ["ECG", "Troponin Test", "Chest X-ray"],
        "food poisoning": ["Stool Culture", "Electrolyte Test"],
        "malaria": ["Blood Smear", "Rapid Diagnostic Test"],
        "common cold": ["Physical Exam", "CBC"],
        "sciatica": ["X-ray", "MRI", "Nerve Conduction Study"],
        "chikungunya": ["ELISA", "CBC", "Liver Function Test"]
    }
    return mapping.get(disease.lower(), ["Consult General Physician"])


# --------------------------------------------
# 💾 Save Prediction History to JSON
# --------------------------------------------
def save_prediction_history(symptoms, disease, tests):
    history_file = os.path.join(base_dir, "..", "..", "prediction_history.json")
    try:
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append({
            "symptoms": symptoms,
            "disease": disease,
            "tests": tests
        })

        with open(history_file, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print("[ERROR] Failed to save prediction history:", str(e))


# --------------------------------------------
# 📊 Get Prediction History Endpoint
# --------------------------------------------
@ai_bp.route('/ai/prediction-history', methods=['GET'])
def prediction_history():
    history_file = os.path.join(base_dir, "..", "..", "prediction_history.json")
    if not os.path.exists(history_file):
        return jsonify([])

    with open(history_file, "r") as f:
        data = json.load(f)
    return jsonify(data)


# --------------------------------------------
# 📥 Export History as CSV Endpoint
# --------------------------------------------
@ai_bp.route('/ai/export-history', methods=['GET'])
def export_prediction_history():
    history_file = os.path.join(base_dir, "..", "..", "prediction_history.json")
    if not os.path.exists(history_file):
        return jsonify({"error": "No history found"}), 404

    with open(history_file, 'r') as f:
        data = json.load(f)

    def generate_csv():
        output = "symptoms,disease,tests\n"
        for record in data:
            output += f"{';'.join(record['symptoms'])},{record['disease']},{';'.join(record['tests'])}\n"
        return output

    return Response(
        generate_csv(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=prediction_history.csv"}
    )
