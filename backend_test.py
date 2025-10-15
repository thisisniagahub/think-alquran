#!/usr/bin/env python3
"""
ThinkQuran Backend API Test Suite
Tests all backend endpoints for the ThinkQuran mobile app
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    return line.split('=')[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_BASE = f"{BASE_URL}/api"
print(f"Testing backend at: {API_BASE}")

class ThinkQuranAPITest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = {
            "username": "testuser2", 
            "password": "password123"
        }
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_register(self):
        """Test user registration"""
        print("\n=== Testing User Registration ===")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/register",
                json=self.user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.log_test("User Registration", True, 
                                f"User registered successfully. Token received. User ID: {data['user']['id']}")
                    return True
                else:
                    self.log_test("User Registration", False, 
                                f"Missing required fields in response: {data}")
                    return False
            elif response.status_code == 400:
                # User might already exist, try login instead
                self.log_test("User Registration", True, 
                            "User already exists (expected), will try login")
                return self.test_login()
            else:
                self.log_test("User Registration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_login(self):
        """Test user login"""
        print("\n=== Testing User Login ===")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=self.user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.log_test("User Login", True, 
                                f"Login successful. User: {data['user']['username']}")
                    return True
                else:
                    self.log_test("User Login", False, 
                                f"Missing required fields in response: {data}")
                    return False
            else:
                self.log_test("User Login", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def test_dashboard(self):
        """Test dashboard stats endpoint"""
        print("\n=== Testing Dashboard Stats ===")
        
        try:
            response = self.session.get(
                f"{API_BASE}/dashboard",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_words_learned", "current_streak", "total_lessons_completed", 
                                 "mastery_percentage", "words_practiced_today"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Dashboard Stats", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                self.log_test("Dashboard Stats", True, 
                            f"Dashboard loaded. Words learned: {data['total_words_learned']}, "
                            f"Streak: {data['current_streak']}, Lessons completed: {data['total_lessons_completed']}")
                return True
            else:
                self.log_test("Dashboard Stats", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Exception: {str(e)}")
            return False
    
    def test_lessons_list(self):
        """Test lessons list endpoint"""
        print("\n=== Testing Lessons List ===")
        
        try:
            response = self.session.get(
                f"{API_BASE}/lessons",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 3:
                    # Check lesson structure
                    lesson_titles = [lesson.get("title") for lesson in data]
                    expected_titles = ["Basic Words", "Common Verbs", "Pronouns & Particles"]
                    
                    if all(title in lesson_titles for title in expected_titles):
                        self.log_test("Lessons List", True, 
                                    f"3 lessons found: {lesson_titles}")
                        return True
                    else:
                        self.log_test("Lessons List", False, 
                                    f"Unexpected lesson titles: {lesson_titles}")
                        return False
                else:
                    self.log_test("Lessons List", False, 
                                f"Expected 3 lessons, got: {len(data) if isinstance(data, list) else 'not a list'}")
                    return False
            else:
                self.log_test("Lessons List", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Lessons List", False, f"Exception: {str(e)}")
            return False
    
    def test_lesson_words(self, lesson_number=1):
        """Test getting words for a specific lesson"""
        print(f"\n=== Testing Lesson {lesson_number} Words ===")
        
        try:
            response = self.session.get(
                f"{API_BASE}/lessons/{lesson_number}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 10:
                    # Check word structure
                    required_fields = ["id", "arabic", "transliteration", "meaning"]
                    
                    for word in data:
                        missing_fields = [field for field in required_fields if field not in word]
                        if missing_fields:
                            self.log_test(f"Lesson {lesson_number} Words", False, 
                                        f"Word missing fields: {missing_fields}")
                            return False
                    
                    # Check specific words for lesson 1
                    if lesson_number == 1:
                        expected_words = ["Allah", "Rabb", "Rahman", "Rahim", "Malik", 
                                        "Yawm", "Deen", "Na'budu", "Nasta'een", "Sirat"]
                        actual_words = [word["transliteration"] for word in data]
                        
                        if all(word in actual_words for word in expected_words):
                            self.log_test(f"Lesson {lesson_number} Words", True, 
                                        f"10 words found with correct content: {actual_words[:3]}...")
                            return data  # Return words for quiz testing
                        else:
                            self.log_test(f"Lesson {lesson_number} Words", False, 
                                        f"Missing expected words. Got: {actual_words}")
                            return False
                    else:
                        self.log_test(f"Lesson {lesson_number} Words", True, 
                                    f"10 words found for lesson {lesson_number}")
                        return data
                else:
                    self.log_test(f"Lesson {lesson_number} Words", False, 
                                f"Expected 10 words, got: {len(data) if isinstance(data, list) else 'not a list'}")
                    return False
            else:
                self.log_test(f"Lesson {lesson_number} Words", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"Lesson {lesson_number} Words", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_lesson(self, lesson_words):
        """Test completing a lesson with quiz results"""
        print("\n=== Testing Lesson Completion ===")
        
        if not lesson_words:
            self.log_test("Lesson Completion", False, "No lesson words provided")
            return False
        
        try:
            # Create quiz answers (mix of correct/incorrect)
            answers = []
            for i, word in enumerate(lesson_words[:5]):  # Test with first 5 words
                answers.append({
                    "word_id": word["id"],
                    "is_correct": i % 2 == 0,  # Alternate correct/incorrect
                    "time_spent": 5 + i  # Varying time
                })
            
            completion_data = {
                "lesson_id": "lesson_1",
                "answers": answers,
                "total_time": 30
            }
            
            response = self.session.post(
                f"{API_BASE}/lessons/complete",
                json=completion_data,
                headers={**self.get_auth_headers(), "Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "words_learned" in data:
                    self.log_test("Lesson Completion", True, 
                                f"Lesson completed successfully. Words learned: {data['words_learned']}")
                    return True
                else:
                    self.log_test("Lesson Completion", False, 
                                f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Lesson Completion", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Lesson Completion", False, f"Exception: {str(e)}")
            return False
    
    def test_word_progress(self):
        """Test word progress endpoint"""
        print("\n=== Testing Word Progress ===")
        
        try:
            response = self.session.get(
                f"{API_BASE}/progress/words",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check progress structure
                    required_fields = ["id", "arabic", "transliteration", "meaning", 
                                     "mastery_level", "total_attempts"]
                    
                    for word_progress in data[:3]:  # Check first 3 words
                        missing_fields = [field for field in required_fields if field not in word_progress]
                        if missing_fields:
                            self.log_test("Word Progress", False, 
                                        f"Progress missing fields: {missing_fields}")
                            return False
                    
                    # Check if some words have progress after lesson completion
                    words_with_progress = [w for w in data if w["mastery_level"] > 0]
                    
                    self.log_test("Word Progress", True, 
                                f"Progress loaded for {len(data)} words. "
                                f"{len(words_with_progress)} words have progress.")
                    return True
                else:
                    self.log_test("Word Progress", False, 
                                f"Expected word list, got: {len(data) if isinstance(data, list) else 'not a list'}")
                    return False
            else:
                self.log_test("Word Progress", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Word Progress", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_errors(self):
        """Test authentication error cases"""
        print("\n=== Testing Authentication Errors ===")
        
        # Test invalid credentials
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json={"username": "nonexistent", "password": "wrong"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_test("Invalid Login", True, "Correctly rejected invalid credentials")
            else:
                self.log_test("Invalid Login", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Login", False, f"Exception: {str(e)}")
        
        # Test protected endpoint without auth
        try:
            response = self.session.get(f"{API_BASE}/dashboard")
            
            if response.status_code == 403:
                self.log_test("No Auth Access", True, "Correctly rejected request without auth")
            else:
                self.log_test("No Auth Access", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_test("No Auth Access", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting ThinkQuran Backend API Tests")
        print("=" * 50)
        
        # Authentication flow
        if not self.test_register():
            print("❌ Registration failed, cannot continue with other tests")
            return False
        
        # Test all endpoints
        self.test_dashboard()
        self.test_lessons_list()
        
        # Test lesson words and completion
        lesson_words = self.test_lesson_words(1)
        if lesson_words:
            self.test_complete_lesson(lesson_words)
        
        # Test progress after completion
        self.test_word_progress()
        
        # Test error cases
        self.test_auth_errors()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = ThinkQuranAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)