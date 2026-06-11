import os

AGENT_REGISTRY: dict[str, str] = {
	"places": os.getenv("PLACES_AGENT_URL", "http://127.0.0.1:8001"),
}


def get_agent_url(name: str) -> str:
	try:
		return AGENT_REGISTRY[name]
	except KeyError:
		raise KeyError(f"Unknown agent: {name!r}. Registered agents: {list(AGENT_REGISTRY)}") from None
