from typing import Literal
from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility", "endurance"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, lt=400)
    goal: Goal
    intensity: Intensity
    @field_validator("name", "user_id")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=2000)

class NutritionResponse(BaseModel):
    tip: str

class DayPlan(BaseModel):
    day: str
    focus: str
    warm_up: str
    exercises: list[str]
    cooldown: str
    recovery: str

class WorkoutResponse(BaseModel):
    title: str
    overview: str
    days: list[DayPlan] = Field(min_length=7, max_length=7)
