from fastapi import FastAPI
from pydantic import BaseModel, Field

from travel_planner.Agents.Orchestrator import TravelAgentOrchestrator

app = FastAPI(title="travel-planner-gateway")
orchestrator = TravelAgentOrchestrator()


class GenerateQuestionsRequest(BaseModel):
	prompt: str


class GenerateItineraryRequest(BaseModel):
	prompt: str
	answers: dict[str, str] = Field(default_factory=dict)


@app.post("/generate-questions")
async def generate_questions(request: GenerateQuestionsRequest) -> dict:
	result = await orchestrator.run(request.prompt)
	if result["stage"] == "irrelevant":
		return {"questions": [], "irrelevant": True, "humorous_reply": result.get("humorous_reply", "")}
	if result["stage"] == "needs_info":
		return {"questions": result["questions"], "irrelevant": False, "humorous_reply": ""}
	return {"questions": [], "irrelevant": False, "humorous_reply": ""}


@app.post("/generate-itinerary")
async def generate_itinerary(request: GenerateItineraryRequest) -> dict:
	combined_input = request.prompt
	if request.answers:
		details = "\n".join(f"- {question}: {answer}" for question, answer in request.answers.items())
		combined_input += f"\n\nAdditional details:\n{details}"
		result = await orchestrator.run_ready(combined_input)
	else:
		result = await orchestrator.run(combined_input)

	return {
		"itinerary": result.get("itinerary", []),
		"where": result.get("trip_data", {}).get("where", ""),
		"weather": result.get("weather", []),
		"error": result.get("error", ""),
	}
