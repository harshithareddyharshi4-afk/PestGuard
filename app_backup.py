# -*- coding: utf-8 -*-

from flask import Flask, request
import joblib
import requests
import pandas as pd

app = Flask(__name__)

# Load the two trained models
risk_model = joblib.load("risk_model.pkl")
pest_model = joblib.load("pest_model.pkl")

risk_history = []


@app.route("/", methods=["GET", "POST"])
def home():

    temperature = "--"
    humidity = "--"
    rainfall = "--"

    risk = "Waiting for analysis"
    confidence = "--"
    pest = "--"
    warning = ""
    advice = ""

    if request.method == "POST":

        try:
            latitude = float(request.form["latitude"])
            longitude = float(request.form["longitude"])

            # Get weather from Open-Meteo
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={latitude}"
                f"&longitude={longitude}"
                f"&current=temperature_2m,relative_humidity_2m,rain"
            )

            response = requests.get(url, timeout=10)
            weather = response.json()["current"]

            temperature = round(float(weather["temperature_2m"]), 1)
            humidity = round(float(weather["relative_humidity_2m"]), 1)
            rainfall = round(float(weather["rain"]), 1)

            # Prepare model input
            inputs = pd.DataFrame([{
                "temperature": temperature,
                "humidity": humidity,
                "rainfall": rainfall
            }])

            # --------------------------------
            # STEP 1: Predict RISK
            # --------------------------------

            risk = risk_model.predict(inputs)[0]

            probabilities = risk_model.predict_proba(inputs)[0]

            confidence = round(
                max(probabilities) * 100,
                1
            )

            # --------------------------------
            # STEP 2: Predict PEST only when
            # risk is MEDIUM or HIGH
            # --------------------------------

            if risk == "LOW":

                pest = "No specific pest indicated"

                warning = (
                    "ALERT: Current paddy pest risk is low."
                )

                advice = (
                    "Continue normal paddy crop monitoring. "
                    "Check the plants regularly."
                )

            elif risk == "MEDIUM":

                pest = pest_model.predict(inputs)[0]

                warning = (
                    "ALERT: Current paddy pest risk is medium."
                )

                advice = (
                    "Monitor the paddy field closely "
                    "for pest activity."
                )

            elif risk == "HIGH":

                pest = pest_model.predict(inputs)[0]

                warning = (
                    "ALERT: Current paddy pest risk is high."
                )

                advice = (
                    "Take immediate field monitoring "
                    "and pest management action."
                )

            risk_history.append(risk)

            if len(risk_history) > 10:
                risk_history.pop(0)

        except Exception as e:

            risk = "Analysis Error"
            confidence = "--"
            pest = "--"
            warning = str(e)
            advice = ""

    # Risk display style
    if risk == "LOW":
        risk_class = "low"
    elif risk == "MEDIUM":
        risk_class = "medium"
    elif risk == "HIGH":
        risk_class = "high"
    else:
        risk_class = "error"

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>PestGuard</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f4f7f5;
    margin: 0;
    padding: 20px;
}}

.container {{
    max-width: 900px;
    margin: auto;
}}

.card {{
    background: white;
    padding: 22px;
    margin: 18px 0;
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}}

h1 {{
    margin-bottom: 5px;
}}

.risk {{
    font-size: 32px;
    font-weight: bold;
    margin: 15px 0;
}}

.low {{
    color: green;
}}

.medium {{
    color: orange;
}}

.high {{
    color: red;
}}

.error {{
    color: red;
}}

.conditions {{
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}}

.condition {{
    flex: 1;
    min-width: 180px;
    background: #f5f5f5;
    padding: 18px;
    border-radius: 10px;
}}

.value {{
    font-size: 25px;
    font-weight: bold;
}}

button {{
    padding: 12px 18px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
}}

.footer {{
    text-align: center;
    margin-top: 30px;
    color: #666;
}}

</style>

</head>


<body>

<div class="container">

<h1>🌾 PestGuard</h1>

<p>
AI-Based Paddy Pest Outbreak Early Warning System
</p>


<div class="card">

<h2>🌾 Paddy Crop Monitoring</h2>

<button onclick="getLocation()">
📍 Use My Location
</button>

<form method="POST" id="locationForm">

<input
type="hidden"
name="latitude"
id="latitude"
>

<input
type="hidden"
name="longitude"
id="longitude"
>

</form>

</div>


<div class="card">

<h2>🚦 Current Paddy Pest Risk</h2>

<div class="risk {risk_class}">
{risk}
</div>

<p>
{warning}
</p>

<p>
🤖 Model Confidence:
<strong>{confidence}%</strong>
</p>

</div>


<div class="card">

<h2>🌾 Field Name: paddy field</h2>

<h3>
Likely Pest: {pest}
</h3>

</div>


<div class="card">

<h2>📋 Current Conditions</h2>

<div class="conditions">

<div class="condition">

🌡️

<p>Temperature (°C)</p>

<div class="value">
{temperature}
</div>

</div>


<div class="condition">

💧

<p>Humidity (%)</p>

<div class="value">
{humidity}
</div>

</div>


<div class="condition">

🌧️

<p>Rainfall (mm)</p>

<div class="value">
{rainfall}
</div>

</div>

</div>

</div>


<div class="card">

<h2>👨‍🌾 Paddy Farmer Guidance</h2>

<p>
{advice}
</p>

</div>


<div class="card">

<h2>📊 Paddy Pest Risk History</h2>

<p>
Recent prediction levels
</p>

<p>
{" → ".join(risk_history)}
</p>

</div>


<div class="footer">

PestGuard • AI Paddy Agriculture Early Warning Prototype

</div>

</div>


<script>

function getLocation() {{

    if (!navigator.geolocation) {{

        alert("Geolocation is not supported.");

        return;
    }}

    navigator.geolocation.getCurrentPosition(

        function(position) {{

            document.getElementById("latitude").value =
                position.coords.latitude;

            document.getElementById("longitude").value =
                position.coords.longitude;

            document.getElementById("locationForm").submit();

        }},

        function(error) {{

            alert(
                "Please allow location access."
            );

        }}

    );

}}

</script>

</body>

</html>
"""


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )