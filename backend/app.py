from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
# from routes.stock_routes import stock_bp
# from routes.trend_routes import trend_bp
from utils.db import connect_db  # Import connect_db function

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend
app.config['SECRET_KEY'] = 'your_secret_key'  # It’s recommended to use a secret key from .env

# Connect to MongoDB
db = connect_db()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
# app.register_blueprint(stock_bp, url_prefix="/stocks")
# app.register_blueprint(trend_bp, url_prefix="/trends")

if __name__ == "__main__":
    app.run(debug=True)
