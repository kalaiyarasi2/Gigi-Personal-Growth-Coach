# gigi_coach.py
# Gigi – Personal Growth Coach (Single-File Prototype)
# Uses Gemini + ChromaDB for memory and planning

import os
import json
import time
from typing import Dict, Any, List
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai

# ========================
# CONFIGURATION
# ========================

# Set your API key here
GEMINI_API_KEY = "AIzaSyDIGmkT4aKr6WF_Iyp3axLxf0V1wsN-Q18 "
CHROMA_PATH = "./gigi_memory"

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Initialize ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = client.get_or_create_collection(
    name="user_profiles",
    embedding_function=embedding_func
)

# ========================
# HELPER FUNCTIONS
# ========================

def parse_json(text: str) -> Dict:
    """Safely parse LLM-generated JSON string"""
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return {}

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")

# ========================
# MEMORY: ChromaDB Interface
# ========================

import json

def save_user_profile(user_id: str, profile_data: Dict):
    """Save or update user profile in Chroma. Convert lists/dicts to strings."""
    # Create a clean metadata dict with only supported types
    safe_metadata = {}
    for k, v in profile_data.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            safe_metadata[k] = v
        elif isinstance(v, (list, dict)):
            # Serialize lists/dicts to JSON string
            safe_metadata[k] = json.dumps(v)
        else:
            # Convert anything else to string
            safe_metadata[k] = str(v)
    
    # Add user_id if not present
    if "user_id" not in safe_metadata:
        safe_metadata["user_id"] = user_id

    # Create document for embedding (text representation)
    doc = " | ".join([f"{k}: {v}" for k, v in safe_metadata.items()])

    # Upsert into Chroma
    collection.upsert(
        ids=[user_id],
        documents=[doc],
        metadatas=[safe_metadata]  # Must be a list of dicts
    )

