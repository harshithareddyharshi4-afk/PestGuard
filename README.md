# 🌾 PestGuard – AI-Based Paddy Pest Risk Prediction System

PestGuard is an AI-based web application designed to help identify potential pest risks in paddy crops using weather conditions and location information.

## 🎯 Problem

Paddy farmers may face pest attacks when environmental conditions become suitable for pests. Early awareness of pest risk can help farmers monitor their crops and take timely action.

## 💡 Solution

PestGuard analyzes environmental conditions such as:

* 🌡️ Temperature
* 💧 Humidity
* 🌧️ Rainfall
* 📍 Location

The system uses machine learning models to predict:

* Pest risk level
* Likely paddy pest
* Basic farming guidance

## 🤖 AI Features

PestGuard currently supports three risk levels:

* 🟢 LOW
* 🟡 MEDIUM
* 🔴 HIGH

For medium and high risk conditions, the system can identify a likely pest such as:

* Brown Planthopper
* Leaf Folder
* Stem Borer

## 🌦️ Live Weather & Location

The application uses:

* Open-Meteo for live weather information
* Browser location services for the user's location
* Reverse geocoding to display the location name

## 👨‍🌾 Farming Guidance

Based on the predicted risk, PestGuard provides simple guidance to help farmers monitor their paddy crop.

## 🛠️ Technologies Used

* Python
* Flask
* Scikit-learn
* Pandas
* Joblib
* HTML
* CSS
* JavaScript
* Open-Meteo API
* BigDataCloud Reverse Geocoding API
* Git & GitHub

## 📁 Project Structure

```text
PestGuard/
│
├── app.py
├── app_backup.py
├── pest_data.csv
├── pest_model.pkl
├── risk_model.pkl
├── train_model.py
├── .gitignore
└── README.md
```

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/harshithareddyharshi4-afk/PestGuard.git
```

### 2. Open the project folder

```bash
cd PestGuard
```

### 3. Install the required Python packages

```bash
pip install flask pandas scikit-learn joblib requests python-dotenv
```

### 4. Start PestGuard

```bash
python app.py
```

### 5. Open the application

Open a browser and visit:

```text
http://127.0.0.1:5000
```

## ⚠️ Current Prototype Status

PestGuard is currently a working prototype.

The machine learning models were trained using a small demonstration dataset. Further development will include larger real-world paddy field datasets and additional validation before using the system for real agricultural decision-making.

## 🚀 Future Scope

* 📱 Android mobile application
* 🌾 Larger real-world paddy datasets
* 🤖 Improved machine learning models
* 📸 Paddy leaf/image-based pest detection
* 🔔 Pest-risk alerts
* 🗺️ Field monitoring
* 🌐 Support for more regions and languages

## 👩‍💻 Project

**PestGuard – AI-Based Paddy Pest Risk Prediction System**

Built as an AI-based agricultural technology project focused on early pest-risk awareness for paddy crops.
