from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Gigi AI Coach API",
    description="Personal Growth Coaching System with LangGraph Integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Data storage (In production, use a proper database)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
GOALS_FILE = DATA_DIR / "goals.json"

# Initialize data files
for file_path in [USERS_FILE, SESSIONS_FILE, GOALS_FILE]:
    if not file_path.exists():
        file_path.write_text("{}")

# Pydantic models
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    age: Optional[int] = None
    goals: Optional[List[str]] = []

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    username: str
    email: str
    full_name: str
    age: Optional[int] = None
    goals: List[str] = []
    created_at: str
    coaching_sessions: int = 0

class CoachingMessage(BaseModel):
    session_id: str
    message: str
    user_id: Optional[str] = None

class StartSession(BaseModel):
    user_id: str
    session_type: str = "general"

class Goal(BaseModel):
    title: str
    description: str
    target_date: str
    category: str
    priority: str = "medium"

class GoalUpdate(BaseModel):
    goal_id: str
    status: str
    progress: int
    notes: Optional[str] = None

# Utility functions
def load_json(file_path: Path) -> Dict:
    try:
        return json.loads(file_path.read_text())
    except:
        return {}

def save_json(file_path: Path, data: Dict):
    file_path.write_text(json.dumps(data, indent=2, default=str))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Simple token verification (implement proper JWT in production)
    users = load_json(USERS_FILE)
    for user_data in users.values():
        if user_data.get("token") == credentials.credentials:
            return user_data["username"]
    raise HTTPException(status_code=401, detail="Invalid token")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Gigi AI Coach API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# User endpoints
@app.post("/users/register")
async def register_user(user: UserRegistration):
    users = load_json(USERS_FILE)
    
    # Check if user exists
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check email
    for existing_user in users.values():
        if existing_user.get("email") == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_data = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "full_name": user.full_name,
        "age": user.age,
        "goals": user.goals,
        "created_at": datetime.now().isoformat(),
        "coaching_sessions": 0,
        "token": generate_token()
    }
    
    users[user.username] = user_data
    save_json(USERS_FILE, users)
    
    return {
        "message": "User registered successfully",
        "username": user.username,
        "token": user_data["token"]
    }

@app.post("/users/login")
async def login_user(login_data: UserLogin):
    users = load_json(USERS_FILE)
    
    if login_data.username not in users:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user_data = users[login_data.username]
    if user_data["password"] != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate new token
    user_data["token"] = generate_token()
    users[login_data.username] = user_data
    save_json(USERS_FILE, users)
    
    return {
        "message": "Login successful",
        "username": login_data.username,
        "token": user_data["token"]
    }

@app.get("/users/profile", response_model=UserProfile)
async def get_user_profile(current_user: str = Depends(verify_token)):
    users = load_json(USERS_FILE)
    user_data = users[current_user]
    
    return UserProfile(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        age=user_data.get("age"),
        goals=user_data.get("goals", []),
        created_at=user_data["created_at"],
        coaching_sessions=user_data.get("coaching_sessions", 0)
    )

@app.put("/users/profile")
async def update_user_profile(
    profile_update: dict,
    current_user: str = Depends(verify_token)
):
    users = load_json(USERS_FILE)
    user_data = users[current_user]
    
    # Update allowed fields
    allowed_fields = ["full_name", "age", "goals"]
    for field in allowed_fields:
        if field in profile_update:
            user_data[field] = profile_update[field]
    
    users[current_user] = user_data
    save_json(USERS_FILE, users)
    
    return {"message": "Profile updated successfully"}

# Coaching endpoints
@app.post("/coaching/start")
async def start_coaching_session(
    session_data: StartSession,
    current_user: str = Depends(verify_token)
):
    sessions = load_json(SESSIONS_FILE)
    users = load_json(USERS_FILE)
    
    session_id = f"session_{secrets.token_urlsafe(16)}"
    
    session_info = {
        "session_id": session_id,
        "user_id": current_user,
        "session_type": session_data.session_type,
        "started_at": datetime.now().isoformat(),
        "messages": [],
        "status": "active"
    }
    
    sessions[session_id] = session_info
    save_json(SESSIONS_FILE, sessions)
    
    # Update user session count
    users[current_user]["coaching_sessions"] += 1
    save_json(USERS_FILE, users)
    
    return {
        "session_id": session_id,
        "message": "Coaching session started successfully",
        "welcome_message": f"Hello {users[current_user]['full_name']}! I'm Gigi, your personal growth coach. How can I help you today?"
    }

