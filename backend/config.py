import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
	mongodb_uri: str
	database_name: str
	collection_name: str
	feedback_collection_name: str
	session_collection_name: str


def load_config() -> AppConfig:
	load_dotenv()
	return AppConfig(
		mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
		database_name=os.getenv("DB_NAME", "data_quality_db"),
		collection_name=os.getenv("COLLECTION_NAME", "quality_stats"),
		feedback_collection_name=os.getenv("FEEDBACK_COLLECTION_NAME", "feedback"),
		session_collection_name=os.getenv("SESSION_COLLECTION_NAME", "user_sessions"),
	)




