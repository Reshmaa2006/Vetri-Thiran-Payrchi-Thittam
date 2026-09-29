import os
os.environ["DATABASE_URL"]="sqlite:///./test_fitbuddy.db"
os.environ["GEMINI_API_KEY"]=""
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app
Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
client=TestClient(app)

def test_health():
    r=client.get("/health"); assert r.status_code==200; assert r.json()["status"]=="ok"

def test_home():
    r=client.get("/"); assert r.status_code==200; assert "FitBuddy" in r.text

def test_generate():
    r=client.post("/api/workout",json={"name":"Rahul","user_id":"TEST001","age":22,"weight":65,"goal":"muscle gain","intensity":"medium"})
    assert r.status_code==200; assert len(r.json()["workout_plan"]["days"])==7

def test_feedback():
    r=client.post("/api/feedback",json={"user_id":"TEST001","feedback":"Add more cardio and one rest day."})
    assert r.status_code==200; assert "updated_plan" in r.json()

def test_tip():
    r=client.get("/api/nutrition-tip",params={"goal":"weight loss"}); assert r.status_code==200; assert r.json()["tip"]
