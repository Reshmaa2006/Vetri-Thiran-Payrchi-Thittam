from .config import get_settings
from .schemas import NutritionResponse

def _demo_tip(goal: str) -> str:
    tips = {
        "weight loss": "Build meals around vegetables, a protein source, whole-food carbohydrates, and water; avoid extreme calorie restriction.",
        "muscle gain": "Include a protein-rich food in each main meal and pair strength training with adequate sleep and hydration.",
        "general wellness": "Prioritize regular meals, varied whole foods, hydration, and consistent sleep to support everyday wellbeing.",
        "flexibility": "Stay hydrated and include varied whole foods while practicing mobility consistently.",
        "endurance": "Fuel training with balanced carbohydrates and protein, and replace fluids after longer or sweat-heavy sessions.",
    }
    return tips.get(goal, "Choose balanced meals, stay hydrated, and prioritize recovery.")

def generate_nutrition_tip_with_flash(goal: str) -> str:
    settings = get_settings()
    if not settings.gemini_api_key: return _demo_tip(goal)
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f'''Give one concise nutrition or recovery tip for a fitness user whose goal is "{goal}". Keep it practical, non-medical, and under 80 words. Avoid extreme diets or supplement claims.'''
    response = client.models.generate_content(model=settings.tip_model, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=NutritionResponse, temperature=0.4))
    return NutritionResponse.model_validate_json(response.text).tip
