import datetime
import zoneinfo
import requests

def get_time_and_weather(city: str) -> dict:
    """
    Lookup latitude/longitude and timezone for city using Open-Meteo Geocoding API, 
    calculate exact local time, and retrieve weather data.
    """
    try:
        # Geocoding lookup
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get("results"):
            now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return {
                "city": city,
                "error": f"City '{city}' not found in geocoding service.",
                "current_local_time": now_utc
            }
        
        location = geo_res["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        country = location.get("country", "")
        tz_name = location.get("timezone", "UTC")
        
        # Calculate exact local time in target timezone
        try:
            tz = zoneinfo.ZoneInfo(tz_name)
            local_dt = datetime.datetime.now(tz)
            local_time_str = local_dt.strftime("%I:%M:%S %p %Z on %B %d, %Y (UTC%z)")
        except Exception:
            local_dt = datetime.datetime.now(datetime.timezone.utc)
            local_time_str = local_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            
        # Weather lookup
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(weather_url, timeout=5).json()
        current_w = w_res.get("current_weather", {})
        
        temp_c = current_w.get("temperature")
        wind_speed = current_w.get("windspeed")
        weather_code = current_w.get("weathercode")
        
        return {
            "city": location.get("name", city),
            "country": country,
            "timezone": tz_name,
            "current_local_time": local_time_str,
            "time_in_city": local_time_str,
            "temperature_celsius": temp_c,
            "temperature_fahrenheit": round(temp_c * 9/5 + 32, 1) if temp_c is not None else None,
            "wind_speed_kmh": wind_speed,
            "weather_code": weather_code
        }
    except Exception as e:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "city": city,
            "error": str(e),
            "current_local_time": now_str
        }

if __name__ == "__main__":
    print(get_time_and_weather("Tokyo"))
