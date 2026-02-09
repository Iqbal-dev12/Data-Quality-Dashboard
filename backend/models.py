from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Feedback:
    """Feedback model for storing user feedback"""
    rating: int  # 1-5 stars
    text: str
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert feedback to dictionary for MongoDB storage"""
        return {
            "rating": self.rating,
            "text": self.text,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Feedback':
        """Create feedback from dictionary"""
        return cls(
            rating=data["rating"],
            text=data["text"],
            timestamp=data["timestamp"],
            user_id=data.get("user_id"),
            session_id=data.get("session_id")
        )


@dataclass
class SessionAction:
    """Individual action within a user session"""
    action: str  # e.g., "file_upload", "export_csv", "feedback_submit"
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None  # Additional action-specific data
    
    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {}
        }


@dataclass
class UserSession:
    """User session model for tracking user activity"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    actions: List[SessionAction] = field(default_factory=list)
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculate session duration in minutes"""
        if self.end_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 60, 2)
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if session is still active"""
        return self.end_time is None
    
    def add_action(self, action: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an action to the session"""
        session_action = SessionAction(
            action=action,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        self.actions.append(session_action)
    
    def end_session(self) -> None:
        """End the session"""
        self.end_time = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert session to dictionary for MongoDB storage"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "actions": [action.to_dict() for action in self.actions],
            "duration_minutes": self.duration_minutes,
            "action_count": len(self.actions)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserSession':
        """Create session from dictionary"""
        session = cls(
            session_id=data["session_id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            user_agent=data.get("user_agent"),
            ip_address=data.get("ip_address")
        )
        
        # Reconstruct actions
        for action_data in data.get("actions", []):
            action = SessionAction(
                action=action_data["action"],
                timestamp=action_data["timestamp"],
                metadata=action_data.get("metadata")
            )
            session.actions.append(action)
        
        return session

