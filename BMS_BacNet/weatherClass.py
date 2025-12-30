import requests
import datetime

class weatherClass:
    def __init__(self, latitude, longitude, cache_minutes: int = 5):
        self.latitude = latitude
        self.longitude = longitude
        self.url = "https://api.open-meteo.com/v1/forecast"
        self._cache_minutes = cache_minutes
        self._cache = None
        self._cache_time = None

    def fetch_weather_data(self):
        """Fetch fresh weather data from Open-Meteo API"""
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,diffuse_radiation,direct_radiation,weather_code",
            "timezone": "auto",
            "current_weather": "true"
        }
        try:
            response = requests.get(self.url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return None

    def get_current_weather(self):
        """Return cached weather if recent, otherwise fetch new"""
        now = datetime.datetime.now()
        if self._cache and self._cache_time:
            diff = (now - self._cache_time).total_seconds() / 60
            if diff < self._cache_minutes:
                return self._cache  # return cached data

        # Fetch new data
        data = self.fetch_weather_data()
        if not data:
            return self._cache  # fallback to last cached if available

        current_hourly_data = data.get("hourly", {})
        current_time = now
        current_time_str = current_time.isoformat(timespec='minutes')[:-3] + "00"

        # Find closest time index
        time_index = -1
        min_diff = datetime.timedelta.max
        for i, t_str in enumerate(current_hourly_data.get("time", [])):
            t = datetime.datetime.fromisoformat(t_str)
            diff = abs(t - current_time)
            if diff < min_diff:
                min_diff = diff
                time_index = i
        if time_index == -1:
            return None

        weather = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current_time": current_time_str,
            "temperature": current_hourly_data["temperature_2m"][time_index],
            "relative_humidity": current_hourly_data["relative_humidity_2m"][time_index],
            "wind_speed": current_hourly_data["wind_speed_10m"][time_index],
            "diffuse_radiation": current_hourly_data["diffuse_radiation"][time_index],
            "direct_radiation": current_hourly_data["direct_radiation"][time_index],
            "weather_code": current_hourly_data["weather_code"][time_index]
        }

        # Update cache
        self._cache = weather
        self._cache_time = now
        return weather
