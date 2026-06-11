from fastapi import FastAPI

from travel_planner.mcp_tools.geoapify import categories_for_interests, geocode_city, search_places
from travel_planner.models.Place import PlaceResult, PlacesRequest, PlacesResponse

app = FastAPI(title="places-agent")


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


def _feature_to_place(feature: dict) -> PlaceResult:
	properties = feature.get("properties", {})
	title = properties.get("name") or properties.get("address_line1") or "Unnamed place"
	address = properties.get("formatted", "")
	categories = properties.get("categories", [])
	description = f"Categories: {', '.join(categories)}" if categories else "A recommended point of interest."
	return PlaceResult(title=title, address=address, description=description)


@app.post("/recommend")
async def recommend(request: PlacesRequest) -> PlacesResponse:
	try:
		lat, lon = await geocode_city(request.where)
		categories = categories_for_interests(request.interests)
		features = await search_places(lat, lon, categories)
	except Exception as e:
		print(f"places-agent: recommend failed: {e}")
		return PlacesResponse(itinerary=[])

	return PlacesResponse(itinerary=[_feature_to_place(feature) for feature in features])
