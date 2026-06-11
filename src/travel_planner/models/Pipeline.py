from pydantic import BaseModel, Field
from typing import Any, Literal

class PipelineResult(BaseModel):
	stage: Literal["irrelevant", "needs_info", "ready"]
	user_input: str = ""
	relevant: bool
	humorous_reply: str = ""
	has_required_information: bool = False
	missing_information: list[str] = Field(default_factory=list)
	questions: list[str] = Field(default_factory=list)
	trip_data: dict[str, Any] = Field(default_factory=dict)
	itinerary: list[dict[str, Any]] = Field(default_factory=list)
	next_step_hint: str = ""