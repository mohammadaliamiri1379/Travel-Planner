from pydantic import BaseModel, Field

class FollowUpQuestionsResult(BaseModel):
	questions: list[str] = Field(default_factory=list)
