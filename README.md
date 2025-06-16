#  AI-Enabled Hospital Management System

A full-stack, intelligent hospital management system built using Python (Flask), SQLAlchemy, and integrated with GenAI for patient symptom prediction and interaction. Designed with MVC architecture, the platform handles role-based dashboards for Doctors, Patients, and Admins while incorporating AI-driven disease prediction and natural language chatbot interaction.

---

##  Features

*  **Role-Based Login System** (Admin, Doctor, Patient)
*  **AI-Powered Symptom Chatbot** using GPT-3.5 via OpenRouter
*  **Disease Prediction** using Random Forest ML Classifier
*  **Patient & Appointment Management** with CRUD functionality
*  **Medical Reports & Prescriptions Upload/View**
*  **Session Management** using Flask-Login
*  **Password Security** with Hashing
*  **Responsive UI** with Bootstrap
*  **Built using MVC Architecture & SOLID Principles**

---

##  Technologies Used

| Stack          | Tools/Libraries                           |
| -------------- | ----------------------------------------- |
| Backend        | Python, Flask, Flask-Login, SQLAlchemy    |
| Frontend       | HTML5, CSS3, Bootstrap, Jinja2 Templating |
| Database       | SQLite                                    |
| AI Integration | GPT-3.5 via OpenRouter API, scikit-learn  |
| ML Model       | Random Forest Classifier                  |
| Architecture   | MVC, OOP, SOLID                           |

---

## Folder Structure

```
hospital-management-system/
├── app/
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS, JS, images
│   ├── controllers/                 # Flask routes (views) # GPT-3.5 OpenRouter integration
│   ├── models/                 # SQLAlchemy DB models             
│   ├── __init__.py             # Flask app initialization
│   └── ...
├── requirements.txt
├── README.md
├── run.py                     # App entry point
├── train_model.py             # Random Forest model
└── .gitignore
|__ ....




```
##  Requirements

```txt
Flask
Flask-Login
SQLAlchemy
scikit-learn
requests
openai (or openrouter-compatible wrapper)
pandas
numpy
bootstrap-flask
python-dotenv
```

Install with:

```bash
pip install -r requirements.txt
```

---

##  How to Run

###  Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/hospital-management-system.git
cd hospital-management-system
```

###  Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

###  Step 3: Setup Environment

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
SECRET_KEY=your_flask_secret_key
```

###  Step 4: Run the App

```bash
python run.py
```

Visit: `http://localhost:5000`

---

##  GenAI-Powered Features

###  GPT-3.5 via OpenRouter

* Users can chat with an AI assistant describing their symptoms
* GPT returns related symptoms
* User selects applicable symptoms

###  Random Forest Disease Prediction

* Based on selected symptoms
* Trained on labeled dataset for common diseases
* Output: probable disease name

