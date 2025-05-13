import unittest
from datetime import datetime
from bson import ObjectId
from app.models.user import User
from app.models.movie import Movie
from app.models.ratings import Rating
from app.models.theater import Theater
from pymongo import MongoClient
from app.config import TestConfig
import mongomock


class TestModels(unittest.TestCase):
    """Test cases for data models in the movie recommendation system."""
    
    def setUp(self):
        """Set up test environment before each test."""
        
        self.client = mongomock.MongoClient()
        self.db = self.client.test_database
        
        # Sample data for testing
        self.user_data = {
            "_id": ObjectId(),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "created_at": datetime.now(),
            "watchlist": [ObjectId(), ObjectId()],
            "preferences": {"genres": ["Action", "Sci-Fi"]}
        }
        
        self.movie_data = {
            "_id": ObjectId(),
            "title": "Test Movie",
            "overview": "A test movie for unit testing",
            "release_date": "2023-01-01",
            "genres": ["Action", "Adventure"],
            "poster_path": "/path/to/poster.jpg",
            "tmdb_id": 12345,
            "runtime": 120,
            "vote_average": 7.5
        }
        
        self.rating_data = {
            "_id": ObjectId(),
            "user_id": self.user_data["_id"],
            "movie_id": self.movie_data["_id"],
            "rating": 4.5,
            "timestamp": datetime.now()
        }
        
        self.theater_data = {
            "_id": ObjectId(),
            "name": "Test Theater",
            "location": {
                "type": "Point",
                "coordinates": [-73.9857, 40.7484]
            },
            "address": "123 Test Street, Test City",
            "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
            "movies_showing": [self.movie_data["_id"]]
        }
    
    def test_user_model_creation(self):
        """Test creating a User model instance."""
        user = User(self.user_data)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(len(user.watchlist), 2)
        self.assertEqual(user.preferences["genres"], ["Action", "Sci-Fi"])
    
    def test_user_model_validation(self):
        """Test validation in User model."""
        # Test with invalid email
        invalid_user_data = self.user_data.copy()
        invalid_user_data["email"] = "invalid-email"
        with self.assertRaises(ValueError):
            User(invalid_user_data)
        
        # Test with missing required field
        invalid_user_data = self.user_data.copy()
        del invalid_user_data["username"]
        with self.assertRaises(KeyError):
            User(invalid_user_data)
    
    def test_movie_model_creation(self):
        """Test creating a Movie model instance."""
        movie = Movie(self.movie_data)
        self.assertEqual(movie.title, "Test Movie")
        self.assertEqual(movie.tmdb_id, 12345)
        self.assertEqual(len(movie.genres), 2)
        self.assertEqual(movie.runtime, 120)
    
    def test_movie_model_year_extraction(self):
        """Test extracting year from release_date."""
        movie = Movie(self.movie_data)
        self.assertEqual(movie.year, 2023)
        
        # Test with missing release_date
        movie_data_no_date = self.movie_data.copy()
        del movie_data_no_date["release_date"]
        movie = Movie(movie_data_no_date)
        self.assertIsNone(movie.year)
    
    def test_rating_model_creation(self):
        """Test creating a Rating model instance."""
        rating = Rating(self.rating_data)
        self.assertEqual(rating.rating, 4.5)
        self.assertEqual(rating.user_id, self.user_data["_id"])
        self.assertEqual(rating.movie_id, self.movie_data["_id"])
    
    def test_rating_model_validation(self):
        """Test validation in Rating model."""
        # Test with invalid rating value (too high)
        invalid_rating_data = self.rating_data.copy()
        invalid_rating_data["rating"] = 6.0
        with self.assertRaises(ValueError):
            Rating(invalid_rating_data)
        
        # Test with invalid rating value (too low)
        invalid_rating_data["rating"] = -1.0
        with self.assertRaises(ValueError):
            Rating(invalid_rating_data)
    
    def test_theater_model_creation(self):
        """Test creating a Theater model instance."""
        theater = Theater(self.theater_data)
        self.assertEqual(theater.name, "Test Theater")
        self.assertEqual(theater.address, "123 Test Street, Test City")
        self.assertEqual(len(theater.movies_showing), 1)
    
    def test_theater_location_validation(self):
        """Test validation of geolocation data in Theater model."""
        # Test with invalid coordinates 
        invalid_theater_data = self.theater_data.copy()
        invalid_theater_data["location"]["coordinates"] = [-200, 100]  
        with self.assertRaises(ValueError):
            Theater(invalid_theater_data)
    
    def test_user_to_dict_method(self):
        """Test User.to_dict() method for serialization."""
        user = User(self.user_data)
        user_dict = user.to_dict()
        
        # Check that password hash
        self.assertNotIn("password_hash", user_dict)
        self.assertEqual(user_dict["username"], "testuser")
        self.assertEqual(user_dict["email"], "test@example.com")
    
    def test_movie_to_dict_method(self):
        """Test Movie.to_dict() method for serialization."""
        movie = Movie(self.movie_data)
        movie_dict = movie.to_dict()
        
        self.assertEqual(movie_dict["title"], "Test Movie")
        self.assertEqual(movie_dict["tmdb_id"], 12345)
        self.assertIn("year", movie_dict)
    
    def test_user_check_password(self):
        """Test User.check_password method."""
        # Create a fresh user with a real password hash
        from werkzeug.security import generate_password_hash
        
        user_data = self.user_data.copy()
        password = "test_password"
        user_data["password_hash"] = generate_password_hash(password)
        
        user = User(user_data)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password("wrong_password"))
    
    def test_movie_get_similar(self):
        """Test Movie.get_similar method that would use content-based similarity."""
        movie = Movie(self.movie_data)
        
        # database connection
        db = self.db
        db.movies.insert_many([
            self.movie_data,
            {
                "_id": ObjectId(),
                "title": "Similar Movie",
                "genres": ["Action", "Adventure"],
                "tmdb_id": 12346
            },
            {
                "_id": ObjectId(),
                "title": "Different Movie",
                "genres": ["Comedy", "Romance"],
                "tmdb_id": 12347
            }
        ])
        
        # queries the database
        
        similar_movies = movie.get_similar(db, limit=5)
        
        # return a list of movie objects
        self.assertIsInstance(similar_movies, list)
    
    def tearDown(self):
        """Clean up after each test."""
        self.client.drop_database("test_database")


if __name__ == "__main__":
    unittest.main()