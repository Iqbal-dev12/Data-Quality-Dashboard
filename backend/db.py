from typing import Optional, Dict, List, Any, Callable
from pymongo import MongoClient
from pymongo.collection import Collection
import os
import json
import threading

from backend.config import load_config


_client: Optional[MongoClient] = None
_use_mock = False

# Data directory for file-backed mock persistence
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_FEEDBACK_FILE = os.path.join(_DATA_DIR, "feedback.json")
_SESSIONS_FILE = os.path.join(_DATA_DIR, "sessions.json")
_io_lock = threading.Lock()


def _ensure_data_dir() -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)


def _load_mock_data(path: str) -> List[Dict[str, Any]]:
    try:
        if not os.path.exists(path):
            return []
        with _io_lock:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Basic validation to ensure it's a list of dicts
                if isinstance(data, list):
                    return [d for d in data if isinstance(d, dict)]
                return []
    except Exception:
        # If loading fails, fall back to empty (avoid crashing app startup)
        return []


def _save_mock_data(path: str, data: List[Dict[str, Any]]) -> None:
    try:
        _ensure_data_dir()
        with _io_lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, default=str)
    except Exception:
        # Swallow errors to avoid breaking API calls in mock mode
        pass


# In-memory storage for when MongoDB is not available (loaded from disk on import)
_mock_feedback: List[Dict[str, Any]] = _load_mock_data(_FEEDBACK_FILE)
_mock_sessions: List[Dict[str, Any]] = _load_mock_data(_SESSIONS_FILE)


class MockCollection:
    """Mock collection that mimics MongoDB collection interface and persists to disk."""
    def __init__(self, data_store: List[Dict[str, Any]], on_change: Optional[Callable[[List[Dict[str, Any]]], None]] = None):
        self.data_store = data_store
        self._on_change = on_change or (lambda _data: None)
    
    def insert_one(self, document: Dict[str, Any]):
        from datetime import datetime
        document['_id'] = f"mock_{len(self.data_store)}_{datetime.utcnow().timestamp()}"
        self.data_store.append(document)
        # persist
        self._on_change(self.data_store)
        class Result:
            def __init__(self, id):
                self.inserted_id = id
        return Result(document['_id'])
	
    def find(self, query=None, projection=None):
        class MockCursor:
            def __init__(self, data):
                self.data = data
                self._skip = 0
                self._limit = None
                self._sort_key = None
                self._sort_order = 1
            
            def sort(self, key, order=-1):
                self._sort_key = key
                self._sort_order = order
                return self
            
            def skip(self, count):
                self._skip = count
                return self
            
            def limit(self, count):
                self._limit = count
                return self
            
            def __iter__(self):
                result = list(self.data)
                if self._sort_key:
                    try:
                        result.sort(key=lambda x: x.get(self._sort_key, ''), reverse=(self._sort_order == -1))
                    except:
                        pass
                result = result[self._skip:]
                if self._limit:
                    result = result[:self._limit]
                return iter(result)
        
        return MockCursor(self.data_store)
    
    def find_one(self, query):
        for doc in self.data_store:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None
    
    def update_one(self, query, update):
        for doc in self.data_store:
            if all(doc.get(k) == v for k, v in query.items()):
                if '$set' in update:
                    doc.update(update['$set'])
                if '$push' in update:
                    for key, value in update['$push'].items():
                        if key not in doc:
                            doc[key] = []
                        doc[key].append(value)
                if '$inc' in update:
                    for key, value in update['$inc'].items():
                        doc[key] = doc.get(key, 0) + value
                # persist
                self._on_change(self.data_store)
                class Result:
                    matched_count = 1
                return Result()
        class Result:
            matched_count = 0
        return Result()
	
    def count_documents(self, query):
        return len(self.data_store)


def get_collection() -> Collection:
    global _client, _use_mock
    if _use_mock:
        return MockCollection([])
	
    config = load_config()
    try:
        if _client is None:
            _client = MongoClient(config.mongodb_uri, serverSelectionTimeoutMS=2000)
            _client.admin.command('ping')  # Test connection
        db = _client[config.database_name]
        return db[config.collection_name]
    except Exception:
        _use_mock = True
        # generic unnamed collection; no persistence target
        return MockCollection([])


def get_feedback_collection() -> Collection:
    global _client, _use_mock, _mock_feedback
    if _use_mock:
        # persist to feedback.json on changes
        return MockCollection(_mock_feedback, on_change=lambda data: _save_mock_data(_FEEDBACK_FILE, data))
	
    config = load_config()
    try:
        if _client is None:
            _client = MongoClient(config.mongodb_uri, serverSelectionTimeoutMS=2000)
            _client.admin.command('ping')  # Test connection
        db = _client[config.database_name]
        return db[config.feedback_collection_name]
    except Exception:
        _use_mock = True
        return MockCollection(_mock_feedback, on_change=lambda data: _save_mock_data(_FEEDBACK_FILE, data))


def get_session_collection() -> Collection:
    global _client, _use_mock, _mock_sessions
    if _use_mock:
        # persist to sessions.json on changes
        return MockCollection(_mock_sessions, on_change=lambda data: _save_mock_data(_SESSIONS_FILE, data))
	
    config = load_config()
    try:
        if _client is None:
            _client = MongoClient(config.mongodb_uri, serverSelectionTimeoutMS=2000)
            _client.admin.command('ping')  # Test connection
        db = _client[config.database_name]
        return db[config.session_collection_name]
    except Exception:
        _use_mock = True
        return MockCollection(_mock_sessions, on_change=lambda data: _save_mock_data(_SESSIONS_FILE, data))