@app.post("/coaching/message")
async def send_coaching_message(
    message_data: CoachingMessage,
    current_user: str = Depends(verify_token)
):
    sessions = load_json(SESSIONS_FILE)
    
    if message_data.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[message_data.session_id]
    
    # Add user message
    user_message = {
        "sender": "user",
        "message": message_data.message,
        "timestamp": datetime.now().isoformat()
    }
    session["messages"].append(user_message)
    
    # Simulate AI response (integrate with LangGraph here)
    ai_response = generate_ai_response(message_data.message, session)
    
    ai_message = {
        "sender": "ai",
        "message": ai_response,
        "timestamp": datetime.now().isoformat()
    }
    session["messages"].append(ai_message)
    
    sessions[message_data.session_id] = session
    save_json(SESSIONS_FILE, sessions)
    
    return {
        "session_id": message_data.session_id,
        "ai_response": ai_response,
        "message_count": len(session["messages"])
    }

def generate_ai_response(user_message: str, session: dict) -> str:
    """
    This is where you'll integrate with your LangGraph workflow
    For now, returning a simple response based on keywords
    """
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["confidence", "self-esteem"]):
        return "Building confidence is a journey! Let's start by identifying your strengths. What's one thing you did well today, no matter how small?"
    
    elif any(word in message_lower for word in ["goal", "achieve", "success"]):
        return "Goal setting is powerful! What specific outcome do you want to achieve? Let's make it SMART - Specific, Measurable, Achievable, Relevant, and Time-bound."
    
    elif any(word in message_lower for word in ["stress", "anxious", "overwhelmed"]):
        return "I hear that you're feeling overwhelmed. Let's take a step back. What's the most pressing thing on your mind right now? Sometimes breaking it down helps."
    
    elif any(word in message_lower for word in ["motivation", "motivated", "procrastination"]):
        return "Motivation can be tricky! Instead of waiting for motivation, let's create systems. What's one small action you could take right now toward your goal?"
    
    else:
        return f"Thank you for sharing that with me. I'm here to support your growth journey. Can you tell me more about what specific area you'd like to work on today?"

@app.get("/coaching/history")
async def get_coaching_history(current_user: str = Depends(verify_token)):
    sessions = load_json(SESSIONS_FILE)
    user_sessions = []
    
    for session_id, session_data in sessions.items():
        if session_data["user_id"] == current_user:
            user_sessions.append({
                "session_id": session_id,
                "session_type": session_data["session_type"],
                "started_at": session_data["started_at"],
                "message_count": len(session_data["messages"]),
                "status": session_data["status"]
            })
    
    return {"sessions": user_sessions}

# Goals endpoints
@app.post("/goals/create")
async def create_goal(goal: Goal, current_user: str = Depends(verify_token)):
    goals = load_json(GOALS_FILE)
    
    goal_id = f"goal_{secrets.token_urlsafe(16)}"
    
    goal_data = {
        "goal_id": goal_id,
        "user_id": current_user,
        "title": goal.title,
        "description": goal.description,
        "target_date": goal.target_date,
        "category": goal.category,
        "priority": goal.priority,
        "status": "active",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "notes": []
    }
    
    goals[goal_id] = goal_data
    save_json(GOALS_FILE, goals)
    
    return {
        "goal_id": goal_id,
        "message": "Goal created successfully",
        "goal": goal_data
    }

@app.get("/goals/progress")
async def get_goals_progress(current_user: str = Depends(verify_token)):
    goals = load_json(GOALS_FILE)
    user_goals = []
    
    for goal_id, goal_data in goals.items():
        if goal_data["user_id"] == current_user:
            user_goals.append(goal_data)
    
    return {"goals": user_goals}

@app.put("/goals/update")
async def update_goal(
    goal_update: GoalUpdate,
    current_user: str = Depends(verify_token)
):
    goals = load_json(GOALS_FILE)
    
    if goal_update.goal_id not in goals:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal = goals[goal_update.goal_id]
    
    if goal["user_id"] != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    goal["status"] = goal_update.status
    goal["progress"] = goal_update.progress
    goal["updated_at"] = datetime.now().isoformat()
    
    if goal_update.notes:
        goal["notes"].append({
            "note": goal_update.notes,
            "timestamp": datetime.now().isoformat()
        })
    
    goals[goal_update.goal_id] = goal
    save_json(GOALS_FILE, goals)
    
    return {"message": "Goal updated successfully", "goal": goal}

# Analytics endpoint
@app.get("/analytics/dashboard")
async def get_analytics(current_user: str = Depends(verify_token)):
    users = load_json(USERS_FILE)
    sessions = load_json(SESSIONS_FILE)
    goals = load_json(GOALS_FILE)
    
    user_data = users[current_user]
    
    # Count user's sessions
    user_session_count = sum(1 for s in sessions.values() if s["user_id"] == current_user)
    
    # Count user's goals
    user_goals = [g for g in goals.values() if g["user_id"] == current_user]
    active_goals = sum(1 for g in user_goals if g["status"] == "active")
    completed_goals = sum(1 for g in user_goals if g["status"] == "completed")
    
    # Calculate average progress
    avg_progress = sum(g["progress"] for g in user_goals) / len(user_goals) if user_goals else 0
    
    return {
        "user_stats": {
            "total_sessions": user_session_count,
            "total_goals": len(user_goals),
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "average_progress": round(avg_progress, 1),
            "member_since": user_data["created_at"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)