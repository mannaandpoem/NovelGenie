import json
import re
from typing import Any, Dict, Tuple


def save_output(content: str, file_path: str) -> None:
    """Save content to specified file path."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def json_parse(response: str) -> str:
    """
    Extract JSON string from LLM response.

    Args:
        response (str): Raw response from LLM

    Returns:
        str: Cleaned JSON string
    """
    # Try to find JSON pattern in the response
    json_pattern = r"\{[\s\S]*\}"
    match = re.search(json_pattern, response)

    if match:
        return match.group()
    return response


def parse_intent(response: str) -> Tuple[str, str, int, int]:
    """
    Parse intent analysis response and extract components.

    Args:
        response (str): Response string from intent analysis

    Returns:
        Tuple[str, str, str]: (description, genre, word_count)
    """
    intent = json_parse(response)
    intent_json = json.loads(intent)
    return (
        intent_json.get("description"),
        intent_json.get("genre"),
        intent_json.get("word_count"),
        intent_json.get("volume_count"),
    )


class Cost:
    def __init__(self) -> None:
        self._accumulated_cost: float = 0.0
        self._costs: list[float] = []

    @property
    def accumulated_cost(self) -> float:
        return self._accumulated_cost

    @accumulated_cost.setter
    def accumulated_cost(self, value: float) -> None:
        if value < 0:
            raise ValueError("Total cost cannot be negative.")
        self._accumulated_cost = value

    @property
    def costs(self) -> list:
        return self._costs

    def add_cost(self, value: float) -> None:
        if value < 0:
            raise ValueError("Added cost cannot be negative.")
        self._accumulated_cost += value
        self._costs.append(value)

    def get(self) -> Dict[str, Any]:
        return {"accumulated_cost": self._accumulated_cost, "costs": self._costs}

    def log(self) -> str:
        cost = self.get()
        return "\n".join(f"{key}: {value}" for key, value in cost.items())
