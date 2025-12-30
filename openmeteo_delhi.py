import requests
import datetime

def get_delhi_weather():
    latitude = 28.61
    longitude = 77.23
    
    # Open-Meteo API endpoint
    url = "https://api.open-meteo.com/v1/forecast"
    
    # Get current hour for hourly forecast
    current_time = datetime.datetime.now()
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,diffuse_radiation,direct_radiation,weather_code",
        "timezone": "auto",
        "current_weather": "true" # Request current weather data
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "current_weather" in data:
            current_weather = data["current_weather"]
            current_hourly_data = data["hourly"]
            
            # Find the index for the current hour
            current_time_str = current_time.isoformat(timespec='minutes')[:-3] + "00" # Match format "YYYY-MM-DDTHH:00"
            
            try:
                time_index = current_hourly_data["time"].index(current_time_str)
            except ValueError:
                # If current_time_str is not exactly in the list, find the closest one
                # This can happen if the API returns times slightly different
                time_index = -1
                min_diff = datetime.timedelta.max
                for i, t_str in enumerate(current_hourly_data["time"]):
                    t = datetime.datetime.fromisoformat(t_str)
                    diff = abs(t - current_time)
                    if diff < min_diff:
                        min_diff = diff
                        time_index = i
                if time_index == -1:
                    raise ValueError("Could not find current hour in hourly data.")


            temperature = current_hourly_data["temperature_2m"][time_index]
            relative_humidity = current_hourly_data["relative_humidity_2m"][time_index]
            wind_speed = current_hourly_data["wind_speed_10m"][time_index]
            diffuse_radiation = current_hourly_data["diffuse_radiation"][time_index]
            direct_radiation = current_hourly_data["direct_radiation"][time_index]
            weather_code = current_hourly_data["weather_code"][time_index]

            print(f"Weather in Delhi (Lat: {latitude}, Lon: {longitude}) for {current_time_str}:")
            print(f"Temperature: {temperature}°C")
            print(f"Relative Humidity: {relative_humidity}%")
            print(f"Wind Speed: {wind_speed} m/s")
            print(f"Diffuse Solar Radiation: {diffuse_radiation} W/m²")
            print(f"Direct Solar Radiation: {direct_radiation} W/m²")
            print(f"Weather Code: {weather_code}")

        else:
            print("Current weather data not available in the response.")
            print(f"Full response: {data}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    get_delhi_weather()
