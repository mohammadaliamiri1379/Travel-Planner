import json
from pydantic import BaseModel, Field


def _load_json(raw_output: str) -> Any:
	return json.loads(raw_output)


def _result_to_text(result: Any) -> str:
	value = getattr(result, "value", result)
	if hasattr(value, "content") and isinstance(getattr(value, "content"), str):
		return getattr(value, "content")
	if hasattr(value, "to_prompt"):
		return value.to_prompt()
	if isinstance(value, list):
		pieces: list[str] = []
		for item in value:
			if hasattr(item, "content") and isinstance(getattr(item, "content"), str):
				pieces.append(getattr(item, "content"))
			elif hasattr(item, "items"):
				inner_texts: list[str] = []
				for inner_item in getattr(item, "items", []):
					text = getattr(inner_item, "text", None)
					if isinstance(text, str) and text.strip():
						inner_texts.append(text)
				if inner_texts:
					pieces.append("\n".join(inner_texts))
			elif hasattr(item, "to_prompt"):
				pieces.append(item.to_prompt())
			else:
				pieces.append(str(item))
		return "\n".join(pieces)
	if isinstance(value, str):
		return value
	if isinstance(value, (dict, list)):
		return json.dumps(value)
	return str(value)
