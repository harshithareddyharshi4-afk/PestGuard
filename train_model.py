from flask import Flask, request
import joblib
import requests
import pandas as pd

app = Flask(__name__)

# =========================================================
# LOAD AI MODELS
# =========================================================

risk_model = joblib.load("risk_model.pkl")
pest_model = joblib.load("pest_model.pkl")

# Store last 10 risk predictions
risk_history = []


# =========================================================
# TRANSLATIONS
# =========================================================

translations = {
    "English": {
        "title": "PestGuard",
        "subtitle": "AI-Based Paddy Pest Outbreak Early Warning System",
        "crop": "Paddy Crop Monitoring",
        "conditions": "Paddy Field Conditions",
        "field": "Field Name",
        "field_placeholder": "Example: Paddy Field",
        "temperature": "Temperature (°C)",
        "humidity": "Humidity (%)",
        "rainfall": "Rainfall (mm)",
        "location": "Use My Location",
        "location_wait": "Getting your field location...",
        "location_success": "Location captured. Getting weather...",
        "location_error": "Unable to get your location.",
        "weather_success": "Weather loaded successfully. AI analysis completed.",
        "weather_error": "Unable to load weather data.",
        "status": "Current Paddy Pest Risk",
        "waiting": "Waiting for analysis",
        "confidence": "Model Confidence",
        "current": "Current Conditions",
        "guidance": "Paddy Farmer Guidance",
        "history": "Paddy Pest Risk History",
        "recent": "Recent prediction levels",
        "pest": "Pest Pattern",
        "no_pest": "No specific pest indicated",
        "pest_possible": "Possible pest pattern",
        "pest_high": "High-risk pest pattern detected",
        "warning_high": "EARLY WARNING: High paddy pest risk detected!",
        "warning_medium": "CAUTION: Moderate paddy pest risk detected.",
        "warning_low": "ALERT: Current paddy pest risk is low.",
        "advice_high": "Monitor the paddy crop closely.<br>Inspect leaves and stems regularly.<br>Continue monitoring over the next few days.",
        "advice_medium": "Monitor the paddy crop regularly.<br>Look for early signs of pest activity.<br>Recheck the risk after a few days.",
        "advice_low": "Continue normal paddy crop monitoring.<br>Check the plants regularly.",
        "select": "Language"
    },

    "Tamil": {
        "title": "PestGuard",
        "subtitle": "AI-Based Paddy Pest Outbreak Early Warning System",
        "crop": "Paddy Crop Monitoring",
        "conditions": "Paddy Field Conditions",
        "field": "Field Name",
        "field_placeholder": "Example: Paddy Field",
        "temperature": "Temperature (°C)",
        "humidity": "Humidity (%)",
        "rainfall": "Rainfall (mm)",
        "location": "Use My Location",
        "location_wait": "Getting your field location...",
        "location_success": "Location captured. Getting weather...",
        "location_error": "Unable to get your location.",
        "weather_success": "Weather loaded successfully. AI analysis completed.",
        "weather_error": "Unable to load weather data.",
        "status": "Current Paddy Pest Risk",
        "waiting": "Waiting for analysis",
        "confidence": "Model Confidence",
        "current": "Current Conditions",
        "guidance": "Paddy Farmer Guidance",
        "history": "Paddy Pest Risk History",
        "recent": "Recent prediction levels",
        "pest": "Pest Pattern",
        "no_pest": "No specific pest indicated",
        "pest_possible": "Possible pest pattern",
        "pest_high": "High-risk pest pattern detected",
        "warning_high": "EARLY WARNING: High paddy pest risk detected!",
        "warning_medium": "CAUTION: Moderate paddy pest risk detected.",
        "warning_low": "ALERT: Current paddy pest risk is low.",
        "advice_high": "Monitor the paddy crop closely.<br>Inspect leaves and stems regularly.",
        "advice_medium": "Monitor the paddy crop regularly.<br>Look for early signs of pest activity.",
        "advice_low": "Continue normal paddy crop monitoring.<br>Check the plants regularly.",
        "select": "Language"
    },

    "Telugu": {
        "title": "PestGuard",
        "subtitle": "AI-Based Paddy Pest Outbreak Early Warning System",
        "crop": "Paddy Crop Monitoring",
        "conditions": "Paddy Field Conditions",
        "field": "Field Name",
        "field_placeholder": "Example: Paddy Field",
        "temperature": "Temperature (°C)",
        "humidity": "Humidity (%)",
        "rainfall": "Rainfall (mm)",
        "location": "Use My Location",
        "location_wait": "Getting your field location...",
        "location_success": "Location captured. Getting weather...",
        "location_error": "Unable to get your location.",
        "weather_success": "Weather loaded successfully. AI analysis completed.",
        "weather_error": "Unable to load weather data.",
        "status": "Current Paddy Pest Risk",
        "waiting": "Waiting for analysis",
        "confidence": "Model Confidence",
        "current": "Current Conditions",
        "guidance": "Paddy Farmer Guidance",
        "history": "Paddy Pest Risk History",
        "recent": "Recent prediction levels",
        "pest": "Pest Pattern",
        "no_pest": "No specific pest indicated",
        "pest_possible": "Possible pest pattern",
        "pest_high": "High-risk pest pattern detected",
        "warning_high": "EARLY WARNING: High paddy pest risk detected!",
        "warning_medium": "CAUTION: Moderate paddy pest risk detected.",
        "warning_low": "ALERT: Current paddy pest risk is low.",
        "advice_high": "Monitor the paddy crop closely.<br>Inspect leaves and stems regularly.",
        "advice_medium": "Monitor the paddy crop regularly.<br>Look for early signs of pest activity.",
        "advice_low": "Continue normal paddy crop monitoring.<br>Check the plants regularly.",
        "select": "Language"
    }
}


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    language = request.form.get(
        "language",
        request.args.get("language", "English")
    )

    if language not in translations:
        language = "English"

    t = translations[language]

    risk = ""
    confidence = ""
    warning = ""
    advice = ""
    pest_display = ""

    risk_class = ""

    field_name = ""
    temperature = ""
    humidity = ""
    rainfall = ""

    latitude = ""
    longitude = ""

    message = ""

    # =====================================================
    # FORM SUBMITTED
    # =====================================================

    if request.method == "POST":

        field_name = request.form.get(
            "field_name",
            "Paddy Field"
        )

        latitude = request.form.get(
            "latitude",
            ""
        )

        longitude = request.form.get(
            "longitude",
            ""
        )

        # -------------------------------------------------
        # AUTOMATIC ANALYSIS
        # -------------------------------------------------

        if request.form.get("action") == "auto_analyze":

            try:

                if not latitude or not longitude:

                    message = t["location_error"]

                else:

                    # -------------------------------------------------
                    # GET LIVE WEATHER
                    # -------------------------------------------------

                    url = (
                        "https://api.open-meteo.com/v1/forecast"
                        f"?latitude={latitude}"
                        f"&longitude={longitude}"
                        "&current=temperature_2m,"
                        "relative_humidity_2m,"
                        "rain,"
                        "precipitation"
                    )

                    response = requests.get(
                        url,
                        timeout=10
                    )

                    response.raise_for_status()

                    weather_data = response.json()

                    current = weather_data["current"]

                    temperature = float(
                        current["temperature_2m"]
                    )

                    humidity = float(
                        current["relative_humidity_2m"]
                    )

                    rainfall = float(
                        current.get(
                            "rain",
                            current.get("precipitation", 0)
                        )
                    )

                    # -------------------------------------------------
                    # CREATE MODEL INPUT
                    # -------------------------------------------------

                    inputs = pd.DataFrame(
                        [[
                            temperature,
                            humidity,
                            rainfall
                        ]],
                        columns=[
                            "temperature",
                            "humidity",
                            "rainfall"
                        ]
                    )

                    # -------------------------------------------------
                    # RISK MODEL
                    # -------------------------------------------------

                    risk = risk_model.predict(inputs)[0]

                    probabilities = risk_model.predict_proba(
                        inputs
                    )[0]

                    confidence = round(
                        max(probabilities) * 100,
                        1
                    )

                    # -------------------------------------------------
                    # PEST MODEL
                    # -------------------------------------------------

                    if risk == "LOW":

                        # LOW risk = don't show a specific pest
                        pest_display = t["no_pest"]

                        warning = t["warning_low"]
                        advice = t["advice_low"]

                        risk_class = "low"

                    else:

                        # For MEDIUM/HIGH, predict pest pattern
                        pest_type = pest_model.predict(inputs)[0]

                        pest_display = pest_type

                        if risk == "HIGH":

                            warning = t["warning_high"]
                            advice = t["advice_high"]

                            risk_class = "high"

                        else:

                            warning = t["warning_medium"]
                            advice = t["advice_medium"]

                            risk_class = "medium"

                    # -------------------------------------------------
                    # SAVE HISTORY
                    # -------------------------------------------------

                    risk_history.append(risk)

                    if len(risk_history) > 10:
                        risk_history.pop(0)

                    message = t["weather_success"]

            except Exception as e:

                print("ERROR:", e)

                message = t["weather_error"]

    # =========================================================
    # CHART DATA
    # =========================================================

    chart_values = []

    for item in risk_history:

        if item == "LOW":
            chart_values.append(1)

        elif item == "MEDIUM":
            chart_values.append(2)

        elif item == "HIGH":
            chart_values.append(3)

    # =========================================================
    # HTML PAGE
    # =========================================================

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>{t["title"]}</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #eef7ee;
    color: #222;
}}

