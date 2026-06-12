"""MCP-style tool wrappers around the Open-Meteo geocoding and forecast APIs.

Open-Meteo's free tier needs no API key, so the weather slice works out of
the box without any .env changes.
"""

import httpx

OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes used by Open-Meteo, mapped to a short emoji label.
WEATHER_CODES: dict[int, str] = {
	0: "☀️ Clear sky",
	1: "🌤️ Mostly clear",
	2: "⛅ Partly cloudy",
	3: "☁️ Overcast",
	45: "🌫️ Foggy",
	48: "🌫️ Foggy",
	51: "🌦️ Light drizzle",
	53: "🌦️ Drizzle",
	55: "🌦️ Heavy drizzle",
	56: "🌧️ Freezing drizzle",
	57: "🌧️ Freezing drizzle",
	61: "🌧️ Light rain",
	63: "🌧️ Rain",
	65: "🌧️ Heavy rain",
	66: "🌧️ Freezing rain",
	67: "🌧️ Freezing rain",
	71: "❄️ Light snow",
	73: "❄️ Snow",
	75: "❄️ Heavy snow",
	77: "❄️ Snow grains",
	80: "🌦️ Rain showers",
	81: "🌦️ Rain showers",
	82: "🌧️ Violent rain showers",
	85: "🌨️ Snow showers",
	86: "🌨️ Snow showers",
	95: "⛈️ Thunderstorm",
	96: "⛈️ Thunderstorm with hail",
	99: "⛈️ Thunderstorm with hail",
}


def describe_weather_code(code: int | None) -> str:
	"""Tool helper: turn a WMO weather code into a short emoji label."""
	return WEATHER_CODES.get(code, "🌡️ Weather")


async def geocode_city(city: str) -> tuple[float, float]:
	"""Tool: geocode_city - resolve a city name to (latitude, longitude) via Open-Meteo."""
	async with httpx.AsyncClient() as client:
		response = await client.get(
			OPEN_METEO_GEOCODING_URL,
			params={"name": city, "count": 1},
			timeout=10.0,
		)
	response.raise_for_status()
	results = response.json().get("results") or []
	if not results:
		raise ValueError(f"No geocoding results for city: {city!r}")

	first = results[0]
	return float(first["latitude"]), float(first["longitude"])


async def get_daily_forecast(lat: float, lon: float, start_date: str, end_date: str) -> dict:
	"""Tool: get_daily_forecast - fetch daily high/low/precipitation/weather code for a date range.

	Returns Open-Meteo's "daily" block: a dict of parallel arrays keyed by
	"time", "temperature_2m_max", "temperature_2m_min",
	"precipitation_probability_max" and "weathercode".
	"""
	async with httpx.AsyncClient() as client:
		response = await client.get(
			OPEN_METEO_FORECAST_URL,
			params={
				"latitude": lat,
				"longitude": lon,
				"daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
				"timezone": "auto",
				"start_date": start_date,
				"end_date": end_date,
			},
			timeout=10.0,
		)
	response.raise_for_status()
	return response.json().get("daily", {})
