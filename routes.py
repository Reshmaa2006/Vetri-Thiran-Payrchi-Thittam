import json
from pathlib import Path
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, UserInput
from .services import delete_user, get_all_plans, get_all_users, get_plan, get_user, save_plan, save_user, update_plan
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

def _safe_json(value: str) -> str:
    try: return json.dumps(json.loads(value), indent=2)
    except Exception: return value

def _check_admin(request: Request):
    key = get_settings().admin_key
    if key and request.query_params.get("admin_key") != key: raise HTTPException(403, "Invalid admin key")

@router.get("/", response_class=HTMLResponse)
def home(request: Request): return templates.TemplateResponse(request=request, name="index.html", context={})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(request: Request, name: str = Form(...), user_id: str = Form(...), age: int = Form(...), weight: float = Form(...), goal: str = Form(...), intensity: str = Form(...), db: Session = Depends(get_db)):
    try:
        data = UserInput(name=name, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
        user = save_user(db, data)
        workout = generate_workout_gemini(data)
        tip = generate_nutrition_tip_with_flash(data.goal)
        save_plan(db, user.user_id, workout, tip)
        return templates.TemplateResponse(request=request, name="result.html", context={"user": user, "workout_plan": _safe_json(workout), "nutrition_tip": tip, "updated_plan": None, "message": None})
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="error.html", context={"message": f"Could not generate the plan: {exc}"}, status_code=500)

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: str = Form(...), feedback: str = Form(...), db: Session = Depends(get_db)):
    try:
        payload = FeedbackRequest(user_id=user_id, feedback=feedback)
        user, plan = get_user(db, payload.user_id), get_plan(db, payload.user_id)
        if not user or not plan: raise HTTPException(404, "User or workout plan not found")
        revised = update_workout_plan(plan.original_plan, payload.feedback)
        update_plan(db, payload.user_id, revised, payload.feedback)
        return templates.TemplateResponse(request=request, name="result.html", context={"user": user, "workout_plan": _safe_json(plan.original_plan), "nutrition_tip": plan.nutrition_tip, "updated_plan": _safe_json(revised), "message": "Your workout plan was updated using the submitted feedback."})
    except HTTPException: raise
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="error.html", context={"message": f"Could not update the plan: {exc}"}, status_code=500)

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    _check_admin(request)
    users, plans = get_all_users(db), get_all_plans(db)
    plans_by_user = {}
    for plan in plans: plans_by_user.setdefault(plan.user_id, []).append(plan)
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": users, "plans_by_user": plans_by_user})

@router.post("/admin/delete/{user_id}")
def admin_delete_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    _check_admin(request); delete_user(db, user_id)
    key = request.query_params.get("admin_key", "")
    return RedirectResponse("/view-all-users" + (f"?admin_key={key}" if key else ""), status_code=status.HTTP_303_SEE_OTHER)

@router.post("/api/workout")
def api_generate_workout(data: UserInput, db: Session = Depends(get_db)):
    user = save_user(db, data); workout = generate_workout_gemini(data); tip = generate_nutrition_tip_with_flash(data.goal); plan = save_plan(db, user.user_id, workout, tip)
    return {"user": data.model_dump(), "plan_id": plan.id, "workout_plan": json.loads(workout), "nutrition_tip": tip}

@router.post("/api/feedback")
def api_feedback(data: FeedbackRequest, db: Session = Depends(get_db)):
    plan = get_plan(db, data.user_id)
    if not plan: raise HTTPException(404, "Workout plan not found")
    revised = update_workout_plan(plan.original_plan, data.feedback); update_plan(db, data.user_id, revised, data.feedback)
    return {"user_id": data.user_id, "updated_plan": json.loads(revised), "feedback": data.feedback}

@router.get("/api/nutrition-tip")
def api_nutrition_tip(goal: str):
    allowed = {"weight loss", "muscle gain", "general wellness", "flexibility", "endurance"}
    if goal not in allowed: raise HTTPException(422, f"goal must be one of: {sorted(allowed)}")
    return {"goal": goal, "tip": generate_nutrition_tip_with_flash(goal)}