def get_user_profile(user_id: str) -> Dict:
    """Retrieve user profile from Chroma and deserialize fields."""
    result = collection.query(
        query_texts=[f"User {user_id} profile"],
        n_results=1,
        where={"user_id": user_id}
    )
    
    if result['metadatas'] and len(result['metadatas'][0]) > 0:
        metadata = result['metadatas'][0][0]  # First result

        # Deserialize JSON strings back to lists/dicts
        profile = {}
        for k, v in metadata.items():
            if isinstance(v, str):
                try:
                    # Try to parse as JSON (for lists/dicts)
                    profile[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    profile[k] = v
            else:
                profile[k] = v
        return profile
    else:
        return None

# ========================
# GOAL ASSESSMENT
# ========================

def assess_goal(user_input: str) -> Dict:
    prompt = f"""
    Analyze the user request and extract:
    - primary_goal
    - domains (nutrition, fitness, study, lifestyle)
    - timeframe
    - desired_outcomes

    Output as strict JSON.

    Request: {user_input}
    """
    response = gemini_model.generate_content(prompt)
    return parse_json(response.text)

# ========================
# NEEDS EVALUATION
# ========================

def evaluate_needs(user_profile: Dict, goal: Dict) -> Dict:
    prompt = f"""
    User Profile: {user_profile}
    Goal: {goal}

    Identify:
    - challenges
    - readiness_level (1-10)
    - risk_factors
    - opportunities

    Output as JSON.
    """
    response = gemini_model.generate_content(prompt)
    return parse_json(response.text)

# ========================
# TOOL: MEAL PLANNER
# ========================

def generate_meal_plan(user_profile: Dict, goal: Dict) -> str:
    prompt = f"""
    Create a 1-day vegetarian meal plan (high-protein) for someone who:
    - Is {user_profile.get('fitness_level', 'intermediate')}
    - Wants to {goal.get('primary_goal', 'stay healthy')}
    - Has dietary restrictions: {user_profile.get('dietary_restrictions', 'none')}
    - Needs ~{user_profile.get('calorie_target', 2000)} calories

    Output: 3 meals + 2 snacks, with macros.
    """
    response = gemini_model.generate_content(prompt)
    return response.text

# ========================
# TOOL: WORKOUT PLANNER
# ========================

def generate_workout_plan(user_profile: Dict, goal: Dict) -> str:
    prompt = f"""
    Create a 3-day/week workout plan for:
    - Level: {user_profile.get('fitness_level')}
    - Goal: {goal.get('primary_goal')}
    - Equipment: {user_profile.get('equipment', 'bodyweight')}
    - Time: 30 mins/session

    Focus on sustainability.
    """
    response = gemini_model.generate_content(prompt)
    return response.text

# ========================
# TOOL: STUDY HELPER
# ========================

def generate_study_plan(user_profile: Dict, goal: Dict) -> str:
    prompt = f"""
    User has exam in {goal.get('timeframe', '4 weeks')}.
    Subjects: {user_profile.get('subjects', 'various')}
    Best focus time: {user_profile.get('focus_time', 'morning')}

    Create a weekly study schedule using Pomodoro.
    """
    response = gemini_model.generate_content(prompt)
    return response.text

# ========================
# PERSONALIZED PLANNING
# ========================

def create_wellness_plan(user_profile: Dict, goal: Dict, gap_analysis: Dict) -> str:
    prompt = f"""
    Create a 4-week holistic wellness plan integrating:
    - Nutrition
    - Exercise
    - Study
    - Lifestyle (sleep, mindfulness)

    User Profile: {user_profile}
    Goal: {goal}
    Challenges: {gap_analysis.get('challenges', 'Unknown')}

    Make it realistic, motivational, and structured.
    Use markdown format.
    """
    response = gemini_model.generate_content(prompt)
    return response.text

# ========================
# PROGRESS MONITORING
# ========================

def monitor_progress(user_id: str, update: str) -> str:
    profile = get_user_profile(user_id)
    prompt = f"""
    Previous Goal: {profile.get('current_goal')}
    User says: {update}

    Respond with:
    - Progress assessment (0-100%)
    - One piece of encouragement
    - One small adjustment if needed

    Keep it warm and supportive.
    """
    response = gemini_model.generate_content(prompt)
    return response.text

# ========================
# CONTINUOUS OPTIMIZATION
# ========================

def update_profile_after_feedback(user_id: str, feedback: str):
    profile = get_user_profile(user_id)
    prompt = f"""
    Based on this feedback: {feedback}
    Suggest 1-2 updates to the user's profile (e.g., motivation triggers, pain points).

    Output as JSON with keys to update.
    """
    response = gemini_model.generate_content(prompt)
    updates = parse_json(response.text)
    profile.update(updates)
    save_user_profile(user_id, profile)

# ========================
# MAIN AGENT FLOW
# ========================

def gigi_coach(user_id: str, user_request: str, weekly_update: str = None):
    print("🧠 Gigi: Personal Growth Coach Activated\n")

    # Step 0: If progress update, handle it
    if weekly_update:
        feedback = monitor_progress(user_id, weekly_update)
        print("📈 Progress Feedback:")
        print(feedback)
        update_profile_after_feedback(user_id, weekly_update)
        return

    # Step 1: Goal Assessment
    print("🎯 Step 1: Assessing Goal...")
    goal = assess_goal(user_request)
    print(json.dumps(goal, indent=2))

    # Step 2: Profile Analysis
    print("\n📂 Step 2: Loading User Profile...")
    profile = get_user_profile(user_id)
    if not profile:
        print("No profile found. Creating default...")
        profile = {
            "user_id": user_id,
            "fitness_level": "beginner",
            "dietary_restrictions": [],
            "focus_time": "morning",
            "equipment": "none",
            "calorie_target": 2000
        }
        save_user_profile(user_id, profile)
    print(f"Loaded: {list(profile.keys())}")

    # Step 3: Needs Evaluation
    print("\n🔍 Step 3: Evaluating Needs...")
    gap_analysis = evaluate_needs(profile, goal)
    print(json.dumps(gap_analysis, indent=2))

    # Step 4 & 5: Personalized Planning + Tool Activation
    print("\n📋 Step 4+5: Generating Holistic Plan...")
    meal_plan = generate_meal_plan(profile, goal)
    workout_plan = generate_workout_plan(profile, goal)
    study_plan = generate_study_plan(profile, goal)

    final_plan = create_wellness_plan(profile, goal, gap_analysis)
    print("\n✅ Final Wellness Plan:")
    print(final_plan)

    # Save updated goal
    profile['current_goal'] = goal
    save_user_profile(user_id, profile)

    # Step 6: Progress Monitoring (simulated later)
    print("\n📌 Tip: Use `weekly_update='I struggled with meals'` next time for feedback.")

# ========================
# EXAMPLE USAGE
# ========================

if __name__ == "__main__":
    USER_ID = "alex_2025"

    # First run: Set goal
    gigi_coach(
        user_id=USER_ID,
        user_request="I have a CS exam in 6 weeks and want to lose 4kg. I'm vegetarian and have 1 hour a day."
    )

    # Later: Weekly check-in (uncomment to test)
    # gigi_coach(
    #     user_id=USER_ID,
    #     user_request="",  # ignored
    #     weekly_update="I'm doing well with study but skipping workouts on Fridays."
    # )