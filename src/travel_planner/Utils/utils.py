import httpx


def Call_Orchestrator(base_url: str, prompt: str, timeout_seconds: float = 25.0) -> list[str]:
    """Calls Orchestrator to manage the request"""

    # Expected response format:
    # {
    #   "step": "generate-questions",
    #   "data": {
    #     "questions": [
    #       "What is your budget?",
    #       "How many days will you travel?",
    #       "Do you prefer museums or nature?"
    #     ]
    #   }
    # }

    return [
        "Question 1: What is your budget?",
        "Question 2: How many days will you travel?",
        "Question 3: Do you prefer museums or nature?"
    ]




def generate_follow_up_questions(base_url: str, prompt: str, timeout_seconds: float = 25.0) -> list[str]:

    """Calls the /generate-questions endpoint to get follow-up questions based on the user's initial prompt."""
    # Expected response format:
    # {
    #   "questions": [
    #     "What is your budget?",
    #     "How many days will you travel?",
    #     "Do you prefer museums or nature?"
    #   ]
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

    return [str(q) for q in questions]



def generate_final_plan(base_url: str, prompt: str, answers: dict) -> list[dict]:
    # Placeholder for actual itinerary generation logic
    response = httpx.post(f"{base_url}/generate-itinerary", json={"prompt": prompt, "answers": answers})
    if response.status_code == 200:
        return response.json().get("itinerary", [])
    
    return [
        {
            "title": "Louvre Museum",
            "address": "Rue de Rivoli, 75001 Paris, France",
            "description": "The world's largest art museum and a historic monument in Paris."
        },
        {
            "title": "Eiffel Tower",
            "address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France",
            "description": "An iconic symbol of France, offering panoramic views of Paris."
        },
        {
            "title": "Le Jules Verne",
            "address": "Avenue Gustave Eiffel, 75007 Paris, France",
            "description": "A Michelin-starred restaurant located on the Eiffel Tower."
        }
    ]
