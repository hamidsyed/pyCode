from weatherClass import weatherClass

def main():
    # Delhi's coordinates
    delhi_lat = 28.61
    delhi_lon = 77.23
    
    # Create an instance of weatherClass
    weather_provider = weatherClass(latitude=delhi_lat, longitude=delhi_lon)
    
    # Get the current weather data
    weather_data = weather_provider.get_current_weather()
    
    if weather_data:
        print(f"Weather in Delhi (Lat: {weather_data['latitude']}, Lon: {weather_data['longitude']}) for {weather_data['current_time']}:")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Relative Humidity: {weather_data['relative_humidity']}%")
        print(f"Wind Speed: {weather_data['wind_speed']} m/s")
        print(f"Diffuse Solar Radiation: {weather_data['diffuse_radiation']} W/m²")
        print(f"Direct Solar Radiation: {weather_data['direct_radiation']} W/m²")
        print(f"Weather Code: {weather_data['weather_code']}")
        print("\nNote: 'Total Electricity Energy (kWh)' is not available via Open-Meteo API.")
    else:
        print("Could not retrieve weather data.")

if __name__ == "__main__":
    main()

