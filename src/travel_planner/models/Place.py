from pydantic import BaseModel, Field


class PlaceResult(BaseModel):
	title: str
	address: str
	description: str


class PlacesRequest(BaseModel):
	where: str
	interests: list[str] = Field(default_factory=list)
	duration: str = ""


class PlacesResponse(BaseModel):
	itinerary: list[PlaceResult] = Field(default_factory=list)
