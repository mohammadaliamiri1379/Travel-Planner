import re
from datetime import date, datetime, timedelta

from dateutil import parser as date_parser
from fastapi import FastAPI

from travel_planner.mcp_tools.weather import describe_weather_code, geocode_city, get_daily_forecast
from travel_planner.models.Weather import DayWeather, WeatherRequest, WeatherResponse

app = FastAPI(title="weather-agent")

# Open-Meteo's free forecast covers at most 16 days ahead.
MAX_FORECAST_DAYS = 16


@app.get("/.well-known/agent-card.json")
async def agent_card() -> dict:
	return {
		"name": "weather-agent",
		"description": "Provides a daily weather forecast for a destination using Open-Meteo.",
		"skills": [
			{
				"id": "forecast_weather",
				"description": "Given a destination, start date and trip duration, return a per-day weather forecast.",
			}
		],
	}


def _parse_duration_days(duration: str) -> int:
	match = re.search(r"\d+", duration)
	return int(match.group()) if match else 3


def _parse_start_date(when: str) -> date | None:
	if not when:
		return None
	try:
		parsed = date_parser.parse(when, fuzzy=True, default=datetime.now()).date()
	except (ValueError, OverflowError):
		return None

	# dateutil's fuzzy parser sometimes reads a day-of-month (e.g. the "16" in
	# "June 15-16") as a 2-digit year, landing the date in the past. Snap it
	# forward to this year (or next) - trip dates are never meant to be in the past.
	today = date.today()
	if parsed < today:
		try:
			parsed = parsed.replace(year=today.year)
		except ValueError:
			parsed = parsed.replace(year=today.year, day=28)
		if parsed < today:
			parsed = parsed.replace(year=today.year + 1)
	return parsed


@app.post("/forecast")
async def forecast(request: WeatherRequest) -> WeatherResponse:
	today = date.today()
	start_date = _parse_start_date(request.when) or today
	if start_date < today:
		start_date = today

	num_days = max(1, min(_parse_duration_days(request.duration), MAX_FORECAST_DAYS))
	end_date = start_date + timedelta(days=num_days - 1)

	if (end_date - today).days >= MAX_FORECAST_DAYS:
		# Beyond Open-Meteo's free forecast range - no reliable data to show.
		return WeatherResponse(forecast=[])

	try:
		lat, lon = await geocode_city(request.where)
		daily = await get_daily_forecast(lat, lon, start_date.isoformat(), end_date.isoformat())
	except Exception as e:
		print(f"weather-agent: forecast failed: {e}")
		return WeatherResponse(forecast=[])

	times = daily.get("time", [])
	highs = daily.get("temperature_2m_max", [])
	lows = daily.get("temperature_2m_min", [])
	precipitation = daily.get("precipitation_probability_max", [])
	codes = daily.get("weathercode", [])

	forecast_days = [
		DayWeather(
			day=i + 1,
			date=datetime.fromisoformat(times[i]).strftime("%a, %b %d"),
			condition=describe_weather_code(codes[i] if i < len(codes) else None),
			temp_high_c=highs[i] if i < len(highs) else None,
			temp_low_c=lows[i] if i < len(lows) else None,
			precipitation_chance=precipitation[i] if i < len(precipitation) else None,
		)
		for i in range(len(times))
	]
	return WeatherResponse(forecast=forecast_days)
