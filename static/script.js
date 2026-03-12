document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('cityInput');
    const searchButton = document.getElementById('searchButton');
    const weatherDisplay = document.getElementById('weatherDisplay');
    const cityNameElem = document.getElementById('cityName');
    const temperatureElem = document.getElementById('temperature');
    const humidityElem = document.getElementById('humidity');
    const windSpeedElem = document.getElementById('windSpeed');
    const conditionsElem = document.getElementById('conditions');
    const errorMessageElem = document.getElementById('errorMessage');
    const loadingMessageElem = document.getElementById('loadingMessage');

    const API_BASE_URL = '/api/weather'; // Flask backend endpoint

    const clearWeatherDisplay = () => {
        cityNameElem.textContent = '';
        temperatureElem.textContent = '';
        humidityElem.textContent = '';
        windSpeedElem.textContent = '';
        conditionsElem.textContent = '';
        errorMessageElem.textContent = '';
        weatherDisplay.style.display = 'none';
    };

    const showLoading = () => {
        loadingMessageElem.style.display = 'block';
    };

    const hideLoading = () => {
        loadingMessageElem.style.display = 'none';
    };

    const fetchWeather = async () => {
        clearWeatherDisplay();
        showLoading();
        const city = cityInput.value.trim();

        if (!city) {
            errorMessageElem.textContent = 'Please enter a city name.';
            hideLoading();
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}?city=${encodeURIComponent(city)}`);
            const data = await response.json();

            if (!response.ok) {
                errorMessageElem.textContent = data.error || 'Could not retrieve weather data. Please try again later.';
                return;
            }

            cityNameElem.textContent = `Weather in ${data.city}`;
            temperatureElem.textContent = `Temperature: ${data.temperature}`;
            humidityElem.textContent = `Humidity: ${data.humidity}`;
            windSpeedElem.textContent = `Wind Speed: ${data.wind_speed}`;
            conditionsElem.textContent = `Conditions: ${data.conditions}`;
            weatherDisplay.style.display = 'block';

        } catch (error) {
            console.error('Error fetching weather:', error);
            errorMessageElem.textContent = 'Network error. Please try again later.';
        } finally {
            hideLoading();
        }
    };

    searchButton.addEventListener('click', fetchWeather);

    cityInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            fetchWeather();
        }
    });
});
