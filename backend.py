import os
import requests
from flask import Flask, render_template, request, jsonify, url_for, redirect
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import serpapi

from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz # Use zoneinfo if on Python 3.9+

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv('OPENWEATHER_API_KEY')
SERP_API_KEY = os.getenv('SERP_API_KEY')

# need to use docker to install n8n on ec2 otherwise it will break
# might need to switch to lamda if it's easier
def send_email_summary(city, weather, events, email):
    url = "http://ec2-18-225-195-196.us-east-2.compute.amazonaws.com:5678/webhook/send-email"

    response = requests.post(url, json={
        "city": city,
        "weather": weather,
        "events": events,
        "email": email
    })

    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

# email
@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.get_json()

    city = data.get('city')
    weather = data.get('weather')
    events = data.get('events')
    email = data.get('email')

    try:
        send_email_summary(city, weather, events, email)
        return jsonify({"status": "Email sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_city_time", methods=['POST'])
def get_time_and_timezone():
    """
    Gets the current time and timezone for a given city name.
    """
    data = request.get_json()
    city_name = data.get('city')
    geolocator = Nominatim(user_agent="city_time_app")
    location = geolocator.geocode(city_name)

    if not location:
        return f"Could not find coordinates for {city_name}"

    # 2. Get the timezone name from the coordinates
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lng=location.longitude, lat=location.latitude)

    if not timezone_name:
        return f"Could not find timezone for {city_name}"

    # 3. Get the current time in that timezone
    # Using pytz
    local_timezone = pytz.timezone(timezone_name)
    current_time = datetime.now(local_timezone)

    try:
        return jsonify({
        "city": city_name,
        "timezone": timezone_name,
        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "latitude": location.latitude,
        "longitude": location.longitude
        })
    except Exception as e:
            return jsonify({"error": str(e)}), 500     


@app.route("/get_city_flights", methods=['POST'])
def get_city_flights():
    data = request.get_json()
    city_name = data.get('city')

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