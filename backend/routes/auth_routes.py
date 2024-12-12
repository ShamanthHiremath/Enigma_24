from flask import Blueprint, request, jsonify
from models.user_model import create_user, authenticate_user  # Import the functions
from utils.auth import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = create_user(username, password)
    if not user:
        return jsonify({"error": "User already exists"}), 409
    
    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    user = authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = generate_token({"username": username})
    return jsonify({"token": token}), 200
