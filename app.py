from flask import Flask, render_template_string, request
import joblib
import pandas as pd
import requests

app = Flask(__name__)

# Load trained AI models
risk_model = joblib.load("risk_model.pkl")
pest_model = joblib.load("pest_model.pkl")

# Store recent predictions
history = []


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,rain",
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    current = data["current"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    rainfall = current["rain"]

    return temperature, humidity, rainfall


def get_location_name(latitude, longitude):
    try:
        url = (
            "https://api.bigdatacloud.net/data/"
            "reverse-geocode-client"
        )

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "localityLanguage": "en"
        }

        headers = {
            "User-Agent": "PestGuard-Paddy-Project"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        city = (
            data.get("city")
            or data.get("locality")
            or data.get("principalSubdivision")
            or "Unknown location"
        )

        state = data.get("principalSubdivision", "")
        country = data.get("countryName", "")

        if city and state and city != state:
            if country:
                return f"{city}, {state}, {country}"
            return f"{city}, {state}"

        if city:
            return city

        return "Location detected"

    except Exception as error:
        print("Location name error:", error)
        return "Location detected"


def get_guidance(risk, pest):
    if risk == "HIGH":
        if pest == "Brown Planthopper":
            return (
                "Inspect the lower parts of paddy plants regularly. "
                "Avoid excessive nitrogen fertilizer and monitor for "
                "hopper populations."
            )

        if pest == "Stem Borer":
            return (
                "Check plants for dead hearts and stem damage. "
                "Remove heavily affected plants and monitor the field closely."
            )

        if pest == "Leaf Folder":
            return (
                "Check folded leaves and damaged leaf areas. "
                "Maintain regular field monitoring."
            )

        return (
            "High pest risk detected. Inspect the crop carefully "
            "and take appropriate agricultural action."
        )

    if risk == "MEDIUM":
        return (
            "Moderate pest risk detected. Monitor the paddy field "
            "regularly and check leaves and stems for early pest signs."
        )

    return (
        "Continue normal paddy crop monitoring. "
        "Check the plants regularly."
    )


@app.route("/", methods=["GET", "POST"])
def home():

    temperature = None
    humidity = None
    rainfall = None
    risk = None
    confidence = None
    pest = None
    guidance = None
    location = None
    error = None

    if request.method == "POST":

        try:
            latitude = float(request.form["latitude"])
            longitude = float(request.form["longitude"])

            # Get live weather
            temperature, humidity, rainfall = get_weather(
                latitude,
                longitude
            )

            # Get location name
            location = get_location_name(
                latitude,
                longitude
            )

            # Prepare AI input
            features = pd.DataFrame(
                [[temperature, humidity, rainfall]],
                columns=[
                    "temperature",
                    "humidity",
                    "rainfall"
                ]
            )

            # Predict pest risk
            risk_prediction = risk_model.predict(features)[0]
            risk = str(risk_prediction)

            # AI confidence
            probabilities = risk_model.predict_proba(features)[0]
            confidence = round(max(probabilities) * 100, 1)

            # Predict pest only for medium/high risk
            if risk in ["MEDIUM", "HIGH"]:
                pest = str(pest_model.predict(features)[0])
            else:
                pest = "No specific pest indicated"

            # Farming guidance
            guidance = get_guidance(risk, pest)

            # Save history
            history.append(risk)

            if len(history) > 10:
                history.pop(0)

        except Exception as error_message:
            error = str(error_message)

    return render_template_string(
        HTML,
        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall,
        risk=risk,
        confidence=confidence,
        pest=pest,
        guidance=guidance,
        location=location,
        history=history,
        error=error
    )


HTML = """
<!DOCTYPE html>
<html>
<head>

    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>PestGuard - Paddy Protection</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f8f1;
            color: #18351d;
        }

        .header {
            background: linear-gradient(
                135deg,
                #1b5e20,
                #43a047
            );
            color: white;
            padding: 28px 20px;
            text-align: center;
            box-shadow: 0 3px 12px rgba(0,0,0,0.15);
        }

        .header h1 {
            margin: 0;
            font-size: 34px;
        }

        .header p {
            margin: 8px 0 0;
            font-size: 16px;
            opacity: 0.95;
        }

        .container {
            width: 92%;
            max-width: 1000px;
            margin: 25px auto;
        }

        .card {
            background: white;
            border-radius: 18px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        }

        .card h2 {
            margin-top: 0;
            font-size: 22px;
        }

        .location {
            background: #e8f5e9;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 18px;
            font-size: 16px;
        }

        .weather-grid {
            display: grid;
            grid-template-columns:
                repeat(3, 1fr);
            gap: 15px;
        }

        .weather-box {
            background: #f7faf6;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid #e1eadf;
        }

        .weather-icon {
            font-size: 30px;
        }

        .weather-value {
            font-size: 24px;
            font-weight: bold;
            margin-top: 8px;
        }

        .weather-label {
            color: #5d6d60;
            margin-top: 5px;
        }

        .button-area {
            text-align: center;
            margin: 25px 0;
        }

        button {
            background: #2e7d32;
            color: white;
            border: none;
            border-radius: 14px;
            padding: 16px 28px;
            font-size: 17px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }

        button:hover {
            background: #1b5e20;
        }

        .risk-box {
            text-align: center;
            padding: 25px;
            border-radius: 16px;
            background: #f7faf6;
        }

        .risk-value {
            font-size: 42px;
            font-weight: bold;
            margin: 10px;
        }

        .confidence {
            font-size: 17px;
            color: #526156;
        }

        .pest {
            margin-top: 18px;
            font-size: 19px;
            font-weight: bold;
        }

        .guidance {
            background: #fff8e1;
            border-left: 6px solid #f9a825;
            padding: 18px;
            border-radius: 10px;
            line-height: 1.6;
        }

        .history-list {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .history-item {
            padding: 10px 14px;
            border-radius: 10px;
            background: #e8f5e9;
            font-weight: bold;
        }

        .error {
            background: #ffebee;
            color: #b71c1c;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .footer {
            text-align: center;
            padding: 25px;
            color: #607064;
            font-size: 14px;
        }

        @media (max-width: 650px) {

            .header h1 {
                font-size: 27px;
            }

            .weather-grid {
                grid-template-columns: 1fr;
            }

            .container {
                width: 94%;
            }

            button {
                width: 100%;
            }

            .risk-value {
                font-size: 36px;
            }
        }

    </style>

</head>

<body>

    <div class="header">

        <h1>🌾 PestGuard</h1>

        <p>
            AI-Based Paddy Pest Risk Prediction System
        </p>

    </div>


    <div class="container">

        {% if error %}

        <div class="error">
            ⚠️ {{ error }}
        </div>

        {% endif %}


        <div class="card">

            <h2>📍 Paddy Field Weather</h2>

            {% if location %}

            <div class="location">
                📍 <strong>Your Location:</strong>
                {{ location }}
            </div>

            {% endif %}


            {% if temperature is not none %}

            <div class="weather-grid">

                <div class="weather-box">

                    <div class="weather-icon">
                        🌡️
                    </div>

                    <div class="weather-value">
                        {{ temperature }} °C
                    </div>

                    <div class="weather-label">
                        Temperature
                    </div>

                </div>


                <div class="weather-box">

                    <div class="weather-icon">
                        💧
                    </div>

                    <div class="weather-value">
                        {{ humidity }} %
                    </div>

                    <div class="weather-label">
                        Humidity
                    </div>

                </div>


                <div class="weather-box">

                    <div class="weather-icon">
                        🌧️
                    </div>

                    <div class="weather-value">
                        {{ rainfall }} mm
                    </div>

                    <div class="weather-label">
                        Rainfall
                    </div>

                </div>

            </div>

            {% else %}

            <p>
                Click the button below to get live weather
                information for your paddy field.
            </p>

            {% endif %}

        </div>


        <div class="card">

            <h2>🤖 AI Paddy Risk Analysis</h2>

            {% if risk %}

            <div class="risk-box">

                <div>
                    Current Paddy Pest Risk
                </div>

                <div class="risk-value">
                    {{ risk }}
                </div>

                <div class="confidence">
                    AI Confidence: {{ confidence }}%
                </div>

                <div class="pest">
                    🐛 Likely Pest:
                    {{ pest }}
                </div>

            </div>

            {% else %}

            <p>
                AI analysis will appear after checking
                your current field conditions.
            </p>

            {% endif %}

        </div>


        <div class="button-area">

            <form method="POST" id="riskForm">

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

                <button type="button"
                        onclick="getLocation()">

                    🌦️ Check My Paddy Field Risk

                </button>

            </form>

        </div>


        {% if guidance %}

        <div class="card">

            <h2>💡 Farming Guidance</h2>

            <div class="guidance">
                {{ guidance }}
            </div>

        </div>

        {% endif %}


        {% if history %}

        <div class="card">

            <h2>📊 Risk History</h2>

            <p>
                Recent AI predictions:
            </p>

            <div class="history-list">

                {% for item in history %}

                <div class="history-item">
                    {{ item }}
                </div>

                {% endfor %}

            </div>

        </div>

        {% endif %}

    </div>


    <div class="footer">

        PestGuard 🌾 |
        AI-based Paddy Crop Protection

    </div>


<script>

function getLocation() {

    if (!navigator.geolocation) {

        alert(
            "Location is not supported by this browser."
        );

        return;

    }

    navigator.geolocation.getCurrentPosition(

        function(position) {

            document.getElementById(
                "latitude"
            ).value = position.coords.latitude;

            document.getElementById(
                "longitude"
            ).value = position.coords.longitude;

            document.getElementById(
                "riskForm"
            ).submit();

        },

        function(error) {

            alert(
                "Please allow location access to check your paddy field risk."
            );

        }

    );

}

</script>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True)