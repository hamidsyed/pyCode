import requests
import datetime

class weatherClass:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.url = "https://api.open-meteo.com/v1/forecast"

    def fetch_weather_data(self):
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,diffuse_radiation,direct_radiation,weather_code",
            "timezone": "auto",
            "current_weather": "true"
        }
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return None

    def get_current_weather(self):
        data = self.fetch_weather_data()
        if data:
            current_time = datetime.datetime.now()
            current_hourly_data = data["hourly"]

            current_time_str = current_time.isoformat(timespec='minutes')[:-3] + "00"
            
            try:
                time_index = current_hourly_data["time"].index(current_time_str)
            except ValueError:
                time_index = -1
                min_diff = datetime.timedelta.max
                for i, t_str in enumerate(current_hourly_data["time"]):
                    t = datetime.datetime.fromisoformat(t_str)
                    diff = abs(t - current_time)
                    if diff < min_diff:
                        min_diff = diff
                        time_index = i
                if time_index == -1:
                    return None

            temperature = current_hourly_data["temperature_2m"][time_index]
            relative_humidity = current_hourly_data["relative_humidity_2m"][time_index]
            wind_speed = current_hourly_data["wind_speed_10m"][time_index]
            diffuse_radiation = current_hourly_data["diffuse_radiation"][time_index]
            direct_radiation = current_hourly_data["direct_radiation"][time_index]
            weather_code = current_hourly_data["weather_code"][time_index]

            return {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "current_time": current_time_str,
                "temperature": temperature,
                "relative_humidity": relative_humidity,
                "wind_speed": wind_speed,
                "diffuse_radiation": diffuse_radiation,
                "direct_radiation": direct_radiation,
                "weather_code": weather_code
            }
        return None
