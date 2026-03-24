import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import serpapi


load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv('OPENWEATHER_API_KEY')
SERP_API_KEY = os.getenv('SERP_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_city_events', methods=['POST'])
def get_city_events():
    data = request.get_json()
    city_name = data.get('city')
    
    if not city_name:
        return jsonify({"error": "City name is required"}), 400

    try:
        client = serpapi.Client(api_key=SERP_API_KEY)
        results = client.search({
            "engine": "google_events",
            "q": f"Events in {city_name}"
            })
        
        events_results = results.get("events_results", [])
        
        # 4. Slice for top 3
        top_three_events = events_results[:3]

        return jsonify(top_three_events)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_city_weather', methods=['POST'])
def get_city_weather():
    data = request.json
    city_name = data.get('city')
    geolocator = Nominatim(user_agent="Travel_dashboard")
    location = geolocator.geocode(city_name)
    lat = location.latitude
    long = location.longitude
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat,
        'lon': long,
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