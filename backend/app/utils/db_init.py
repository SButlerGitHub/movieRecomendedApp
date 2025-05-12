from app.database import get_collections
import json
from pathlib import Path

def load_sample_data():
    collections = get_collections()
    
    # Load sample movies
    sample_path = Path(__file__).parent.parent / "data" / "sample_movies.json"
    with open(sample_path, 'r') as f:
        movies = json.load(f)
        # Clear existing data
        collections['movies'].delete_many({})
        # Insert sample data if collection is empty
        if collections['movies'].count_documents({}) == 0:
            collections['movies'].insert_many(movies)
            print(f"Inserted {len(movies)} sample movies") 