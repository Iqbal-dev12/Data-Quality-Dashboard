#!/usr/bin/env python3
"""
Test script for session tracking functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5001"
SESSION_ENDPOINT = f"{API_BASE_URL}/api/session"
ANALYTICS_ENDPOINT = f"{API_BASE_URL}/api/analytics"

def test_session_tracking():
    """Test the complete session tracking workflow"""
    print("🧪 Testing Session Tracking API")
    print("=" * 50)
    
    # Test 1: Start a session
    print("\n1. Testing session start...")
    try:
        start_response = requests.post(
            f"{SESSION_ENDPOINT}/start",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if start_response.status_code == 201:
            session_data = start_response.json()
            session_id = session_data["session_id"]
            print(f"✅ Session started successfully")
            print(f"   Session ID: {session_id}")
            print(f"   Start time: {session_data['start_time']}")
        else:
            print(f"❌ Failed to start session: {start_response.status_code}")
            print(f"   Response: {start_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return False
    
    # Test 2: Track some actions
    print("\n2. Testing action tracking...")
    actions_to_test = [
        {"action": "file_upload", "metadata": {"file_size": "2.5MB", "file_type": "csv"}},
        {"action": "data_analysis", "metadata": {"rows_processed": 1500}},
        {"action": "export_csv", "metadata": {"export_format": "csv", "rows_exported": 1200}},
        {"action": "feedback_submit", "metadata": {"rating": 5}}
    ]
    
    for action_data in actions_to_test:
        try:
            action_payload = {
                "session_id": session_id,
                "action": action_data["action"],
                "metadata": action_data["metadata"]
            }
            
            action_response = requests.post(
                f"{SESSION_ENDPOINT}/action",
                json=action_payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if action_response.status_code == 200:
                result = action_response.json()
                print(f"✅ Action '{action_data['action']}' tracked successfully")
                print(f"   Timestamp: {result['timestamp']}")
            else:
                print(f"❌ Failed to track action '{action_data['action']}': {action_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error tracking action '{action_data['action']}': {e}")
    
    # Wait a moment to simulate session duration
    print("\n3. Simulating user activity...")
    time.sleep(2)
    
    # Test 3: End the session
    print("\n4. Testing session end...")
    try:
        end_response = requests.post(
            f"{SESSION_ENDPOINT}/end",
            json={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if end_response.status_code == 200:
            end_data = end_response.json()
            print(f"✅ Session ended successfully")
            print(f"   End time: {end_data['end_time']}")
        else:
            print(f"❌ Failed to end session: {end_response.status_code}")
            print(f"   Response: {end_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error ending session: {e}")
    
    # Test 4: Get analytics
    print("\n5. Testing analytics endpoint...")
    try:
        analytics_response = requests.get(
            ANALYTICS_ENDPOINT,
            params={"days": 1},
            timeout=10
        )
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print(f"✅ Analytics retrieved successfully")
            print(f"   Total sessions: {analytics_data['total_sessions']}")
            print(f"   Completed sessions: {analytics_data['completed_sessions']}")
            print(f"   Average duration: {analytics_data['avg_duration_minutes']} minutes")
            print(f"   Total actions: {analytics_data['total_actions']}")
            print(f"   Average actions per session: {analytics_data['avg_actions_per_session']}")
        else:
            print(f"❌ Failed to get analytics: {analytics_response.status_code}")
            print(f"   Response: {analytics_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting analytics: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Session tracking test completed!")
    return True

def test_error_cases():
    """Test error handling"""
    print("\n🧪 Testing Error Cases")
    print("=" * 30)
    
    # Test invalid session action
    print("\n1. Testing action without session_id...")
    try:
        response = requests.post(
            f"{SESSION_ENDPOINT}/action",
            json={"action": "test_action"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 400:
            print("✅ Correctly rejected action without session_id")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
    
    # Test ending non-existent session
    print("\n2. Testing end of non-existent session...")
    try:
        response = requests.post(
            f"{SESSION_ENDPOINT}/end",
            json={"session_id": "non_existent_session"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 404:
            print("✅ Correctly rejected non-existent session")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Session Tracking Tests")
    print(f"📡 API Base URL: {API_BASE_URL}")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run main tests
    success = test_session_tracking()
    
    # Run error case tests
    test_error_cases()
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check your backend server.")
        
    print("\n💡 To view session data, check your MongoDB 'user_sessions' collection")
