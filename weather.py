import argparse
import os
import sys
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

ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌁", 48: "🌁",
    51: "🌦️", 53: "🌦️", 55: "🌧️", 56: "🌧️", 57: "🌧️",
    61: "🌦️", 63: "🌧️", 65: "🌧️", 66: "🌧️", 67: "🌧️",
    71: "🌨️", 73: "🌨️", 75: "❄️", 77: "❄️",
    80: "🌦️", 81: "🌧️", 82: "🌧️", 85: "🌨️", 86: "❄️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}

DESCRIPTIONS = {
    "en": {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    },
    "es": {
        0: "Cielo despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla", 48: "Niebla con escarcha",
        51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna densa",
        56: "Llovizna helada ligera", 57: "Llovizna helada densa",
        61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia fuerte",
        66: "Lluvia helada ligera", 67: "Lluvia helada fuerte",
        71: "Nevada ligera", 73: "Nevada moderada", 75: "Nevada fuerte",
        77: "Granos de nieve",
        80: "Chubascos ligeros", 81: "Chubascos moderados", 82: "Chubascos violentos",
        85: "Chubascos de nieve ligeros", 86: "Chubascos de nieve fuertes",
        95: "Tormenta", 96: "Tormenta con granizo ligero",
        99: "Tormenta con granizo fuerte",
    },
}

TEXTS = {
    "en": {
        "feels_like": "feels like",
        "humidity": "humidity",
        "wind": "wind",
        "uv": "UV",
        "rain": "rain",
        "rain_chance": "rain chance",
        "forecast": "7-day forecast:",
        "hours": "Next {n} hours:",
        "unknown": "Unknown conditions (code {code})",
        "not_found": "City not found: {city}",
        "several": "Several places match:",
        "population": "pop.",
        "choose": "Choose 1-{n} (Enter = 1): ",
        "invalid": "Invalid choice.",
        "need_tty": "--choose needs an interactive terminal (with Docker, use: docker run -it --rm ...)",
        "connection_error": "Couldn't connect to the weather service. Check your internet connection and try again.",
        "data_error": "Something went wrong while reading the weather data.",
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    },
    "es": {
        "feels_like": "sensación",
        "humidity": "humedad",
        "wind": "viento",
        "uv": "UV",
        "rain": "lluvia",
        "rain_chance": "prob. de lluvia",
        "forecast": "Previsión de 7 días:",
        "hours": "Próximas {n} horas:",
        "unknown": "Condiciones desconocidas (código {code})",
        "not_found": "Ciudad no encontrada: {city}",
        "several": "Varios lugares coinciden:",
        "population": "hab.",
        "choose": "Elige 1-{n} (Intro = 1): ",
        "invalid": "Opción no válida.",
        "need_tty": "--choose necesita una terminal interactiva (con Docker, usa: docker run -it --rm ...)",
        "connection_error": "No se pudo conectar con el servicio del tiempo. Revisa tu conexión a internet e inténtalo de nuevo.",
        "data_error": "Algo salió mal al leer los datos del tiempo.",
        "days": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
        "months": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    },
}

GRAPH_WIDTH = 30

_color_enabled = True


def paint(text, *codes):
    if not _color_enabled:
        return str(text)
    return f"\033[{';'.join(codes)}m{text}\033[0m"


def temp_color(value, units):
    celsius = (value - 32) * 5 / 9 if units == "imperial" else value
    if celsius < 5:
        return "34"
    if celsius < 12:
        return "36"
    if celsius < 20:
        return "32"
    if celsius < 28:
        return "33"
    return "31"


def uv_color(uv):
    if uv < 3:
        return "32"
    if uv < 6:
        return "33"
    if uv < 8:
        return "38;5;208"
    if uv < 11:
        return "31"
    return "35"


def paint_temp(value, units):
    return paint(f"{value}{UNITS[units]['temp']}", temp_color(value, units))


def paint_uv(uv):
    return paint(round(uv, 1), uv_color(uv))


def describe_weather_code(code, lang):
    text = DESCRIPTIONS[lang].get(code)
    if text is None:
        return f"❓ {TEXTS[lang]['unknown'].format(code=code)}"
    return f"{ICONS[code]} {text}"


def format_date(value, lang, with_time=False):
    t = TEXTS[lang]
    moment = datetime.strptime(value, "%Y-%m-%dT%H:%M" if with_time else "%Y-%m-%d")
    day = t["days"][moment.weekday()]
    if with_time:
        return f"{day} {moment:%H:%M}"
    return f"{day} {moment.day:02d} {t['months'][moment.month - 1]}"


def format_place(location):
    parts = [location["name"]]
    region = location.get("admin1")
    if region and region != location["name"]:
        parts.append(region)
    if location.get("country"):
        parts.append(location["country"])
    return ", ".join(parts)


def search_locations(city, lang, count=1):
    resp = requests.get(
        GEOCODE_URL,
        params={"name": city, "count": count, "language": lang},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json().get("results") or []


def choose_location(results, lang):
    if len(results) == 1:
        return results[0]

    t = TEXTS[lang]
    print(t["several"])
    for i, location in enumerate(results, start=1):
        population = location.get("population")
        extra = f" ({t['population']} {population:,})" if population else ""
        print(f"  {i}. {format_place(location)}{extra}")

    while True:
        try:
            answer = input(t["choose"].format(n=len(results))).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)
        if not answer:
            return results[0]
        if answer.isdigit() and 1 <= int(answer) <= len(results):
            return results[int(answer) - 1]
        print(t["invalid"])


