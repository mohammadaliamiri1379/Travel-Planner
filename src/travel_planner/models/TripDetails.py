from pydantic import BaseModel, Field

class TripDetailsResult(BaseModel):
	has_required_information: bool
	when: str = ""
	where: str = ""
	interests: list[str] = Field(default_factory=list)
	duration: str = ""