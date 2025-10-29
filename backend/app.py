import os
import sys
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.routes import api_bp  # make sure your routes handle feedback, sessions, etc.


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    
    # Stable server settings
    host = "127.0.0.1"
    port = 5001
    debug = False           # disable debug mode
    use_reloader = False    # disable Flask auto-reloader

    print(f"Starting backend server on http://{host}:{port} ...")
    app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)

