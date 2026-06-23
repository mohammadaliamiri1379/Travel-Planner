import httpx


def generate_follow_up_questions(base_url: str, prompt: str, timeout_seconds: float = 25.0) -> dict:

    """Calls the /generate-questions endpoint to get follow-up questions based on the user's initial prompt."""
    # Expected response format:
    # {
    #   "questions": ["What is your budget?", ...],
    #   "irrelevant": false,
    #   "humorous_reply": ""
    # }


    response = httpx.post(
        f"{base_url}/generate-questions",
        json={"prompt": prompt},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, dict) or "questions" not in payload:
        raise TypeError(f"Expected response to be a dict with a 'questions' key, got: {payload}")
    questions = payload.get("questions", [])
    if not isinstance(questions, list):
        raise TypeError(f"Expected 'questions' to be a list, got {type(questions).__name__}")

    return {
        "questions": [str(q) for q in questions],
        "irrelevant": bool(payload.get("irrelevant", False)),
        "humorous_reply": str(payload.get("humorous_reply", "")),
    }



def generate_final_plan(base_url: str, prompt: str, answers: dict) -> dict:
    response = httpx.post(f"{base_url}/generate-itinerary", json={"prompt": prompt, "answers": answers}, timeout=60.0)
    response.raise_for_status()
    payload = response.json()
    return {
        "itinerary": payload.get("itinerary", []),
        "where": payload.get("where", ""),
        "weather": payload.get("weather", []),
        "error": payload.get("error", ""),
    }
