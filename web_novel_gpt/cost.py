from typing import Any, Dict, List

from pydantic import BaseModel, field_validator


class Cost(BaseModel):
    accumulated_cost: float = 0.0
    costs: List[float] = []

    @field_validator("accumulated_cost")
    def validate_accumulated_cost(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Total cost cannot be negative.")
        return value

    def add_cost(self, value: float) -> None:
        if value < 0:
            raise ValueError("Added cost cannot be negative.")
        self.accumulated_cost += value
        self.costs.append(value)

    def get(self) -> Dict[str, Any]:
        return {"accumulated_cost": self.accumulated_cost, "costs": self.costs}

    def log(self) -> str:
        cost = self.get()
        return "\n".join(f"{key}: {value}" for key, value in cost.items())
