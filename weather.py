import argparse
from datetime import datetime

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

UNITS = {
    "metric": {"temp": "°C", "wind": "km/h", "rain": "mm", "api": {}},
    "imperial": {
        "temp": "°F",
        "wind": "mph",
        "rain": "in",
        "api": {
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
        },
    },
}


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


def get_weather(lat, lon, units):
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": 7,
            "timezone": "auto",
            **UNITS[units]["api"],
        },
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["current"], data["daily"]


def format_place(location):
    parts = [location["name"]]
    region = location.get("admin1")
    if region and region != location["name"]:
        parts.append(region)
    if location.get("country"):
        parts.append(location["country"])
    return ", ".join(parts)


def print_forecast(daily, units):
    u = UNITS[units]
    print()
    print("7-day forecast:")
    for i, day in enumerate(daily["time"]):
        label = datetime.strptime(day, "%Y-%m-%d").strftime("%a %d %b")
        print(
            f"  {label}: {describe_weather_code(daily['weather_code'][i])}, "
            f"{daily['temperature_2m_min'][i]}{u['temp']} / {daily['temperature_2m_max'][i]}{u['temp']}, "
            f"rain {daily['precipitation_sum'][i]} {u['rain']}"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Show the current weather and a 7-day forecast for a city."
    )
    parser.add_argument(
        "city",
        nargs="+",
        help='city name; add the region after a comma to disambiguate, e.g. "Springfield, Massachusetts"',
    )
    parser.add_argument(
        "-u",
        "--units",
        choices=sorted(UNITS),
        default="metric",
        help="metric (°C, km/h, mm) or imperial (°F, mph, in); default: metric",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    city = " ".join(args.city)
    units = args.units
    u = UNITS[units]

    try:
        location = get_location(city)
        if location is None:
            print(f"City not found: {city}")
            return

        current, daily = get_weather(location["latitude"], location["longitude"], units)
        print(
            f"{format_place(location)}: {current['temperature_2m']}{u['temp']} "
            f"(feels like {current['apparent_temperature']}{u['temp']}), "
            f"humidity {current['relative_humidity_2m']}%, "
            f"wind {current['wind_speed_10m']} {u['wind']}"
        )
        print(describe_weather_code(current["weather_code"]))
        print_forecast(daily, units)

    except requests.exceptions.RequestException:
        print("Couldn't connect to the weather service. Check your internet connection and try again.")
    except (KeyError, ValueError):
        print("Something went wrong while reading the weather data.")


if __name__ == "__main__":
    main()
