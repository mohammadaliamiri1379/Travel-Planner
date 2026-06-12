import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml
from dateutil import parser as date_parser
from dotenv import load_dotenv
from fastapi import FastAPI
from groq import AsyncGroq

from travel_planner.mcp_tools.geoapify import (
	categories_for_interests,
	describe_categories,
	extract_coordinates,
	geocode_city,
	most_specific_category,
	search_places_diverse,
)
from travel_planner.models.Place import PlaceResult, PlacesRequest, PlacesResponse

app = FastAPI(title="places-agent")

TIME_SLOTS = ["09:00 AM", "12:30 PM", "03:00 PM", "06:30 PM", "09:00 PM"]
MEAL_SLOT_INDEXES = {1, 3}
NIGHTLIFE_SLOT_INDEX = 4
NIGHTLIFE_PREFIXES = ("catering.bar", "adult.nightclub")
MAX_SCHEDULED_DAYS = 14

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")
with open(BASE_DIR / "prompts.yaml", "r", encoding="utf-8") as f:
	PROMPTS = yaml.safe_load(f)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DESCRIPTION_MODEL = "llama-3.3-70b-versatile"
_groq_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


@app.get("/.well-known/agent-card.json")
async def agent_card() -> dict:
	return {
		"name": "places-agent",
		"description": "Recommends points of interest for a destination using Geoapify.",
		"skills": [
			{
				"id": "recommend_places",
				"description": "Given a destination, interests and trip duration, return recommended places to visit.",
			}
		],
	}


def _parse_duration_days(duration: str) -> int:
	match = re.search(r"\d+", duration)
	days = int(match.group()) if match else 3
	return max(1, min(days, MAX_SCHEDULED_DAYS))


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


def _feature_to_place(feature: dict) -> PlaceResult:
	properties = feature.get("properties", {})
	title = properties.get("name") or properties.get("address_line1") or "Unnamed place"
	address = properties.get("formatted", "")
	categories = properties.get("categories", [])
	description = describe_categories(categories)
	lat, lon = extract_coordinates(feature)
	return PlaceResult(
		title=title,
		address=address,
		description=description,
		category=most_specific_category(categories),
		lat=lat,
		lon=lon,
	)


def _schedule_itinerary(places: list[PlaceResult], num_days: int, start_date: date | None) -> list[PlaceResult]:
	"""Spread places across the trip's days and assign approximate dates/times.

	Meal-time slots are filled from food/drink places first so cafes and
	restaurants land at lunch/dinner rather than alongside sightseeing. Bars
	and nightclubs are held back for the evening slot so nobody gets sent to
	a club at 9am.
	"""
	nightlife = [p for p in places if p.category.startswith(NIGHTLIFE_PREFIXES)]
	food = [p for p in places if p.category.startswith("catering.") and not p.category.startswith(NIGHTLIFE_PREFIXES)]
	other = [p for p in places if not p.category.startswith("catering.") and not p.category.startswith(NIGHTLIFE_PREFIXES)]

	scheduled: list[PlaceResult] = []
	food_iter = iter(food)
	other_iter = iter(other)
	nightlife_iter = iter(nightlife)

	for day_offset in range(num_days):
		day_number = day_offset + 1
		day_date = start_date + timedelta(days=day_offset) if start_date else None
		date_label = day_date.strftime("%a, %b %d") if day_date else ""
		date_iso = day_date.isoformat() if day_date else ""

		exhausted = True
		for slot_index, time_label in enumerate(TIME_SLOTS):
			if slot_index == NIGHTLIFE_SLOT_INDEX:
				place = next(nightlife_iter, None)
			elif slot_index in MEAL_SLOT_INDEXES:
				place = next(food_iter, None) or next(other_iter, None)
			else:
				place = next(other_iter, None) or next(food_iter, None)
			if place is None:
				continue
			exhausted = False
			place.day = day_number
			place.date = date_label
			place.date_iso = date_iso
			place.time = time_label
			scheduled.append(place)

		if exhausted:
			break

	return scheduled


async def _enrich_descriptions(places: list[PlaceResult], city: str) -> None:
	"""Ask the LLM for a short, specific description of each place, in place.

	Falls back silently to the existing category-based description (set in
	_feature_to_place) if the LLM call or response parsing fails.
	"""
	if not _groq_client or not places:
		return

	places_text = "\n".join(
		f"{i + 1}. {place.title} (category: {place.category or 'unknown'})"
		for i, place in enumerate(places)
	)
	prompt = (
		PROMPTS["place_descriptions_agent"]["content"]
		.replace("{{$city}}", city)
		.replace("{{$places}}", places_text)
	)

	try:
		response = await _groq_client.chat.completions.create(
			model=DESCRIPTION_MODEL,
			messages=[
				{"role": "system", "content": PROMPTS["system_rules"]["content"]},
				{"role": "user", "content": prompt},
			],
			response_format={"type": "json_object"},
			temperature=0.85,
		)
		descriptions = json.loads(response.choices[0].message.content or "{}").get("descriptions", [])
	except Exception as e:
		print(f"places-agent: description enrichment failed: {e}")
		return

	for place, description in zip(places, descriptions):
		if isinstance(description, str) and description.strip():
			place.description = description.strip()


@app.post("/recommend")
async def recommend(request: PlacesRequest) -> PlacesResponse:
	try:
		lat, lon = await geocode_city(request.where)
		categories = categories_for_interests(request.interests)

		num_days = _parse_duration_days(request.duration)
		target_count = min(num_days * len(TIME_SLOTS), MAX_SCHEDULED_DAYS * len(TIME_SLOTS))
		per_category_limit = max(4, -(-target_count // max(len(categories), 1)))

		features = await search_places_diverse(
			lat, lon, categories, per_category_limit=per_category_limit, total_limit=target_count
		)
	except Exception as e:
		print(f"places-agent: recommend failed: {e}")
		return PlacesResponse(itinerary=[])

	places = [_feature_to_place(feature) for feature in features]
	start_date = _parse_start_date(request.when)
	itinerary = _schedule_itinerary(places, num_days, start_date)
	await _enrich_descriptions(itinerary, request.where)
	return PlacesResponse(itinerary=itinerary)
