import asyncio
import sys
import os
import json
from datetime import datetime

# Import the agent from your existing file
from core import LangGraphGigiAPI

SESSION_FILE = "gigi_session.json"

# At the top of main.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--user", type=str, required=True, help="Username for this session")
args = parser.parse_args()

SESSION_FILE = f"gigi_session_{args.user}.json"


class TerminalGigiAgent:
    def __init__(self):
        """Initialize the terminal-based agent"""
        self.api = LangGraphGigiAPI()
        self.session_token = None
        self.conversation_count = 0

    def print_welcome(self):
        """Display welcome message"""
        print("=" * 50)
        print("🤖 GIGI - Your Personal Growth Coach")
        print("=" * 50)
        print("Hi! I'm Gigi, ready to help you achieve your goals!")
        print("Type your message and press Enter to chat.")
        print("Commands: 'exit' to quit, 'history' to see conversation history, 'clear' to start fresh")
        print("=" * 50)

    async def get_conversation_history(self):
        """Retrieve and display conversation history"""
        if not self.session_token:
            print("No conversation history yet.")
            return

        try:
            print("🔍 Loading conversation history...")
            history = await self.api.get_history(self.session_token)
            
            if history['success']:
                conversation_history = history.get('conversation_history', [])
                past_goals = history.get('past_goals', [])
                
                if conversation_history:
                    print(f"\n📊 Conversation Summary (Total: {len(conversation_history)} interactions)")
                    print("-" * 60)
                    
                    # Show last 5 interactions
                    recent_conversations = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
                    
                    for i, convo in enumerate(recent_conversations, 1):
                        timestamp = convo.get('timestamp', 'Unknown time')
                        message = convo.get('user_message', 'No message')[:60]
                        # Format timestamp better
                        try:
                            if 'T' in timestamp:
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                            else:
                                formatted_time = timestamp
                        except:
                            formatted_time = timestamp
                        
                        print(f"{i}. [{formatted_time}] {message}...")
                    
                    if len(conversation_history) > 5:
                        print(f"... and {len(conversation_history) - 5} more interactions")
                else:
                    print("No conversation history found.")

                # Show current goal
                if history.get('current_goal'):
                    goal = history['current_goal']
                    print(f"\n🎯 Current Goal: {goal.get('primary_goal', 'Not specified')}")
                    print(f"⏰ Timeframe: {goal.get('timeframe', 'Not specified')}")
                    print(f"📋 Focus Areas: {', '.join(goal.get('domains', []))}")

                # Show past goals summary
                if past_goals:
                    print(f"\n📚 Total Goals Created: {len(past_goals)}")
                    
                # Show session info
                if history.get('session_created'):
                    try:
                        created = datetime.fromisoformat(history['session_created'].replace('Z', '+00:00'))
                        print(f"🕒 Session Started: {created.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        print(f"🕒 Session Started: {history['session_created']}")
                        
                print("-" * 60)
                
            else:
                error_msg = history.get('message', history.get('error', 'Unknown error'))
                print(f"❌ Could not retrieve conversation history: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error retrieving history: {str(e)}")
            print("💡 Try starting a new conversation to reset your session.")

    async def clear_session(self):
        """Clear current session and start fresh"""
        self.session_token = None
        self.conversation_count = 0
        
        # Remove session file
        if os.path.exists(SESSION_FILE):
            try:
                os.remove(SESSION_FILE)
                print("🗑️ Session cleared! Starting fresh.")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete session file: {e}")
        else:
            print("🗑️ Session cleared! Starting fresh.")

    async def process_user_input(self, user_input: str):
        """Process user input and get AI response"""
        try:
            # Show thinking indicator
            print("🤔 Gigi is thinking...")
            
            # Call the agent
            response = await self.api.chat(
                message=user_input,
                session_token=self.session_token
            )
            
            if response['success']:
                # Update session token for continuity
                self.session_token = response.get('session_token')
                self.conversation_count += 1
                
                # Save session after successful interaction
                self.save_session_to_file()
                
                return response['response']
            else:
                error_msg = response.get('error', 'Unknown error')
                return f"Sorry, I encountered an error: {error_msg}\n\n💡 You can try:\n- Rephrasing your message\n- Typing 'clear' to start a fresh session\n- Typing 'exit' to quit"
                
        except Exception as e:
            return f"Sorry, I encountered a technical issue: {str(e)}\n\n💡 Try typing 'clear' to start a fresh session."

    def save_session_to_file(self):
        """Save session token to file"""
        if self.session_token:
            try:
                with open(SESSION_FILE, 'w') as f:
                    json.dump({
                        "session_token": self.session_token,
                        "last_saved": datetime.utcnow().isoformat(),
                        "conversation_count": self.conversation_count
                    }, f)
            except Exception as e:
                print(f"⚠️ Warning: Could not save session: {e}")

    def load_session_from_file(self):
        """Load session token from file"""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    self.session_token = data.get("session_token")
                    self.conversation_count = data.get("conversation_count", 0)
                    
                    if self.session_token:
                        session_id = self.session_token[-8:] if len(self.session_token) > 8 else self.session_token
                        last_saved = data.get("last_saved", "Unknown")
                        print(f"[✅ Loaded session: ...{session_id} | Last saved: {last_saved[:16]}]")
                        return True
            except Exception as e:
                print(f"[⚠️ Could not load session: {e}]")
                return False
        return False

    async def show_help(self):
        """Display help information"""
        print("\n" + "=" * 50)
        print("📖 HELP - Available Commands")
        print("=" * 50)
        print("🗨️  Just type your message - I'll help you with goals and wellness!")
        print("📊  'history' - View conversation history and goals")
        print("🗑️  'clear' - Start a fresh session (clears history)")
        print("❓  'help' - Show this help message")
        print("🚪  'exit' - Save session and quit")
        print("\n💡 Tips:")
        print("   • Tell me about your goals (fitness, study, lifestyle)")
        print("   • Ask for meal plans, workout routines, or study schedules")
        print("   • I remember our conversation within the same session")
        print("=" * 50)

    async def run(self):
        """Main terminal interaction loop"""
        self.print_welcome()
        
        # Try to load previous session
        session_loaded = self.load_session_from_file()
        
        if not session_loaded:
            print("[Starting new session...]")

        while True:
            try:
                # Get user input
                print(f"\n[Message #{self.conversation_count + 1}]")
                user_input = input("You: ").strip()

                # Handle special commands
                if user_input.lower() == 'exit':
                    self.save_session_to_file()
                    print(f"\n👋 Thanks for chatting! Your session is saved.")
                    if self.conversation_count > 0:
                        print(f"   We had {self.conversation_count} meaningful interactions.")
                    print("   I'll remember our conversation next time!")
                    break

                elif user_input.lower() == 'history':
                    await self.get_conversation_history()
                    continue

                elif user_input.lower() == 'clear':
                    await self.clear_session()
                    continue

                elif user_input.lower() in ['help', '?']:
                    await self.show_help()
                    continue

                elif not user_input:
                    print("Please enter a message or type 'help' for available commands.")
                    continue

                # Process the message with AI agent
                response = await self.process_user_input(user_input)

                # Display response
                print("\n" + "=" * 50)
                print("🤖 Gigi:")
                print("=" * 50)
                print(response)
                print("=" * 50)

            except KeyboardInterrupt:
                self.save_session_to_file()
                print(f"\n👋 Session saved. Goodbye!")
                if self.conversation_count > 0:
                    print(f"   We had {self.conversation_count} great interactions!")
                break

            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("💡 Try typing 'clear' to start fresh, or 'exit' to quit.")
                continue

def main():
    """Entry point for the terminal agent"""
    # Set up Windows event loop policy if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Create and run the terminal agent
    agent = TerminalGigiAgent()
    
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\nAgent terminated by user.")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure your .env file has GEMINI_API_KEY set")
        print("   2. Install required packages: pip install -r requirements.txt")
        print("   3. Try deleting gigi_session.json and restarting")

if __name__ == "__main__":
    main()
