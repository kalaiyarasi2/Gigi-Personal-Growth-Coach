# Gigi-Personal-Growth-Coach
Gigi is an AI-powered personal growth coach that helps users achieve their goals in health, fitness, study, and lifestyle optimization. 
It integrates **LangGraph for workflow orchestration**, **Google Gemini AI for natural language analysis**, and **ChromaDB + SQLAlchemy for persistent memory and goal tracking**.  


## ✨ Features

- 🔹 **Multi-User Support** – Each user has a unique encrypted session and independent memory.  
- 🔹 **Workflow Orchestration (LangGraph)** – AI-driven flow for input analysis, goal identification, and personalized plan generation.  
- 🔹 **AI Model (Gemini 1.5 Flash)** – Provides context-aware, structured analysis and planning.  
- 🔹 **Persistent Memory** – Stores goals and conversation history in **ChromaDB** (semantic) + **SQLAlchemy ORM** (structured).  
- 🔹 **Secure Data Handling** – Uses **Fernet encryption** and hashing for all stored data.  
- 🔹 **CLI Interface** – Simple terminal-based chat with commands:  
  - `history` → Show past interactions  
  - `clear` → Reset current session  
  - `help` → Show available commands  
  - `exit` → Save & exit session  
- 🔹 **Developer Tool (`dev_view.py`)** – Allows developers to securely decrypt and view stored user inputs for debugging.  
- 🔹 **Error Handling** – Built-in retry logic and rate limiting for API stability.  

---

## 🛠️ Tech Stack

- **AI & Workflow**: [LangGraph](https://github.com/langchain-ai/langgraph), [Google Gemini AI](https://ai.google.dev/)  
- **Memory**: [ChromaDB](https://www.trychroma.com/), [SentenceTransformers](https://www.sbert.net/)  
- **Database**: [SQLAlchemy ORM](https://www.sqlalchemy.org/) (SQLite by default, supports PostgreSQL/MySQL)  
- **Security**: [cryptography.Fernet](https://cryptography.io/), `hashlib`, `secrets`  
- **Validation**: [Pydantic](https://docs.pydantic.dev/)  
- **Async Handling**: `asyncio` with retry + rate limiting  
- **Environment Management**: `python-dotenv`  
- **CLI Interface**: Python-based (`main.py`)  

---

## 📂 Project Structure

```

├── core.py         # Core AI agent logic, DB, memory, encryption
├── main.py         # CLI interface for user interaction
├── dev\_view\.py     # Developer-only tool to view decrypted sessions
├── gigi\_session.json  # Stores session metadata (not raw user input)
├── gigi\_langgraph.db  # SQLite database (encrypted session data)
├── .env            # API keys & encryption key
└── README.md       # Project documentation

````

---

## ⚙️ Setup & Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/gigi-ai-agent.git
   cd gigi-ai-agent
````

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Example `requirements.txt`:

   ```txt
   langgraph
   google-generativeai
   chromadb
   sqlalchemy
   cryptography
   pydantic
   python-dotenv
   ```

3. **Set up environment variables**
   Create a `.env` file:

   ```ini
   GEMINI_API_KEY=your_google_gemini_api_key
   ENCRYPTION_KEY=your_generated_fernet_key
   DATABASE_URL=sqlite:///./gigi_langgraph.db
   ```

   Generate a Fernet key:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

---

## 🚀 Usage

### Run the Agent (CLI)

```bash
python main.py
```

Example session:

```
Welcome to Gigi AI Agent! Type 'help' for commands.
> I want to lose 5kg in 2 months
Gigi: Great! Let's create a fitness and diet plan to achieve this goal.
> history
Shows past conversation and stored goals.
```

Commands:

* `history` → View chat history
* `clear` → Reset current session
* `help` → Show help menu
* `exit` → Save session and exit

---

## 🔍 Developer Tools

### View Stored Sessions

Run:

```bash
python dev_view.py --list
```

View specific session by suffix:

```bash
python dev_view.py --session-suffix 76WMEc --show-full
```

View sessions by user suffix:

```bash
python dev_view.py --user-suffix Abcd1234 --show-full
```

⚠️ Requires correct `ENCRYPTION_KEY` in `.env`.
Without the key, decrypted user input cannot be accessed.

---

## ✅ Testing Checklist

* [✅] CLI chat flow works (`main.py`)
* [✅] Multi-user sessions handled separately
* [✅] Conversation history persists across sessions
* [✅] Goals saved in DB (encrypted)
* [✅] Developer tool (`dev_view.py`) retrieves user data
* [✅] Encryption prevents direct DB inspection
* [✅] Retry logic handles API limits gracefully

---

## 🔮 Future Enhancements

* 🌐 Web-based interface with FastAPI/Streamlit
* 📊 Admin dashboard for secure session management
* 🔑 Role-based access control for developer tools
* 📱 Integration with wearables & health APIs
* 📈 Analytics dashboard for progress tracking

