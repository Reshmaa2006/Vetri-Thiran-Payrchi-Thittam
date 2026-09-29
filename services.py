from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import User, WorkoutPlan

def save_user(db: Session, data) -> User:
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user:
        user.name, user.age, user.weight, user.goal, user.intensity = data.name, data.age, data.weight, data.goal, data.intensity
    else:
        user = User(user_id=data.user_id, name=data.name, age=data.age, weight=data.weight, goal=data.goal, intensity=data.intensity)
        db.add(user)
    db.commit(); db.refresh(user); return user

def save_plan(db: Session, user_id: str, original_plan: str, nutrition_tip: str) -> WorkoutPlan:
    plan = WorkoutPlan(user_id=user_id, original_plan=original_plan, nutrition_tip=nutrition_tip)
    db.add(plan); db.commit(); db.refresh(plan); return plan

def get_plan(db: Session, user_id: str) -> WorkoutPlan | None:
    return db.scalar(select(WorkoutPlan).where(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.id.desc()))

def get_user(db: Session, user_id: str) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))

def update_plan(db: Session, user_id: str, updated_plan: str, feedback: str) -> WorkoutPlan | None:
    plan = get_plan(db, user_id)
    if not plan: return None
    plan.updated_plan, plan.feedback = updated_plan, feedback
    db.commit(); db.refresh(plan); return plan

def get_all_users(db: Session):
    return list(db.scalars(select(User).order_by(User.id.desc())).all())

def get_all_plans(db: Session):
    return list(db.scalars(select(WorkoutPlan).order_by(WorkoutPlan.id.desc())).all())

def delete_user(db: Session, user_id: str) -> bool:
    user = get_user(db, user_id)
    if not user: return False
    for plan in list(db.scalars(select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)).all()): db.delete(plan)
    db.delete(user); db.commit(); return True
