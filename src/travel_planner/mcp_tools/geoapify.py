"""MCP-style tool wrappers around the Geoapify Geocoding and Places APIs."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
GEOAPIFY_BASE_URL = "https://api.geoapify.com"

INTEREST_CATEGORY_MAP: dict[str, list[str]] = {
	"food": ["catering.restaurant", "catering.cafe"],
	"restaurants": ["catering.restaurant"],
	"art": ["entertainment.museum", "entertainment.culture"],
	"museums": ["entertainment.museum"],
	"culture": ["entertainment.culture"],
	"nature": ["leisure.park", "natural"],
	"parks": ["leisure.park"],
	"shopping": ["commercial.shopping_mall"],
	"nightlife": ["catering.bar", "entertainment.nightclub"],
	"history": ["tourism.sights", "entertainment.culture"],
}
DEFAULT_CATEGORIES = ["tourism.sights", "tourism.attraction"]


def categories_for_interests(interests: list[str]) -> list[str]:
	"""Map free-form interests (e.g. "food", "art") to Geoapify category strings."""
	categories: list[str] = []
	for interest in interests:
		for category in INTEREST_CATEGORY_MAP.get(interest.strip().lower(), []):
			if category not in categories:
				categories.append(category)
	return categories or DEFAULT_CATEGORIES


async def geocode_city(city: str) -> tuple[float, float]:
	"""Tool: geocode_city - resolve a city name to (latitude, longitude)."""
	if not GEOAPIFY_API_KEY:
		raise RuntimeError("GEOAPIFY_API_KEY is missing")

	async with httpx.AsyncClient() as client:
		response = await client.get(
			f"{GEOAPIFY_BASE_URL}/v1/geocode/search",
			params={"text": city, "format": "json", "apiKey": GEOAPIFY_API_KEY},
			timeout=10.0,
		)
	response.raise_for_status()
	results = response.json().get("results", [])
	if not results:
		raise ValueError(f"No geocoding results for city: {city!r}")

	first = results[0]
	return float(first["lat"]), float(first["lon"])


async def search_places(lat: float, lon: float, categories: list[str], limit: int = 10) -> list[dict]:
	"""Tool: search_places - find points of interest near a location."""
	if not GEOAPIFY_API_KEY:
		raise RuntimeError("GEOAPIFY_API_KEY is missing")

	async with httpx.AsyncClient() as client:
		response = await client.get(
			f"{GEOAPIFY_BASE_URL}/v2/places",
			params={
				"categories": ",".join(categories),
				"filter": f"circle:{lon},{lat},5000",
				"bias": f"proximity:{lon},{lat}",
				"limit": limit,
				"apiKey": GEOAPIFY_API_KEY,
			},
			timeout=10.0,
		)
	response.raise_for_status()
	return response.json().get("features", [])


def list_tools() -> list[dict]:
	"""Mirror an MCP server's tools/list response for this tool module."""
	return [
		{
			"name": "geocode_city",
			"description": "Resolve a city name to (latitude, longitude).",
			"input_schema": {"city": "str"},
		},
		{
			"name": "search_places",
			"description": "Find points of interest near a location, filtered by category.",
			"input_schema": {"lat": "float", "lon": "float", "categories": "list[str]", "limit": "int"},
		},
	]
