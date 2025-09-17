# dev_view.py
import asyncio
import json
from core import SessionLocal, SessionRecord, security

async def view_all_sessions():
    """Developer-only: Decrypt and display all user session data"""
    db = SessionLocal()
    try:
        sessions = db.query(SessionRecord).all()
        results = []
        for s in sessions:
            try:
                # Decrypt stored data
                decrypted = security.decrypt_data(s.encrypted_data)
                data = json.loads(decrypted)

                results.append({
                    "session_token": s.session_token,
                    "user_internal_id": s.user_internal_id,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "last_activity": s.last_activity.isoformat() if s.last_activity else None,
                    "conversation_history": data.get("conversation_history", [])
                })
            except Exception as e:
                results.append({
                    "session_token": s.session_token,
                    "error": f"Decryption failed: {str(e)}"
                })
        return results
    finally:
        db.close()

async def main():
    print("=== Developer View: User Sessions ===\n")
    sessions = await view_all_sessions()

    for s in sessions:
        print(f"📌 Session: {s['session_token']}")
        print(f"👤 User: {s.get('user_internal_id', 'Unknown')}")
        print(f"🕒 Created: {s.get('created_at')}")
        print(f"🕒 Last Activity: {s.get('last_activity')}")
        
        if "conversation_history" in s:
            for convo in s["conversation_history"]:
                print(f"   🗨️ User: {convo.get('user_message')}")
                print(f"   📊 Analysis: {convo.get('analysis')}")
            print("-" * 50)
        else:
            print(f"   ⚠️ {s.get('error')}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
