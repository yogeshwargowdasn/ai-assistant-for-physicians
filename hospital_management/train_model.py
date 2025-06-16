# train_model.py

import joblib
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

# ✅ Save models in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1️⃣ Expanded real-world training data (symptoms → disease)
samples = [
    (["fever", "cough", "fatigue"], "Influenza"),
    (["headache", "vomiting", "nausea"], "Migraine"),
    (["rash", "fever", "body pain"], "Dengue"),
    (["shortness of breath", "chest pain", "weakness", "arm pain", "Sweating"], "Heart Attack"),
    (["diarrhea", "vomiting", "fever"], "Food Poisoning"),
    (["fever", "nausea", "chills"], "Malaria"),
    (["runny nose", "sore throat", "sneezing"], "Common Cold"),
    (["back pain", "leg pain", "numbness"], "Sciatica"),
    (["fever", "joint pain", "rash"], "Chikungunya"),
    (["itching", "redness", "dry skin"], "Eczema"),
    (["sore throat", "difficulty swallowing"], "Tonsillitis"),
    (["abdominal pain", "bloating", "constipation"], "IBS"),
    (["sensitivity to light", "headache", "blurred vision"], "Cluster Headache"),
    (["weight loss", "night sweats", "persistent cough"], "Tuberculosis"),
    (["anxiety", "insomnia", "palpitations"], "Generalized Anxiety Disorder"),
    (["low mood", "loss of interest", "fatigue"], "Depression"),
    (["itching", "hives", "swelling"], "Allergic Reaction"),
    (["frequent urination", "thirst", "blurred vision"], "Diabetes"),
    (["high blood pressure", "nausea", "nosebleeds"], "Hypertension"),
    (["sensitivity to cold", "weight gain", "dry skin"], "Hypothyroidism"),
    (["irritability", "tremors", "rapid heartbeat"], "Hyperthyroidism"),
    (["cough", "wheezing", "tight chest"], "Asthma"),
    (["sore joints", "morning stiffness", "swelling"], "Rheumatoid Arthritis"),
    (["painful urination", "cloudy urine", "frequent urge to urinate"], "UTI"),
    (["memory loss", "confusion", "mood changes"], "Alzheimer's"),
    (["yellowing skin", "dark urine", "fatigue"], "Hepatitis"),
    (["blurred vision", "eye redness", "light sensitivity"], "Conjunctivitis"),
    (["neck stiffness", "high fever", "sensitivity to light"], "Meningitis"),
    (["sudden severe headache", "loss of balance", "confusion"], "Stroke"),
    (["severe chest pain", "breathlessness", "sweating"], "Pneumothorax"),
    (["pelvic pain", "abnormal discharge", "painful urination"], "PID"),
    (["vomiting", "abdominal cramps", "bloody diarrhea"], "E. coli Infection"),
    (["joint swelling", "morning stiffness", "tenderness"], "Osteoarthritis"),
    (["skin rash", "joint pain", "fatigue"], "Lupus"),
    (["chronic cough", "shortness of breath", "wheezing"], "COPD"),
    (["seizures", "confusion", "staring spells"], "Epilepsy"),
]

# 2️⃣ Prepare features and labels
X_symptoms = [s[0] for s in samples]
y_disease = [s[1] for s in samples]

# 3️⃣ Encode features
mlb = MultiLabelBinarizer()
X_encoded = mlb.fit_transform(X_symptoms)

# 4️⃣ Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_encoded, y_disease)

# 5️⃣ Save model and symptom encoder in the same directory as this script
joblib.dump(clf, os.path.join(BASE_DIR, "disease_model.joblib"))
joblib.dump(mlb, os.path.join(BASE_DIR, "symptom_encoder.joblib"))

# 6️⃣ Save valid symptoms for UI checkboxes
with open(os.path.join(BASE_DIR, "valid_symptoms.json"), "w") as f:
    json.dump(mlb.classes_.tolist(), f, indent=4)

# ✅ Final Console Outputs
print("\n[✔] Model and encoder saved:")
print(f"    → {os.path.join(BASE_DIR, 'disease_model.joblib')}")
print(f"    → {os.path.join(BASE_DIR, 'symptom_encoder.joblib')}")
print("[🧠] Symptoms used for prediction:")
print("     ", mlb.classes_.tolist())
print("[📁] Symptoms list saved to valid_symptoms.json")