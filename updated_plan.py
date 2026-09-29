import json
from .config import get_settings
from .schemas import WorkoutResponse

def update_workout_plan(original_plan: str, feedback: str) -> str:
    settings = get_settings()
    if not settings.gemini_api_key:
        try:
            data = json.loads(original_plan)
            data["overview"] = data.get("overview", "") + f" Updated using demo feedback: {feedback.strip()}"
            data["source"] = "local-demo-fallback"
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            return original_plan + f"\n\nFeedback requested: {feedback.strip()}"
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f'''Revise this 7-day workout plan according to the user's feedback.
Original plan:
{original_plan}
Feedback:
{feedback}
Return exactly 7 days with focus, warm-up, exercises, cooldown and recovery. Apply feedback where practical and keep the plan safe and non-medical.'''
    response = client.models.generate_content(model=settings.workout_model, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=WorkoutResponse, temperature=0.4))
    return json.dumps(WorkoutResponse.model_validate_json(response.text).model_dump(), indent=2)
