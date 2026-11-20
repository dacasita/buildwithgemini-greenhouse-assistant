"""Live weather and humidity lookup using Open-Meteo free API."""

import urllib.parse
import urllib.request
import json
from typing import Dict, Any


def get_live_weather(city: str) -> Dict[str, Any]:
    """Gets real-time live weather, temperature, and humidity for a city using Open-Meteo.
    Useful for checking outdoor/indoor growing climate and plant care recommendations.

    Args:
        city: The name of the city (e.g. 'Taipei', 'San Francisco', 'New York').

    Returns:
        A dictionary with temperature, humidity, apparent temperature, and location info.
    """
    try:
        encoded_city = urllib.parse.quote(city.strip())
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "GreenhouseAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            geo_data = json.loads(resp.read().decode())

        if not geo_data.get("results"):
            return {"error": f"City '{city}' not found."}

        loc = geo_data["results"][0]
        lat = loc["latitude"]
        lon = loc["longitude"]
        city_name = loc.get("name", city)
        country = loc.get("country", "")

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation"
        )
        req_w = urllib.request.Request(weather_url, headers={"User-Agent": "GreenhouseAssistant/1.0"})
        with urllib.request.urlopen(req_w, timeout=5) as resp_w:
            weather_data = json.loads(resp_w.read().decode())

        curr = weather_data.get("current", {})
        return {
            "city": city_name,
            "country": country,
            "temperature_c": curr.get("temperature_2m"),
            "relative_humidity_pct": curr.get("relative_humidity_2m"),
            "apparent_temperature_c": curr.get("apparent_temperature"),
            "precipitation_mm": curr.get("precipitation"),
        }
    except Exception as e:
        return {"error": f"Failed to retrieve weather for '{city}': {str(e)}"}


get_live_climate = get_live_weather

