# dev_view.py
import argparse
import asyncio
import json
from datetime import datetime

# Import DB objects & security manager from core
from core import SessionLocal, SessionRecord, security

MASK_LEN = 6

def mask_id(s: str, show_last: int = MASK_LEN) -> str:
    if not s:
        return "<unknown>"
    if len(s) <= show_last:
        return s
    return "..." + s[-show_last:]

async def list_sessions(limit: int = 50):
    db = SessionLocal()
    try:
        sessions = db.query(SessionRecord).order_by(SessionRecord.created_at.desc()).limit(limit).all()
        output = []
        for s in sessions:
            output.append({
                "session_token_masked": mask_id(s.session_token),
                "user_internal_id_masked": mask_id(s.user_internal_id),
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "last_activity": s.last_activity.isoformat() if s.last_activity else None
            })
        return output
    finally:
        db.close()

async def get_session_by_token(token: str):
    db = SessionLocal()
    try:
        session = db.query(SessionRecord).filter_by(session_token=token).first()
        return session
    finally:
        db.close()

async def find_sessions_by_token_suffix(suffix: str):
    db = SessionLocal()
    try:
        sessions = db.query(SessionRecord).filter(SessionRecord.session_token.like(f"%{suffix}")).all()
        return sessions
    finally:
        db.close()

async def find_sessions_by_user_suffix(suffix: str):
    db = SessionLocal()
    try:
        sessions = db.query(SessionRecord).filter(SessionRecord.user_internal_id.like(f"%{suffix}")).all()
        return sessions
    finally:
        db.close()

def decrypt_session_record(session_record):
    """Return decrypted payload dict (conversation_history etc) or error."""
    try:
        if not session_record.encrypted_data:
            return {"error": "no encrypted_data"}
        decrypted = security.decrypt_data(session_record.encrypted_data)
        payload = json.loads(decrypted)
        return payload
    except Exception as e:
        return {"error": f"decryption_failed: {e}"}

def print_session_summary(session_record, show_full=False):
    print("-" * 80)
    print(f"Session token: {session_record.session_token}")
    print(f"User internal id: {session_record.user_internal_id}")
    print(f"Created : {session_record.created_at}")
    print(f"Last act: {session_record.last_activity}")
    if show_full:
        payload = decrypt_session_record(session_record)
        if "error" in payload:
            print("  ⚠️", payload["error"])
        else:
            ch = payload.get("conversation_history", [])
            print(f"  Conversation entries: {len(ch)}")
            for i, c in enumerate(ch[-10:], start=1):
                ts = c.get("timestamp", "unknown")
                um = c.get("user_message", "<no-message>")
                analysis = c.get("analysis")
                print(f"    {i}. [{ts}] {um}")
                if analysis:
                    print(f"       analysis: {analysis[:140]}{'...' if len(analysis)>140 else ''}")
    print("-" * 80)

async def main():
    parser = argparse.ArgumentParser(description="Developer session viewer (requires ENCRYPTION_KEY)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="List recent sessions (masked)")
    group.add_argument("--session", type=str, help="Show session by FULL session token")
    group.add_argument("--session-suffix", type=str, help="Find sessions by trailing token characters")
    group.add_argument("--user-suffix", type=str, help="Find sessions by trailing user_internal_id characters")
    parser.add_argument("--show-full", action="store_true", help="Decrypt and show full conversation payload (developer-only)")
    parser.add_argument("--limit", type=int, default=50, help="Max sessions to list")

    args = parser.parse_args()

    if args.list:
        rows = await list_sessions(limit=args.limit)
        print(f"Showing {len(rows)} recent sessions (masked):")
        for r in rows:
            print(f"  Session {r['session_token_masked']}  | User {r['user_internal_id_masked']}  | Created {r['created_at']}  | Last {r['last_activity']}")
        return

    if args.session:
        s = await get_session_by_token(args.session)
        if not s:
            print("No session found with that exact token.")
            return
        print_session_summary(s, show_full=args.show_full)
        return

    if args.session_suffix:
        sessions = await find_sessions_by_token_suffix(args.session_suffix)
        if not sessions:
            print("No sessions match that suffix.")
            return
        for s in sessions:
            print_session_summary(s, show_full=args.show_full)
        return

    if args.user_suffix:
        sessions = await find_sessions_by_user_suffix(args.user_suffix)
        if not sessions:
            print("No sessions match that user id suffix.")
            return
        for s in sessions:
            print_session_summary(s, show_full=args.show_full)
        return

    parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
