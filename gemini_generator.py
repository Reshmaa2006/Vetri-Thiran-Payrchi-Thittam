import json
from .config import get_settings
from .schemas import UserInput, WorkoutResponse

def _demo_workout(data: UserInput) -> str:
    focuses = ["Full Body", "Upper Body", "Cardio", "Lower Body", "Core + Mobility", "Active Recovery", "Rest + Stretching"]
    days = []
    for i, focus in enumerate(focuses, 1):
        exercises = ["Bodyweight squat – 3 x 10–12", "Push-up or incline push-up – 3 x 8–12", "Glute bridge – 3 x 12–15", "Plank – 3 x 20–40 sec"]
        if focus == "Cardio": exercises = ["Brisk walk/jog – 20–30 min", "Cycling or step-ups – 10–15 min", "Plank – 3 x 20–30 sec"]
        if focus == "Active Recovery": exercises = ["Brisk walk – 20–30 min", "Mobility flow – 10 min", "Easy core work – 2 sets"]
        if focus == "Rest + Stretching": exercises = ["Easy walking – 15–20 min", "Gentle full-body stretching – 10 min"]
        days.append({"day": f"Day {i}", "focus": focus, "warm_up": "5–10 minutes of easy movement and dynamic mobility.", "exercises": exercises, "cooldown": "5 minutes of easy walking and gentle stretching.", "recovery": "Hydrate and stop if you experience pain, dizziness, or unusual symptoms."})
    return json.dumps({"title": f"7-Day {data.goal.title()} Plan", "overview": f"Demo plan for {data.name}; goal={data.goal}, intensity={data.intensity}.", "days": days, "source": "local-demo-fallback"}, indent=2)

def generate_workout_gemini(data: UserInput) -> str:
    settings = get_settings()
    if not settings.gemini_api_key: return _demo_workout(data)
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f'''Create a safe, practical 7-day beginner-to-intermediate fitness plan.
User: name={data.name}, age={data.age}, weight={data.weight} kg, goal={data.goal}, intensity={data.intensity}.
Return exactly 7 days. Each day needs focus, warm-up, exercises with sets/reps or duration, cooldown and recovery. Match difficulty to intensity. Include rest or active recovery where appropriate. Do not diagnose or prescribe medical treatment. Include a brief safety reminder.'''
    response = client.models.generate_content(model=settings.workout_model, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=WorkoutResponse, temperature=0.4))
    return json.dumps(WorkoutResponse.model_validate_json(response.text).model_dump(), indent=2)
