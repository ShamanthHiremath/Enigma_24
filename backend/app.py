import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from routes.stock_routes import stock_bp
from routes.market_routes import market_bp
from utils.db import connect_db

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Set secret key for Flask app
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")

# Connect to MongoDB (if needed)
db = connect_db()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(stock_bp, url_prefix="/stocks")
app.register_blueprint(market_bp, url_prefix='/api/market')

if __name__ == "__main__":
    app.run(debug=True)
