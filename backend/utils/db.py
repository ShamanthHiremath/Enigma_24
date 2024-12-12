import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variables
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/StockAnalysis")

# Function to connect to the database
def connect_db():
    client = MongoClient(MONGODB_URI)
    db = client.get_database()  # You can get the database from the URI directly
    return db
