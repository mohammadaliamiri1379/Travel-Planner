from typing import ClassVar
from pydantic import BaseModel, Field

class MissingInformationResult(BaseModel):
	does_have_all_information: bool
	missing_information: list[str] = Field(default_factory=list)
