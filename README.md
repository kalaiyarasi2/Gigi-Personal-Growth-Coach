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