.dashboard {{
    max-width: 1000px;
    margin: auto;
    padding: 30px 20px;
}}

.header {{
    background: white;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}}

.logo {{
    font-size: 45px;
}}

.header h1 {{
    margin: 5px;
    font-size: 42px;
}}

.subtitle {{
    color: #666;
    font-size: 18px;
}}

.language-box {{
    margin-top: 20px;
}}

select {{
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 16px;
}}

.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}}

.card {{
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}}

input {{
    width: 100%;
    padding: 14px;
    margin: 8px 0;
    border: 1px solid #ccc;
    border-radius: 10px;
    font-size: 16px;
}}

button {{
    width: 100%;
    margin-top: 12px;
    padding: 15px;
    border: none;
    border-radius: 10px;
    font-size: 17px;
    cursor: pointer;
    background: #7b1fa2;
    color: white;
    font-weight: bold;
}}

.message {{
    margin-top: 12px;
    padding: 12px;
    background: #e8f5e9;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
}}

.risk {{
    padding: 22px;
    border-radius: 15px;
    text-align: center;
    font-size: 32px;
    font-weight: bold;
}}

.high {{
    background: #ffe0e0;
    color: #b71c1c;
}}

.medium {{
    background: #fff0c2;
    color: #8a6500;
}}

.low {{
    background: #dff5df;
    color: #246b2a;
}}

