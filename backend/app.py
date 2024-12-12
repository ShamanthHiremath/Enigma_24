import os
from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.stock_routes import stock_bp  # Stock routes
from utils.db import connect_db  # Import the DB connection function
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")  # From .env

# Connect to MongoDB
db = connect_db()

# Register Blueprints for different routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(stock_bp, url_prefix="/stocks")  # Register stock routes

if __name__ == "__main__":
    app.run(debug=True)
