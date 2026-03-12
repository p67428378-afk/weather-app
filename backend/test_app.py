import pytest
from unittest.mock import patch
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_weather_success(client):
    with patch('requests.get') as mock_get:
        # Mock geocoding API response
        mock_get.side_effect = [
            pytest.mock_response(status_code=200, json_data={
                "results": [{
                    "latitude": 51.5074,
                    "longitude": 0.1278,
                    "name": "London"
                }]
            }),
            # Mock weather API response
            pytest.mock_response(status_code=200, json_data={
                "current_weather": {
                    "temperature": 10.5,
                    "windspeed": 15.3,
                    "weathercode": 3
                }
            })
        ]
        response = client.get('/api/weather?city=London')
        assert response.status_code == 200
        data = response.get_json()
        assert data['city'] == 'London'
        assert data['temperature'] == '10.5°C'
        assert data['wind_speed'] == '15.3 km/h'
        assert data['conditions'] == 'Overcast'
        assert data['humidity'] == 'N/A'

def test_get_weather_empty_city(client):
    response = client.get('/api/weather?city=')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Please enter a city name'

def test_get_weather_city_not_found(client):
    with patch('requests.get') as mock_get:
        # Mock geocoding API response with no results
        mock_get.return_value = pytest.mock_response(status_code=200, json_data={
            "results": []
        })
        response = client.get('/api/weather?city=NonExistentCity')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'City not found or no weather data available.'

def test_get_weather_api_error(client):
    with patch('requests.get') as mock_get:
        # Mock geocoding API success
        mock_get.side_effect = [
            pytest.mock_response(status_code=200, json_data={
                "results": [{
                    "latitude": 51.5074,
                    "longitude": 0.1278,
                    "name": "London"
                }]
            }),
            # Mock weather API failure
            pytest.mock_response(status_code=500, text_data="Internal Server Error", raise_for_status=True)
        ]
        response = client.get('/api/weather?city=London')
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Could not retrieve weather data. Please try again later.'