.warning {{
    margin-top: 15px;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
}}

.pest {{
    background: #f7f7f7;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}}

.info-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 20px;
}}

.info {{
    background: #f7f7f7;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
}}

.icon {{
    font-size: 25px;
}}

.value {{
    font-size: 22px;
    font-weight: bold;
    margin-top: 5px;
}}

.confidence {{
    text-align: center;
    margin-top: 20px;
    font-size: 18px;
}}

.advice {{
    margin-top: 20px;
    padding: 18px;
    background: #f7f7f7;
    border-radius: 12px;
    line-height: 1.8;
    font-size: 16px;
}}

.chart-card {{
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}}

.chart-container {{
    position: relative;
    height: 320px;
}}

.footer {{
    text-align: center;
    color: #666;
    margin-top: 20px;
    font-size: 14px;
}}

@media (max-width: 700px) {{

    .grid {{
        grid-template-columns: 1fr;
    }}

    .info-grid {{
        grid-template-columns: 1fr;
    }}

    .header h1 {{
        font-size: 32px;
    }}

}}

</style>

</head>


<body>

<div class="dashboard">


<div class="header">

    <div class="logo">🌾</div>

    <h1>{t["title"]}</h1>

    <p class="subtitle">
        {t["subtitle"]}
    </p>

    <h3>🌾 {t["crop"]}</h3>

    <div class="language-box">

        <form method="POST">

            <input
                type="hidden"
                name="action"
                value="language"
            >

            <label>
                <b>{t["select"]}:</b>
            </label>

            <select
                name="language"
                onchange="this.form.submit()"
            >

                <option
                    value="English"
                    {"selected" if language == "English" else ""}
                >
                    English
                </option>

                <option
                    value="Tamil"
                    {"selected" if language == "Tamil" else ""}
                >
                    தமிழ்
                </option>

                <option
                    value="Telugu"
                    {"selected" if language == "Telugu" else ""}
                >
                    తెలుగు
                </option>

            </select>

        </form>

    </div>