def get_weather(lat, lon, units, hours=None):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code,uv_index",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,uv_index_max",
        "forecast_days": 7,
        "timezone": "auto",
        **UNITS[units]["api"],
    }
    if hours:
        params["hourly"] = "weather_code,temperature_2m,precipitation_probability"
        params["forecast_hours"] = hours

    resp = requests.get(FORECAST_URL, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return data["current"], data["daily"], data.get("hourly")


def print_current(location, current, units, lang):
    t = TEXTS[lang]
    u = UNITS[units]
    print(
        f"{paint(format_place(location), '1')}: {paint_temp(current['temperature_2m'], units)} "
        f"({t['feels_like']} {paint_temp(current['apparent_temperature'], units)}), "
        f"{t['humidity']} {current['relative_humidity_2m']}%, "
        f"{t['wind']} {current['wind_speed_10m']} {u['wind']}, "
        f"{t['uv']} {paint_uv(current['uv_index'])}"
    )
    print(describe_weather_code(current["weather_code"], lang))


def print_hourly(hourly, units, lang, graph):
    t = TEXTS[lang]
    temps = hourly["temperature_2m"]
    low, high = min(temps), max(temps)

    print()
    print(paint(t["hours"].format(n=len(hourly["time"])), "1"))
    for i, hour in enumerate(hourly["time"]):
        label = format_date(hour, lang, with_time=True)
        temp = temps[i]
        chance = hourly["precipitation_probability"][i]
        chance_text = f"{chance}%"
        if chance is not None and chance >= 50:
            chance_text = paint(chance_text, "34")

        if graph:
            width = round((temp - low) / (high - low) * (GRAPH_WIDTH - 1)) + 1 if high > low else GRAPH_WIDTH // 2
            bar = paint("█" * width, temp_color(temp, units)) + " " * (GRAPH_WIDTH - width)
            icon = ICONS.get(hourly["weather_code"][i], "❓")
            print(f"  {label} {bar} {paint_temp(temp, units)} {icon} {chance_text}")
        else:
            print(
                f"  {label}: {describe_weather_code(hourly['weather_code'][i], lang)}, "
                f"{paint_temp(temp, units)}, {t['rain_chance']} {chance_text}"
            )


def print_forecast(daily, units, lang):
    t = TEXTS[lang]
    u = UNITS[units]
    print()
    print(paint(t["forecast"], "1"))
    for i, day in enumerate(daily["time"]):
        print(
            f"  {format_date(day, lang)}: {describe_weather_code(daily['weather_code'][i], lang)}, "
            f"{paint_temp(daily['temperature_2m_min'][i], units)} / "
            f"{paint_temp(daily['temperature_2m_max'][i], units)}, "
            f"{t['rain']} {daily['precipitation_sum'][i]} {u['rain']}, "
            f"{t['uv']} {paint_uv(daily['uv_index_max'][i])}"
        )


def hours_arg(value):
    try:
        hours = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number")
    if not 1 <= hours <= 48:
        raise argparse.ArgumentTypeError("must be between 1 and 48")
    return hours


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
    parser.add_argument(
        "-c",
        "--choose",
        action="store_true",
        help="when several places match, list them and choose one (needs an interactive terminal)",
    )
    parser.add_argument(
        "-H",
        "--hours",
        type=hours_arg,
        metavar="N",
        help="also show an hourly forecast for the next N hours (1-48)",
    )
    parser.add_argument(
        "-g",
        "--graph",
        action="store_true",
        help="show the hourly temperature as a bar chart (24 hours unless -H is given)",
    )
    parser.add_argument(
        "-l",
        "--lang",
        choices=sorted(TEXTS),
        default="en",
        help="language of the output: en or es; default: en",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable colors (also disabled when the NO_COLOR environment variable is set)",
    )
    return parser.parse_args()


def main():
    global _color_enabled

    args = parse_args()
    city = " ".join(args.city)
    units = args.units
    lang = args.lang
    t = TEXTS[lang]
    hours = args.hours or (24 if args.graph else None)
    _color_enabled = not (args.no_color or os.environ.get("NO_COLOR"))

    if args.choose and not sys.stdin.isatty():
        print(t["need_tty"])
        return

    try:
        results = search_locations(city, lang, count=10 if args.choose else 1)
        if not results:
            print(t["not_found"].format(city=city))
            return
        location = choose_location(results, lang) if args.choose else results[0]

        current, daily, hourly = get_weather(
            location["latitude"], location["longitude"], units, hours
        )
        print_current(location, current, units, lang)
        if hourly:
            print_hourly(hourly, units, lang, args.graph)
        print_forecast(daily, units, lang)

    except requests.exceptions.RequestException:
        print(t["connection_error"])
    except (KeyError, ValueError):
        print(t["data_error"])


if __name__ == "__main__":
    main()
