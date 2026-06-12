"""MCP-style tool wrappers around the Geoapify Geocoding and Places APIs."""

import asyncio
import os
from itertools import zip_longest
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
GEOAPIFY_BASE_URL = "https://api.geoapify.com"

INTEREST_CATEGORY_MAP: dict[str, list[str]] = {
	"food": ["catering.restaurant", "catering.cafe"],
	"restaurant": ["catering.restaurant"],
	"restaurants": ["catering.restaurant"],
	"coffee": ["catering.cafe"],
	"cafe": ["catering.cafe"],
	"cafes": ["catering.cafe"],
	"gelato": ["catering.ice_cream"],
	"ice cream": ["catering.ice_cream"],
	"dessert": ["catering.ice_cream", "catering.cafe"],
	"art": ["entertainment.museum", "entertainment.culture"],
	"museum": ["entertainment.museum"],
	"museums": ["entertainment.museum"],
	"gallery": ["entertainment.culture"],
	"galleries": ["entertainment.culture"],
	"culture": ["entertainment.culture"],
	"nature": ["leisure.park", "natural"],
	"park": ["leisure.park"],
	"parks": ["leisure.park"],
	"shopping": ["commercial.shopping_mall"],
	"nightlife": ["catering.bar", "entertainment.nightclub"],
	"bar": ["catering.bar"],
	"bars": ["catering.bar"],
	"history": ["tourism.sights", "entertainment.culture"],
	"landmark": ["tourism.sights"],
	"landmarks": ["tourism.sights"],
	"sightseeing": ["tourism.sights", "tourism.attraction"],
}
DEFAULT_CATEGORIES = ["tourism.sights", "tourism.attraction"]

CATEGORY_LABELS: dict[str, str] = {
	"tourism.attraction.artwork.sculpture": "Sculpture",
	"tourism.attraction.artwork.statue": "Statue",
	"tourism.attraction.artwork": "Artwork",
	"tourism.sights.memorial": "Memorial",
	"tourism.sights.square": "Square",
	"tourism.sights": "Landmark",
	"tourism.attraction": "Tourist attraction",
	"entertainment.museum": "Museum",
	"entertainment.culture": "Cultural venue",
	"catering.restaurant": "Restaurant",
	"catering.cafe.dessert": "Dessert café",
	"catering.cafe": "Café",
	"catering.ice_cream": "Gelato spot",
	"catering.bar": "Bar",
	"leisure.park": "Park",
	"natural": "Natural landmark",
	"commercial.shopping_mall": "Shopping mall",
	"building.public_and_civil": "Landmark",
}

# Prefixes that describe metadata (accessibility, amenities, etc.) rather than
# what kind of place this is - never pick these as the "most specific" category.
NON_DESCRIPTIVE_PREFIXES = ("wheelchair", "internet_access")


def extract_coordinates(feature: dict) -> tuple[float | None, float | None]:
	"""Pull (lat, lon) out of a Geoapify Places feature, if present."""
	properties = feature.get("properties", {})
	lat = properties.get("lat")
	lon = properties.get("lon")
	if lat is not None and lon is not None:
		return float(lat), float(lon)

	coordinates = feature.get("geometry", {}).get("coordinates")
	if coordinates and len(coordinates) == 2:
		lon, lat = coordinates
		return float(lat), float(lon)

	return None, None


def most_specific_category(categories: list[str]) -> str:
	"""Return the most specific (longest) Geoapify category code in a list."""
	descriptive = [c for c in categories if not c.startswith(NON_DESCRIPTIVE_PREFIXES)]
	return max(descriptive, key=len, default="")


def describe_categories(categories: list[str]) -> str:
	"""Turn Geoapify category codes into a short human-readable description."""
	label = CATEGORY_LABELS.get(most_specific_category(categories), "Point of interest")
	return f"{label} recommended near your destination."


def _interest_categories(interest: str) -> list[str]:
	"""Look up Geoapify categories for a single interest, tolerating simple singular/plural variants."""
	key = interest.strip().lower()
	if key in INTEREST_CATEGORY_MAP:
		return INTEREST_CATEGORY_MAP[key]
	if key.endswith("s") and key[:-1] in INTEREST_CATEGORY_MAP:
		return INTEREST_CATEGORY_MAP[key[:-1]]
	if f"{key}s" in INTEREST_CATEGORY_MAP:
		return INTEREST_CATEGORY_MAP[f"{key}s"]
	return []


def categories_for_interests(interests: list[str]) -> list[str]:
	"""Map free-form interests (e.g. "food", "art") to Geoapify category strings."""
	categories: list[str] = []
	for interest in interests:
		for category in _interest_categories(interest):
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


async def search_places_diverse(
	lat: float, lon: float, categories: list[str], per_category_limit: int = 4, total_limit: int = 10
) -> list[dict]:
	"""Tool: search_places_diverse - search each category separately and interleave the results.

	Avoids the single most popular spot (e.g. one busy square) dominating the results.
	"""
	results = await asyncio.gather(
		*(search_places(lat, lon, [category], limit=per_category_limit) for category in categories)
	)

	seen_names: set[str] = set()
	merged: list[dict] = []
	for batch in zip_longest(*results, fillvalue=None):
		for feature in batch:
			if feature is None or len(merged) >= total_limit:
				continue
			name = feature.get("properties", {}).get("name", "")
			if name and name.lower() in seen_names:
				continue
			seen_names.add(name.lower())
			merged.append(feature)
	return merged


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
		{
			"name": "search_places_diverse",
			"description": "Search multiple categories and interleave the results for variety.",
			"input_schema": {"lat": "float", "lon": "float", "categories": "list[str]"},
		},
	]
