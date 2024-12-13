import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Import blueprints
from routes.auth_routes import auth_bp
from routes.stock_routes import stock_bp
from routes.market_routes import market_bp

# Import database connection
from utils.db import connect_db

# Load environment variables
load_dotenv()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Enable CORS with more specific configuration
    CORS(app, resources={
        r"/auth/*": {"origins": "*"},
        r"/stocks/*": {"origins": "*"},
        r"/api/market/*": {"origins": "*"}
    })

    # Configure app settings
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", os.urandom(24)),
        DEBUG=os.getenv("FLASK_DEBUG", "False") == "True"
    )

    # Connect to database
    try:
        db = connect_db()
        app.config['DB'] = db
    except Exception as e:
        print(f"Database connection error: {e}")

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(stock_bp, url_prefix="/stocks")
    app.register_blueprint(market_bp, url_prefix='/api/market')

    return app

# Application factory pattern
app = create_app()

if __name__ == "__main__":
    # Additional configuration for production vs development
    if os.getenv("FLASK_ENV", "development") == "production":
        app.run(
            host='0.0.0.0', 
            port=int(os.getenv('PORT', 5000)),
            debug=False
        )
    else:
        app.run(
            host='127.0.0.1', 
            port=5000, 
            debug=True
        )