import requests
import json
from datetime import datetime, timedelta

# API Base URL
BASE_URL = "http://localhost:8000"

class GigiCoachTestClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.username = None
        self.session = requests.Session()
    
    def test_health_check(self):
        """Test the health endpoint"""
        print("\n🔍 Testing Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        print("\n🔍 Testing Root Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n🔍 Testing User Registration...")
        
        # Generate unique username for testing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "age": 25,
            "goals": ["Improve confidence", "Learn new skills"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/users/register", json=test_user)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                self.token = result.get("token")
                self.username = result.get("username")
                print(f"✅ Registration successful! Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Registration failed")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_user_login(self):
        """Test user login"""
        if not self.username:
            print("❌ No username available for login test")
            return False
        
        print("\n🔍 Testing User Login...")
        login_data = {
            "username": self.username,
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/users/login", json=login_data)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                self.token = result.get("token")
                print(f"✅ Login successful! New token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login failed")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_get_profile(self):
        """Test getting user profile"""
        if not self.token:
            print("❌ No token available for profile test")
            return False
        
        print("\n🔍 Testing Get User Profile...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/users/profile", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Get profile error: {e}")
            return False
    
    def test_start_coaching_session(self):
        """Test starting a coaching session"""
        if not self.token:
            print("❌ No token available for coaching session test")
            return False
        
        print("\n🔍 Testing Start Coaching Session...")
        headers = {"Authorization": f"Bearer {self.token}"}
        session_data = {
            "user_id": self.username,
            "session_type": "confidence_building"
        }
        
        try:
            response = requests.post(f"{self.base_url}/coaching/start", json=session_data, headers=headers)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                self.session_id = result.get("session_id")
                print(f"✅ Coaching session started! ID: {self.session_id}")
                return True
            else:
                print(f"❌ Failed to start coaching session")
                return False
        except Exception as e:
            print(f"❌ Start coaching session error: {e}")
            return False
    
    def test_send_coaching_message(self):
        """Test sending a coaching message"""
        if not self.token or not hasattr(self, 'session_id'):
            print("❌ No token or session_id available for messaging test")
            return False
        
        print("\n🔍 Testing Send Coaching Message...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        test_messages = [
            "I want to improve my confidence",
            "I'm feeling overwhelmed with work",
            "What are some goals I should set?",
            "I need motivation to exercise"
        ]
        
        for message in test_messages:
            message_data = {
                "session_id": self.session_id,
                "message": message
            }
            
            try:
                response = requests.post(f"{self.base_url}/coaching/message", json=message_data, headers=headers)
                print(f"\n📝 Message: '{message}'")
                print(f"Status: {response.status_code}")
                result = response.json()
                print(f"🤖 AI Response: {result.get('ai_response', 'No response')}")
                
                if response.status_code != 200:
                    print(f"❌ Message failed")
                    return False
            except Exception as e:
                print(f"❌ Send message error: {e}")
                return False
        
        print("✅ All coaching messages sent successfully!")
        return True
    
    def test_create_goal(self):
        """Test creating a goal"""
        if not self.token:
            print("❌ No token available for goal creation test")
            return False
        
        print("\n🔍 Testing Create Goal...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        goal_data = {
            "title": "Improve Public Speaking",
            "description": "Practice speaking in front of groups to build confidence",
            "target_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "category": "Personal Development",
            "priority": "high"
        }
        
        try:
            response = requests.post(f"{self.base_url}/goals/create", json=goal_data, headers=headers)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                self.goal_id = result.get("goal_id")
                print(f"✅ Goal created! ID: {self.goal_id}")
                return True
            else:
                print(f"❌ Failed to create goal")
                return False
        except Exception as e:
            print(f"❌ Create goal error: {e}")
            return False
    
    def test_get_analytics(self):
        """Test getting analytics dashboard"""
        if not self.token:
            print("❌ No token available for analytics test")
            return False
        
        print("\n🔍 Testing Analytics Dashboard...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/analytics/dashboard", headers=headers)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Analytics Data: {json.dumps(result, indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Analytics error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Gigi Coach API Tests...")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Root Endpoint", self.test_root_endpoint),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Profile", self.test_get_profile),
            ("Start Coaching Session", self.test_start_coaching_session),
            ("Send Coaching Messages", self.test_send_coaching_message),
            ("Create Goal", self.test_create_goal),
            ("Analytics Dashboard", self.test_get_analytics),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results[test_name] = False
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASSED" if passed_test else "❌ FAILED"
            print(f"{test_name:<25} {status}")
            if passed_test:
                passed += 1
        
        print("=" * 50)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your API is working perfectly!")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the errors above.")
        
        return passed == total

def main():
    """Main function to run tests"""
    print("🤖 Gigi Coach API Test Client")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    
    input("\nPress Enter to start testing...")
    
    client = GigiCoachTestClient()
    client.run_all_tests()

if __name__ == "__main__":
    main()