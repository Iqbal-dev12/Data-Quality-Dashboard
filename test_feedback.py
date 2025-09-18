#!/usr/bin/env python3
"""
Test script for feedback functionality
"""
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5001"
FEEDBACK_ENDPOINT = f"{API_BASE_URL}/api/feedback"

def test_submit_feedback():
    """Test submitting feedback"""
    print("Testing feedback submission...")
    
    test_feedback = {
        "rating": 5,
        "text": "Great dashboard! Very helpful for data quality monitoring.",
        "session_id": f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    try:
        response = requests.post(
            FEEDBACK_ENDPOINT,
            json=test_feedback,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Feedback submitted successfully!")
            print(f"   Feedback ID: {result.get('feedback_id')}")
            return True
        else:
            print(f"❌ Failed to submit feedback: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_get_feedback():
    """Test retrieving feedback"""
    print("\nTesting feedback retrieval...")
    
    try:
        response = requests.get(FEEDBACK_ENDPOINT, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            feedback_list = result.get('feedback', [])
            print(f"✅ Retrieved {len(feedback_list)} feedback entries")
            
            if feedback_list:
                print("   Latest feedback:")
                latest = feedback_list[0]
                print(f"   - Rating: {latest.get('rating')}/5")
                print(f"   - Text: {latest.get('text')[:50]}...")
                print(f"   - Timestamp: {latest.get('timestamp')}")
            
            return True
        else:
            print(f"❌ Failed to retrieve feedback: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_invalid_feedback():
    """Test submitting invalid feedback"""
    print("\nTesting invalid feedback submission...")
    
    # Test missing rating
    invalid_feedback = {
        "text": "This should fail - no rating"
    }
    
    try:
        response = requests.post(
            FEEDBACK_ENDPOINT,
            json=invalid_feedback,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Correctly rejected feedback without rating")
            return True
        else:
            print(f"❌ Should have rejected invalid feedback: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Data Quality Dashboard Feedback API")
    print("=" * 50)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_submit_feedback():
        tests_passed += 1
    
    if test_get_feedback():
        tests_passed += 1
        
    if test_invalid_feedback():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Feedback system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the backend server and database connection.")
