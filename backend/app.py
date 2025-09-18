import os
import sys
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.routes import api_bp


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    # ---- MongoDB Connection ----
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb+srv://fabbnawab_db_user:LEka6FsAx50xAd5x@cluster0.qaohshr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    try:
        client = MongoClient(MONGO_URI)
        app.db = client["data_quality_dashboard"]  # database name
        print("✅ MongoDB client initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize MongoDB client: {e}")
        raise e

    # ---- Routes ----
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health_check():
        # Check MongoDB connection and log error if any
        try:
            app.db.command("ping")
            return {"status": "ok", "db": "connected"}
        except Exception as e:
            error_message = f"❌ MongoDB connection failed: {e}"
            print(error_message)
            return {"status": "error", "db_error": str(e)}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=True)

