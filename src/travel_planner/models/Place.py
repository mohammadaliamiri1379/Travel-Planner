from pydantic import BaseModel, Field


class PlaceResult(BaseModel):
	title: str
	address: str
	description: str
	category: str = ""
	lat: float | None = None
	lon: float | None = None
	day: int = 1
	date: str = ""
	date_iso: str = ""
	time: str = ""


class PlacesRequest(BaseModel):
	where: str
	when: str = ""
	interests: list[str] = Field(default_factory=list)
	duration: str = ""


class PlacesResponse(BaseModel):
	itinerary: list[PlaceResult] = Field(default_factory=list)
	error: str = ""
