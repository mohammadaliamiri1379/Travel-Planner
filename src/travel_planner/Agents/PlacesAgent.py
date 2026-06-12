import re
from datetime import date, datetime, timedelta

from dateutil import parser as date_parser
from fastapi import FastAPI

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

TIME_SLOTS = ["09:00 AM", "12:30 PM", "03:00 PM", "06:30 PM"]
MEAL_SLOT_INDEXES = {1, 3}
MAX_SCHEDULED_DAYS = 14


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
		return date_parser.parse(when, fuzzy=True, default=datetime.now()).date()
	except (ValueError, OverflowError):
		return None


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
	restaurants land at lunch/dinner rather than alongside sightseeing.
	"""
	food = [p for p in places if p.category.startswith("catering.")]
	other = [p for p in places if not p.category.startswith("catering.")]

	scheduled: list[PlaceResult] = []
	food_iter = iter(food)
	other_iter = iter(other)

	for day_offset in range(num_days):
		day_number = day_offset + 1
		if start_date:
			date_label = (start_date + timedelta(days=day_offset)).strftime("%a, %b %d")
		else:
			date_label = f"Day {day_number}"

		exhausted = True
		for slot_index, time_label in enumerate(TIME_SLOTS):
			is_meal_slot = slot_index in MEAL_SLOT_INDEXES
			primary, fallback = (food_iter, other_iter) if is_meal_slot else (other_iter, food_iter)
			place = next(primary, None) or next(fallback, None)
			if place is None:
				continue
			exhausted = False
			place.day = day_number
			place.date = date_label
			place.time = time_label
			scheduled.append(place)

		if exhausted:
			break

	return scheduled


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
	return PlacesResponse(itinerary=itinerary)
