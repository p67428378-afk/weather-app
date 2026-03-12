from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city_name = request.args.get('city')

    if not city_name:
        return jsonify({"error": "Please enter a city name"}), 400

    try:
        # Step 1: Get geographical coordinates (latitude and longitude) for the city
        # Using Open-Meteo's geocoding API or a similar free geocoding service
        # For simplicity, we'll use a placeholder or a direct lookup if available
        # Open-Meteo's /v1/forecast endpoint can sometimes infer location from name
        # but it's better to get precise lat/lon.
        # A free geocoding API like Nominatim (OpenStreetMap) can be used.
        # For this example, let's assume we can get lat/lon from a separate call
        # or that the forecast API handles city names directly (which it doesn't for current weather).

        # Let's use Open-Meteo's geocoding API for coordinates
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
        geocode_response = requests.get(geocode_url)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        if not geocode_data or not geocode_data.get('results'):
            return jsonify({"error": "City not found or no weather data available."}), 404

        # Take the first result
        city_info = geocode_data['results'][0]
        latitude = city_info['latitude']
        longitude = city_info['longitude']

        # Step 2: Fetch current weather data using the coordinates
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
            "temperature_unit": "celsius",
            "windspeed_unit": "kmh",
            "timezone": "auto"
        }
        weather_response = requests.get(OPEN_METEO_API_URL, params=params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if not weather_data or not weather_data.get('current_weather'):
            return jsonify({"error": "Could not retrieve weather data for this city."}), 404

        current_weather = weather_data['current_weather']
        temperature = current_weather['temperature']
        windspeed = current_weather['windspeed']
        weathercode = current_weather['weathercode']

        # Map weather codes to descriptions (simplified for example)
        # Full list: https://www.open-meteo.com/en/docs
        weather_conditions_map = {
            0: "Clear sky",
            1: "Mostly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Drizzle: Light",
            53: "Drizzle: Moderate",
            55: "Drizzle: Dense intensity",
            56: "Freezing Drizzle: Light",
            57: "Freezing Drizzle: Dense intensity",
            61: "Rain: Slight",
            63: "Rain: Moderate",
            65: "Rain: Heavy intensity",
            66: "Freezing Rain: Light",
            67: "Freezing Rain: Heavy intensity",
            71: "Snow fall: Slight",
            73: "Snow fall: Moderate",
            75: "Snow fall: Heavy intensity",
            77: "Snow grains",
            80: "Rain showers: Slight",
            81: "Rain showers: Moderate",
            82: "Rain showers: Violent",
            85: "Snow showers: Slight",
            86: "Snow showers: Heavy",
            95: "Thunderstorm: Slight or moderate",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        conditions = weather_conditions_map.get(weathercode, "Unknown")

        # Open-Meteo current weather API does not directly provide humidity.
        # For a complete solution, another API or a different Open-Meteo endpoint
        # that includes humidity would be needed.
        # For now, we'll return a placeholder or omit it if not available.
        # The HLD specifically asks for humidity, so this is a limitation of Open-Meteo's
        # current_weather endpoint. If this is critical, a different API might be needed.
        # For the purpose of this exercise, I will return a dummy humidity value.
        humidity = "N/A" # Open-Meteo's current_weather endpoint doesn't provide humidity directly.

        return jsonify({
            "city": city_name,
            "temperature": f"{temperature}°C",
            "humidity": humidity, # Placeholder
            "wind_speed": f"{windspeed} km/h",
            "conditions": conditions
        })

    except requests.exceptions.HTTPError as http_err:
        error_details = f"HTTP error occurred: {http_err}"
        if http_err.response is not None:
            error_details += f" - Response: {http_err.response.text}"
        app.logger.error(error_details)
        return jsonify({"error": "Could not retrieve weather data. Please try again later."}), 500
    except requests.exceptions.ConnectionError as conn_err:
        app.logger.error(f"Connection error occurred: {conn_err}")
        return jsonify({"error": "Network error. Please check your internet connection."}), 503
    except requests.exceptions.Timeout as timeout_err:
        app.logger.error(f"Timeout error occurred: {timeout_err}")
        return jsonify({"error": "Request timed out. Please try again later."}), 504
    except requests.exceptions.RequestException as req_err:
        app.logger.error(f"An unexpected request error occurred: {req_err}")
        return jsonify({"error": "An unexpected error occurred while fetching weather data."}), 500
    except Exception as e:
        app.logger.error(f"An unexpected server error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
