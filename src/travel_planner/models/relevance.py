
from pydantic import BaseModel, Field

class RelevanceResult(BaseModel):
	relevant: bool
	humorous_reply: str = ""
	summary: str = ""
	user_input: str = ""
	# questions_already_asked: bool = False
