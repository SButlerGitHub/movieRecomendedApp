from app.database import get_database, get_collections
from app.models.movie import validate_movie
from app.models.user import validate_user

def test_database_connection():
    db = get_database()
    assert db is not None, "Database connection failed"
    print("Database connection successful")

def test_collections_access():
    collections = get_collections()
    for name, collection in collections.items():
        assert collection is not None, f"Failed to access {name} collection"
    print("All collections accessible")

if __name__ == "__main__":
    test_database_connection()
    test_collections_access()