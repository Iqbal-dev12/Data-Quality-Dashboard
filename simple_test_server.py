#!/usr/bin/env python3
"""
Simple test server without MongoDB dependency
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage for testing
feedback_storage = []

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'rating' not in data or 'text' not in data:
            return jsonify({"error": "Rating and text are required"}), 400
        
        rating = data.get('rating')
        text = data.get('text', '').strip()
        
        # Validate rating
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        
        # Validate text
        if not text:
            return jsonify({"error": "Feedback text cannot be empty"}), 400
        
        # Create feedback object
        feedback = {
            "rating": rating,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": data.get('user_id'),
            "session_id": data.get('session_id'),
            "_id": f"test_{len(feedback_storage) + 1}"
        }
        
        # Save to memory
        feedback_storage.append(feedback)
        
        return jsonify({
            "message": "Feedback submitted successfully",
            "feedback_id": feedback["_id"]
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/api/feedback", methods=["GET"])
def get_feedback():
    """Get all feedback"""
    try:
        return jsonify({
            "feedback": feedback_storage,
            "total_count": len(feedback_storage),
            "page": 1,
            "limit": 50,
            "total_pages": 1
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route("/health")
def health_check():
    return {"status": "ok", "message": "Simple test server running"}

if __name__ == "__main__":
    print("🚀 Starting simple test server on http://localhost:5001")
    print("📝 This server uses in-memory storage (no MongoDB required)")
    app.run(host="0.0.0.0", port=5001, debug=True)
