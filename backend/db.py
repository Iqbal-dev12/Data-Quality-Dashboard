from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection

from backend.config import load_config


_client: Optional[MongoClient] = None


def get_collection() -> Collection:
	global _client
	config = load_config()
	if _client is None:
		_client = MongoClient(config.mongodb_uri)
	db = _client[config.database_name]
	return db[config.collection_name]


def get_feedback_collection() -> Collection:
	global _client
	config = load_config()
	if _client is None:
		_client = MongoClient(config.mongodb_uri)
	db = _client[config.database_name]
	return db[config.feedback_collection_name]


def get_session_collection() -> Collection:
	global _client
	config = load_config()
	if _client is None:
		_client = MongoClient(config.mongodb_uri)
	db = _client[config.database_name]
	return db[config.session_collection_name]

