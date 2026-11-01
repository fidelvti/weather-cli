import sys
from datetime import datetime

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


WEATHER_CODES = {
    0: "☀️ Clear sky",
    1: "🌤️ Mainly clear",
    2: "⛅ Partly cloudy",
    3: "☁️ Overcast",
    45: "🌁 Fog",
    48: "🌁 Depositing rime fog",
    51: "🌦️ Light drizzle",
    53: "🌦️ Moderate drizzle",
    55: "🌧️ Dense drizzle",
    56: "🌧️ Light freezing drizzle",
    57: "🌧️ Dense freezing drizzle",
    61: "🌦️ Slight rain",
    63: "🌧️ Moderate rain",
    65: "🌧️ Heavy rain",
    66: "🌧️ Light freezing rain",
    67: "🌧️ Heavy freezing rain",
    71: "🌨️ Slight snow fall",
    73: "🌨️ Moderate snow fall",
    75: "❄️ Heavy snow fall",
    77: "❄️ Snow grains",
    80: "🌦️ Slight rain showers",
    81: "🌧️ Moderate rain showers",
    82: "🌧️ Violent rain showers",
    85: "🌨️ Slight snow showers",
    86: "❄️ Heavy snow showers",
    95: "⛈️ Thunderstorm",
    96: "⛈️ Thunderstorm with slight hail",
    99: "⛈️ Thunderstorm with heavy hail",
}


def describe_weather_code(code):
    return WEATHER_CODES.get(code, f"❓ Unknown conditions (code {code})")


def get_location(city):
    resp = requests.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=5)
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None
    return results[0]


def get_weather(lat, lon):
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": 7,
            "timezone": "auto",
        },
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["current"], data["daily"]


def print_forecast(daily):
    print()
    print("7-day forecast:")
    for i, day in enumerate(daily["time"]):
        label = datetime.strptime(day, "%Y-%m-%d").strftime("%a %d %b")
        print(
            f"  {label}: {describe_weather_code(daily['weather_code'][i])}, "
            f"{daily['temperature_2m_min'][i]}°C / {daily['temperature_2m_max'][i]}°C, "
            f"rain {daily['precipitation_sum'][i]} mm"
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python weather.py <city_name>")
        return

    city = " ".join(sys.argv[1:])

    try:
        location = get_location(city)
        if location is None:
            print(f"City not found: {city}")
            return

        current, daily = get_weather(location["latitude"], location["longitude"])
        place = location["name"]
        if location.get("country"):
            place += f", {location['country']}"
        print(
            f"{place}: {current['temperature_2m']}°C "
            f"(feels like {current['apparent_temperature']}°C), "
            f"humidity {current['relative_humidity_2m']}%, "
            f"wind {current['wind_speed_10m']} km/h"
        )
        print(describe_weather_code(current["weather_code"]))
        print_forecast(daily)

    except requests.exceptions.RequestException:
        print("Couldn't connect to the weather service. Check your internet connection and try again.")
    except (KeyError, ValueError):
        print("Something went wrong while reading the weather data.")


if __name__ == "__main__":
    main()
