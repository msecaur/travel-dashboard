import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv('OPENWEATHER_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    # Receive JSON data from the frontend
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'imperial'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        # Process data to only return midday forecasts
        forecast_list = []
        for entry in weather_data['list']:
            if "12:00:00" in entry['dt_txt']:
                forecast_list.append({
                    "date": entry['dt_txt'],
                    "temp": entry['main']['temp'],
                    "desc": entry['weather'][0]['description']
                })
        
        return jsonify(forecast_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)