</div>


<div class="grid">


<div class="card">

    <h2>📍 {t["conditions"]}</h2>

    <form method="POST" id="autoForm">

        <input
            type="hidden"
            name="action"
            value="auto_analyze"
        >

        <input
            type="hidden"
            name="language"
            value="{language}"
        >

        <input
            type="text"
            name="field_name"
            placeholder="{t["field_placeholder"]}"
            value="{field_name}"
            required
        >

        <input
            type="hidden"
            name="latitude"
            id="latitude"
            value="{latitude}"
        >

        <input
            type="hidden"
            name="longitude"
            id="longitude"
            value="{longitude}"
        >

        <button
            type="button"
            onclick="startAutomaticAnalysis()"
        >
            📍 {t["location"]}
        </button>

        <div
            id="locationMessage"
            class="message"
            style="display:none;"
        ></div>

    </form>

</div>


<div class="card">

    <h2>🚦 {t["status"]}</h2>

    <div class="risk {risk_class}">
        {risk if risk else t["waiting"]}
    </div>

    <div class="warning">
        {warning}
    </div>

    <div class="confidence">

        🤖 {t["confidence"]}:

        <b>
            {confidence if confidence else "--"}%
        </b>

    </div>

</div>

</div>


<div class="card">

    <h2>🌾 {t["field"]}: {field_name if field_name else "--"}</h2>

    <h2>🐛 {t["pest"]}</h2>

    <div class="pest">

        {pest_display if pest_display else "--"}

    </div>

    <h2>📋 {t["current"]}</h2>

    <div class="info-grid">


        <div class="info">

            <div class="icon">🌡️</div>

            {t["temperature"]}

            <div class="value">
                {temperature if temperature else "--"}
            </div>

        </div>


        <div class="info">

            <div class="icon">💧</div>

            {t["humidity"]}

            <div class="value">
                {humidity if humidity else "--"}
            </div>

        </div>


        <div class="info">

            <div class="icon">🌧️</div>

            {t["rainfall"]}

            <div class="value">
                {rainfall if rainfall != "" else "--"}
            </div>

        </div>


    </div>


    <div class="advice">

        <b>
            👨‍🌾 {t["guidance"]}
        </b>

        <br><br>

        {advice if advice else "Use My Location to start automatic analysis."}

    </div>

</div>


<div class="chart-card">

    <h2>📊 {t["history"]}</h2>

    <p>{t["recent"]}</p>

    <div class="chart-container">

        <canvas id="riskChart"></canvas>

    </div>

</div>


<div class="footer">

    PestGuard • AI Paddy Agriculture Early Warning Prototype

</div>


</div>


<script>

function startAutomaticAnalysis() {{

    const message =
        document.getElementById("locationMessage");

    message.style.display = "block";

    message.innerText =
        "{t["location_wait"]}";


    if (!navigator.geolocation) {{

        message.innerText =
            "{t["location_error"]}";

        return;

    }}


    navigator.geolocation.getCurrentPosition(

        function(position) {{

            document.getElementById(
                "latitude"
            ).value =
                position.coords.latitude;

            document.getElementById(
                "longitude"
            ).value =
                position.coords.longitude;

            message.innerText =
                "{t["location_success"]}";

            document
                .getElementById("autoForm")
                .submit();

        }},

        function(error) {{

            message.innerText =
                "{t["location_error"]};

        }}

    );

}}


const riskValues = {chart_values};

const labels = riskValues.map(
    (_, index) => "Check " + (index + 1)
);


new Chart(

    document.getElementById("riskChart"),

    {{

        type: "line",

        data: {{

            labels: labels,

            datasets: [{{

                label: "Paddy Pest Risk Level",

                data: riskValues,

                tension: 0.3,

                fill: false,

                pointRadius: 7

            }}]

        }},

        options: {{

            responsive: true,

            maintainAspectRatio: false,

            scales: {{

                y: {{

                    min: 1,

                    max: 3,

                    ticks: {{

                        stepSize: 1,

                        callback: function(value) {{

                            if (value === 1)
                                return "LOW";

                            if (value === 2)
                                return "MEDIUM";

                            if (value === 3)
                                return "HIGH";

                            return "";

                        }}

                    }}

                }}

            }}

        }}

    }}

);

</script>

</body>

</html>
"""


# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )