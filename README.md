# Gigi-Personal-Growth-Coach
Gigi is an AI-powered personal growth coach that helps users achieve their goals in health, fitness, study, and lifestyle optimization.   It integrates Google Gemini AI for intelligent reasoning and planning with ChromaDB for long-term memory of user profiles and progress.

---

## 🚀 Features
- **Goal Assessment** → Understands user requests (e.g., weight loss, exam prep).  
- **Profile Analysis** → Loads or creates personalized user profiles stored in ChromaDB.  
- **Needs Evaluation** → Identifies challenges, risks, and opportunities.  
- **Personalized Planning** → Generates:
  - Nutrition (meal planning 🍎)  
  - Fitness (workout routines 🏋️)  
  - Study schedules 📚  
  - Holistic wellness plans 🧘  
- **Progress Monitoring** → Weekly check-ins with encouragement + adjustments.  
- **Continuous Optimization** → Updates user profile to improve personalization over time.

---

## 🛠️ Technologies Used
- **[Google Gemini API](https://ai.google.dev/)** – Natural language reasoning & content generation.  
- **[ChromaDB](https://docs.trychroma.com/)** – Vector database for memory persistence.  
- **SentenceTransformers (`all-MiniLM-L6-v2`)** – For embedding user profiles.  
- **Python 3.9+** – Core language.  

---

## 🔄 Workflow
1. **User Input** → Enter goals or updates.  
2. **Goal Assessment (Gemini)** → Extracts structured info.  
3. **Profile Analysis (ChromaDB)** → Loads past memory or creates defaults.  
4. **Needs Evaluation (Gemini)** → Identifies readiness, challenges, and opportunities.  
5. **Personalized Planning** → Generates nutrition, workout, study, and lifestyle plans.  
6. **Progress Monitoring** → Tracks progress with feedback.  
7. **Continuous Optimization** → Updates profile in ChromaDB for better personalization.

---

## 📂 Project Structure

├── main.py # Main AI agent script
├── gigi_memory/ # ChromaDB persistence (user profiles, embeddings)
└── README.md # Project documentation


## ▶️ Example Usage
```bash
python main.py

First Run:

"I have a CS exam in 6 weeks and want to lose 4kg. I'm vegetarian and have 1 hour a day."

Weekly Update:

gigi_coach(
    user_id="alex_2025",
    user_request="",  # ignored
    weekly_update="I'm doing well with study but skipping workouts on Fridays."
)

🎯 Future Enhancements

Streamlit web interface for user interaction.

Support for multi-user profiles with authentication.

Integration with wearables (e.g., fitness trackers, sleep apps).

