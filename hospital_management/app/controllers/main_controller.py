from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, session
import json
from flask_login import current_user, login_required
from app import db
from app.models.prediction_result import PredictionResult




main_bp = Blueprint('main', __name__)

# ------------------------------
# 🔹 Route: AI Tools Overview
# ------------------------------
@main_bp.route('/ai-tools')
def ai_tools_page():
    return render_template('ai_suggestions.html')

# ------------------------------
# 🔹 Route: Symptom Suggest Page
# ------------------------------
@main_bp.route('/symptom-suggest')
def symptom_suggest_page():
    return render_template('symptom_suggest.html')

# ------------------------------
# 🔹 Route: Speech-to-Text Page
# ------------------------------


@main_bp.route('/speech-to-text')
def speech_to_text_page():
    return render_template('speech_to_text.html')



# ------------------------------
# 🔹 Save Symptoms (Optional Manual Entry)
# ------------------------------
@main_bp.route('/save-symptoms', methods=['POST'])
def save_symptoms():
    manual_symptoms = request.form.get('manual_symptoms', '')
    selected_symptoms = request.form.getlist('selected_symptoms')

    # Combine and clean symptoms
    all_symptoms = []
    if manual_symptoms:
        all_symptoms.extend([s.strip().lower() for s in manual_symptoms.split(',') if s.strip()])
    if selected_symptoms:
        all_symptoms.extend([s.strip().lower() for s in selected_symptoms])

    all_symptoms = list(set(all_symptoms))  # remove duplicates

    # ✅ Save to session
    session['submitted_symptoms'] = all_symptoms

    flash("Symptoms submitted successfully!", "success")
    return redirect(url_for('main.symptom_suggest_page'))

# ------------------------------
# 🔹 Legacy Submit Route (Form Submission)
# ------------------------------
@main_bp.route('/submit-symptoms', methods=['POST'])
@login_required
def submit_symptoms():
    selected = request.form.get('finalSymptoms', '')
    symptoms = selected.split(',') if selected else []

    # Ensure submitted_symptoms is a dict
    if not isinstance(session.get('submitted_symptoms'), dict):
        session['submitted_symptoms'] = {}

    user_id = str(current_user.id)
    existing = session['submitted_symptoms'].get(user_id, [])
    combined = list(set(existing + symptoms))

    session['submitted_symptoms'][user_id] = combined

    flash("Symptoms submitted: " + ", ".join(symptoms), "success")
    return redirect(url_for('main.symptom_suggest_page'))


# ------------------------------
# 🔹 Predict Disease Page
# ------------------------------
@main_bp.route('/predict-disease', methods=['GET'])
@login_required
def predict_disease_page():
    default_symptoms = [
        "fever", "cough", "headache", "nausea", "vomiting", "fatigue", "chest pain",
        "rash", "sore throat", "body pain", "diarrhea", "shortness of breath", "dizziness"
    ]

    submitted_dict = session.get('submitted_symptoms')
    user_symptoms = []

    if isinstance(submitted_dict, dict):
        user_symptoms = submitted_dict.get(str(current_user.id), [])

    all_symptoms = sorted(set(default_symptoms + user_symptoms))

    return render_template("symptom_predict.html", symptoms=all_symptoms)



# @main_bp.route('/predict-disease', methods=['GET'])
# def predict_disease_page():
#     default_symptoms = [
#         "fever", "cough", "headache", "nausea", "vomiting", "fatigue", "chest pain",
#         "rash", "sore throat", "body pain", "diarrhea", "shortness of breath", "dizziness"
#     ]
#     saved_symptoms = session.get('submitted_symptoms', [])
#     combined_symptoms = list(set(default_symptoms + saved_symptoms))
#     return render_template("symptom_predict.html", symptoms=combined_symptoms, saved_symptoms=saved_symptoms)



# -----------------------------------------------------
# 🧠 Unified Endpoint: Predict Disease (Rule-Based)
# -----------------------------------------------------
@main_bp.route('/ai/predict-disease', methods=['POST'])
@login_required
def predict_disease_api():
    # Accept JSON or form-encoded data
    if request.is_json:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
    else:
        raw = request.form.get('symptoms', '')
        try:
            symptoms = json.loads(raw) if raw else []
        except Exception:
            return jsonify({"error": "Invalid symptom format"}), 400

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    print("Symptoms received for prediction:", symptoms)

    # 🧠 Rule-Based Disease Prediction
    disease_map = {
        "fever": ["Flu", "Dengue", "Malaria"],
        "cough": ["Common Cold", "Bronchitis", "COVID-19"],
        "headache": ["Migraine", "Tension headache", "Flu"],
        "rash": ["Allergy", "Chickenpox", "Measles"],
        "nausea": ["Food Poisoning", "Gastritis"],
        "fatigue": ["Anemia", "Hypothyroidism"],
        "chest pain": ["Heart Attack", "Angina"],
        "diarrhea": ["Food Poisoning", "Cholera"]
    }

    predicted_diseases = set()
    for symptom in symptoms:
        predicted_diseases.update(disease_map.get(symptom.lower(), []))

    disease = sorted(predicted_diseases)[0] if predicted_diseases else None

    # 🧪 Suggested Tests
    lab_tests_map = {
        "Flu": ["CBC", "Influenza Test"],
        "Dengue": ["Dengue NS1 Antigen", "CBC"],
        "Malaria": ["Peripheral Blood Smear", "Rapid Diagnostic Test"],
        "Common Cold": [],
        "Bronchitis": ["Chest X-Ray"],
        "COVID-19": ["RT-PCR", "Antigen Test"],
        "Migraine": [],
        "Tension headache": [],
        "Allergy": ["Allergy Test"],
        "Chickenpox": ["Varicella-Zoster Virus Test"],
        "Measles": ["Measles Antibody Test"],
        "Food Poisoning": ["Stool Culture"],
        "Gastritis": ["Endoscopy"],
        "Anemia": ["CBC", "Iron Studies"],
        "Hypothyroidism": ["TSH Test"],
        "Heart Attack": ["ECG", "Troponin Test"],
        "Angina": ["ECG", "Stress Test"],
        "Cholera": ["Stool Test"]
    }

    tests = lab_tests_map.get(disease, []) if disease else []

    # ✅ Save result to DB
    new_result = PredictionResult(
        user_id=current_user.id,
        symptoms=",".join(symptoms),
        disease=disease,
        tests=",".join(tests)
    )
    db.session.add(new_result)
    db.session.commit()

    # Return as JSON or render UI
    if request.is_json:
        return jsonify({"disease": disease, "tests": tests})

    return render_template("symptom_suggest.html", disease=disease, tests=tests)