from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import connect_db

# Connect to DB
db = connect_db()
users_collection = db["users"]

# Function to create a new user
def create_user(username, password):
    if users_collection.find_one({"username": username}):
        return None  # User already exists
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password})
    return {"username": username, "password": hashed_password}

# Function to authenticate a user
def authenticate_user(username, password):
    user = users_collection.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return None  # Invalid username or password
    return user
