from pymongo import MongoClient
import os

class DatabaseConnection:
    def __init__(self):
        # For local testing, use a simple connection
        # Replace with your actual MongoDB connection string
        connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client["tiktok_login"]
            # Test connection
            self.client.admin.command('ping')
            print("Connected to MongoDB successfully")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            # For testing without MongoDB, create a mock
            self.db = MockDB()

class MockDB:
    """Mock database for testing without MongoDB"""
    def __init__(self):
        self.collections = {}
    
    def __getitem__(self, collection_name):
        if collection_name not in self.collections:
            self.collections[collection_name] = MockCollection()
        return self.collections[collection_name]

class MockCollection:
    """Mock collection for testing"""
    def __init__(self):
        self.data = []
    
    def find_one(self, query):
        # Mock user data for testing
        if query.get("email"):
            return {
                "_id": "test_user_id",
                "email": query["email"],
                "social_account": [
                    {
                        "provider": "tiktok",
                        "provider_id": "test_tiktok_id",
                        "name": "Test User",
                        "token": "test_token",
                        "avatar": "https://example.com/avatar.jpg"
                    }
                ]
            }
        return None

connect = DatabaseConnection()
