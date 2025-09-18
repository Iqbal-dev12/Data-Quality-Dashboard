from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from pymongo.errors import PyMongoError

from backend.db import get_feedback_collection, get_session_collection
from backend.models import Feedback, UserSession

api_bp = Blueprint("api", __name__)

@api_bp.route("/", methods=["GET"])
def example():
    """Example endpoint"""
    return jsonify({"message": "Hello from the API!"})


@api_bp.route("/feedback", methods=["POST"])
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
        feedback = Feedback(
            rating=rating,
            text=text,
            timestamp=datetime.utcnow(),
            user_id=data.get('user_id'),
            session_id=data.get('session_id')
        )
        
        # Save to database
        collection = get_feedback_collection()
        result = collection.insert_one(feedback.to_dict())
        
        return jsonify({
            "message": "Feedback submitted successfully",
            "feedback_id": str(result.inserted_id)
        }), 201
        
    except PyMongoError as e:
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@api_bp.route("/feedback", methods=["GET"])
def get_feedback():
    """Get all feedback (admin endpoint)"""
    try:
        collection = get_feedback_collection()
        
        # Get query parameters for pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        
        # Get total count
        total_count = collection.count_documents({})
        
        # Get feedback with pagination, sorted by timestamp (newest first)
        feedback_cursor = collection.find({}).sort("timestamp", -1).skip(skip).limit(limit)
        
        feedback_list = []
        for doc in feedback_cursor:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            feedback_list.append(doc)
        
        return jsonify({
            "feedback": feedback_list,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }), 200
        
    except PyMongoError as e:
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@api_bp.route("/session/start", methods=["POST"])
def start_session():
    """Start a new user session"""
    try:
        data = request.get_json() or {}
        
        # Generate session ID if not provided
        session_id = data.get('session_id') or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Get client info
        user_agent = request.headers.get('User-Agent')
        ip_address = request.remote_addr
        
        # Create session object
        session = UserSession(
            session_id=session_id,
            start_time=datetime.utcnow(),
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Save to database
        collection = get_session_collection()
        result = collection.insert_one(session.to_dict())
        
        return jsonify({
            "message": "Session started successfully",
            "session_id": session_id,
            "start_time": session.start_time.isoformat()
        }), 201
        
    except PyMongoError as e:
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@api_bp.route("/session/action", methods=["POST"])
def track_action():
    """Track a user action within a session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'session_id' not in data or 'action' not in data:
            return jsonify({"error": "session_id and action are required"}), 400
        
        session_id = data.get('session_id')
        action = data.get('action')
        metadata = data.get('metadata', {})
        
        # Find the session
        collection = get_session_collection()
        session_doc = collection.find_one({"session_id": session_id})
        
        if not session_doc:
            return jsonify({"error": "Session not found"}), 404
        
        # Add action to session
        new_action = {
            "action": action,
            "timestamp": datetime.utcnow(),
            "metadata": metadata
        }
        
        # Update session with new action
        collection.update_one(
            {"session_id": session_id},
            {
                "$push": {"actions": new_action},
                "$inc": {"action_count": 1}
            }
        )
        
        return jsonify({
            "message": "Action tracked successfully",
            "session_id": session_id,
            "action": action,
            "timestamp": new_action["timestamp"].isoformat()
        }), 200
        
    except PyMongoError as e:
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@api_bp.route("/session/end", methods=["POST"])
def end_session():
    """End a user session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'session_id' not in data:
            return jsonify({"error": "session_id is required"}), 400
        
        session_id = data.get('session_id')
        
        # Find and update the session
        collection = get_session_collection()
        end_time = datetime.utcnow()
        
        result = collection.update_one(
            {"session_id": session_id, "end_time": None},
            {
                "$set": {
                    "end_time": end_time
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Active session not found"}), 404
        
        # Calculate duration
        session_doc = collection.find_one({"session_id": session_id})
        if session_doc:
            start_time = session_doc["start_time"]
            duration = (end_time - start_time).total_seconds() / 60
            
            # Update with duration
            collection.update_one(
                {"session_id": session_id},
                {"$set": {"duration_minutes": round(duration, 2)}}
            )
        
        return jsonify({
            "message": "Session ended successfully",
            "session_id": session_id,
            "end_time": end_time.isoformat()
        }), 200
        
    except PyMongoError as e:
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@api_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """Get user analytics and session statistics (admin endpoint)"""
    try:
        collection = get_session_collection()
        
        # Get query parameters
        days = int(request.args.get('days', 7))  # Default to last 7 days
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Simple date calculation for recent days
        start_date = end_date - timedelta(days=days)
        
        # Get basic session statistics
        total_sessions = collection.count_documents({
            "start_time": {"$gte": start_date, "$lte": end_date}
        })
        
        completed_sessions = collection.count_documents({
            "start_time": {"$gte": start_date, "$lte": end_date},
            "end_time": {"$ne": None}
        })
        
        # Get sessions with duration for average calculation
        sessions_with_duration = list(collection.find({
            "start_time": {"$gte": start_date, "$lte": end_date},
            "duration_minutes": {"$ne": None}
        }, {"duration_minutes": 1, "action_count": 1}))
        
        avg_duration = 0
        avg_actions = 0
        total_actions = 0
        
        if sessions_with_duration:
            avg_duration = sum(s.get("duration_minutes", 0) for s in sessions_with_duration) / len(sessions_with_duration)
            avg_actions = sum(s.get("action_count", 0) for s in sessions_with_duration) / len(sessions_with_duration)
            total_actions = sum(s.get("action_count", 0) for s in sessions_with_duration)
        
        response = {
            "period_days": days,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "avg_duration_minutes": round(avg_duration, 2),
            "total_actions": total_actions,
            "avg_actions_per_session": round(avg_actions, 2)
        }
        
        return jsonify(response), 200
        
    except PyMongoError as e:
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500
