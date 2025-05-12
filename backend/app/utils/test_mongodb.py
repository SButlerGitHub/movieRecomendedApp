import sys
import os
import pymongo

# Add parent directory 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mongodb_connection():
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        
        # Print available databases
        print("Connected to MongoDB!")
        print("Available databases:", client.list_database_names())
        
        # Create film_recommendation database if it doesn't exist
        db = client["film_recommendation"]
        print(f"Using database: {db.name}")
        
        # Create collections if they don't exist
        collections = ["users", "movies", "ratings", "theaters"]
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
            else:
                print(f"Collection already exists: {collection_name}")
        
        # Print collection stats
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"Collection '{collection_name}' has {count} documents")
            
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()