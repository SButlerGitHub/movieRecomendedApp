import unittest
import json
from unittest.mock import patch, MagicMock
import mongomock
from bson import ObjectId, json_util
from datetime import datetime, timedelta

from app.config import TestConfig
from main import app
from app.database import get_db
import jwt


class TestAPIRoutes(unittest.TestCase):
    """Test cases for API routes in the movie recommendation system."""
    
    def setUp(self):
        """Set up the test client and mock database."""
        # Configure the Flask app for testing
        app.config.from_object(TestConfig)
        self.client = app.test_client()
        
        # Setup mock MongoDB
        self.mongo_patch = patch('app.database.get_db')
        self.mock_db = self.mongo_patch.start()
        
        # Create a mongomock client
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client.test_db
        self.mock_db.return_value = self.db
        
        # Create sample test data
        self.create_test_data()
        
        # Create a valid auth token for testing protected routes
        self.auth_token = jwt.encode(
            {'sub': str(self.test_user_id), 'exp': datetime.utcnow() + timedelta(days=1)},
            app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
    def create_test_data(self):
        """Create sample data for testing."""
        # Create a test user
        self.test_user_id = ObjectId()
        self.test_user = {
            "_id": self.test_user_id,
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "pbkdf2:sha256:150000$abc123$abcdef1234567890abcdef1234567890",
            "created_at": datetime.now(),
            "watchlist": []
        }
        self.db.users.insert_one(self.test_user)
        
        # Create test movies
        self.test_movies = []
        for i in range(5):
            movie = {
                "_id": ObjectId(),
                "title": f"Test Movie {i}",
                "overview": f"This is test movie {i}",
                "release_date": "2023-01-01",
                "genres": ["Action", "Adventure"] if i % 2 == 0 else ["Comedy", "Drama"],
                "poster_path": f"/path/to/poster{i}.jpg",
                "tmdb_id": 10000 + i,
                "vote_average": 7.5 + (i * 0.1)
            }
            self.test_movies.append(movie)
        
        self.db.movies.insert_many(self.test_movies)
        
        # Create test ratings
        self.test_ratings = []
        for i, movie in enumerate(self.test_movies):
            rating = {
                "_id": ObjectId(),
                "user_id": self.test_user_id,
                "movie_id": movie["_id"],
                "rating": 4.0 if i % 2 == 0 else 3.0,
                "timestamp": datetime.now()
            }
            self.test_ratings.append(rating)
        
        self.db.ratings.insert_many(self.test_ratings)
        
        # Create test theaters
        self.test_theaters = []
        for i in range(3):
            theater = {
                "_id": ObjectId(),
                "name": f"Test Theater {i}",
                "location": {
                    "type": "Point",
                    "coordinates": [-73.9857 + (i * 0.01), 40.7484 + (i * 0.01)]
                },
                "address": f"{i+1}23 Test Street, Test City",
                "place_id": f"ChIJN1t_tDeuEmsR{i}",
                "movies_showing": [self.test_movies[i]["_id"] for i in range(min(i+2, 5))]
            }
            self.test_theaters.append(theater)
        
        self.db.theaters.insert_many(self.test_theaters)
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop the MongoDB mock patch
        self.mongo_patch.stop()
        # Drop the test database
        self.mongo_client.drop_database('test_db')

    def test_get_movies_route(self):
        """Test the GET /api/v1.0/movies endpoint."""
        response = self.client.get('/api/v1.0/movies')
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check that we got movies back
        self.assertIn('movies', data)
        self.assertEqual(len(data['movies']), 5)  # All test movies
        
        # Check for pagination info
        self.assertIn('pagination', data)
    
    def test_get_movie_by_id_route(self):
        """Test the GET /api/v1.0/movies/<id> endpoint."""
        # Get a test movie ID
        movie_id = str(self.test_movies[0]["_id"])
        
        response = self.client.get(f'/api/v1.0/movies/{movie_id}')
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the response
        data = json.loads(response.data)
        
        
        self.assertIn('movie', data)
        self.assertEqual(data['movie']['title'], "Test Movie 0")
    
    def test_get_nonexistent_movie(self):
        """Test requesting a movie that doesn't exist."""
        fake_id = str(ObjectId())
        
        response = self.client.get(f'/api/v1.0/movies/{fake_id}')
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
    
    def test_search_movies_route(self):
        """Test the GET /api/v1.0/movies/search endpoint."""
        # Search for movies with "Test" in the title
        response = self.client.get('/api/v1.0/movies/search?query=Test')
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the response
        data = json.loads(response.data)
        
        # find all test movies
        self.assertIn('movies', data)
        self.assertEqual(len(data['movies']), 5)
        
        # Search for a specific movie
        response = self.client.get('/api/v1.0/movies/search?query=Test Movie 1')
        data = json.loads(response.data)
        self.assertEqual(len(data['movies']), 1)
        self.assertEqual(data['movies'][0]['title'], "Test Movie 1")
    
    def test_login_route(self):
        """Test the POST /api/v1.0/auth/login endpoint."""
        # Mock the password check
        with patch('werkzeug.security.check_password_hash', return_value=True):
            response = self.client.post(
                '/api/v1.0/auth/login',
                json={'username': 'testuser', 'password': 'password123'}
            )
            
            # Check status code
            self.assertEqual(response.status_code, 200)
            
            # Parse the response
            data = json.loads(response.data)
            
            # return a token
            self.assertIn('token', data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Mock the password check to fail
        with patch('werkzeug.security.check_password_hash', return_value=False):
            response = self.client.post(
                '/api/v1.0/auth/login',
                json={'username': 'testuser', 'password': 'wrongpassword'}
            )
            
            # Should return 401 Unauthorized
            self.assertEqual(response.status_code, 401)
    
    def test_protected_route_with_valid_token(self):
        """Test accessing a protected route with a valid token."""
        response = self.client.get(
            '/api/v1.0/users/profile',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        
        self.assertEqual(response.status_code, 200)
    
    def test_protected_route_without_token(self):
        """Test accessing a protected route without a token."""
        response = self.client.get('/api/v1.0/users/profile')
        
        # return 401 Unauthorized
        self.assertEqual(response.status_code, 401)
    
    def test_protected_route_with_invalid_token(self):
        """Test accessing a protected route with an invalid token."""
        response = self.client.get(
            '/api/v1.0/users/profile',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, 401)
    
    def test_register_route(self):
        """Test the POST /api/v1.0/auth/register endpoint."""
        # New user data
        new_user = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        }
        
        # Mock the password hash
        with patch('werkzeug.security.generate_password_hash', return_value='hashed_password'):
            response = self.client.post(
                '/api/v1.0/auth/register',
                json=new_user
            )
            
            # Check status code
            self.assertEqual(response.status_code, 201)
            
            # New user should be in database
            db_user = self.db.users.find_one({'username': 'newuser'})
            self.assertIsNotNone(db_user)
            self.assertEqual(db_user['email'], 'new@example.com')
    
    def test_register_duplicate_username(self):
        """Test registration with an existing username."""
        # Try to register with existing username
        user_data = {
            'username': 'testuser',  
            'email': 'another@example.com',
            'password': 'password123'
        }
        
        response = self.client.post(
            '/api/v1.0/auth/register',
            json=user_data
        )
        
        # Should return conflict error
        self.assertEqual(response.status_code, 409)
    
    def test_get_recommendations_route(self):
        """Test the GET /api/v1.0/recommendations endpoint."""
        # Mock the recommendation function
        with patch('app.routes.recommendation.get_recommendations') as mock_get_recs:
            # Setup mock return value
            mock_movies = [self.test_movies[i] for i in range(3)]
            mock_get_recs.return_value = mock_movies
            
            response = self.client.get(
                '/api/v1.0/recommendations',
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            # Check status code
            self.assertEqual(response.status_code, 200)
            
            # Parse the response
            data = json.loads(response.data)
            
            # Should return recommendations
            self.assertIn('recommendations', data)
            self.assertEqual(len(data['recommendations']), 3)
    
    def test_rate_movie_route(self):
        """Test the POST /api/v1.0/movies/<id>/rate endpoint."""
        movie_id = str(self.test_movies[0]["_id"])
        
        response = self.client.post(
            f'/api/v1.0/movies/{movie_id}/rate',
            json={'rating': 4.5},
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check that rating was updated in database
        rating = self.db.ratings.find_one({
            'user_id': self.test_user_id,
            'movie_id': self.test_movies[0]["_id"]
        })
        
        self.assertIsNotNone(rating)
        self.assertEqual(rating['rating'], 4.5)
    
    def test_get_theaters_route(self):
        """Test the GET /api/v1.0/theaters endpoint."""
        response = self.client.get('/api/v1.0/theaters')
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the response
        data = json.loads(response.data)
        
        # Should return theaters
        self.assertIn('theaters', data)
        self.assertEqual(len(data['theaters']), 3)  # All test theaters
    
    def test_get_theater_by_id_route(self):
        """Test the GET /api/v1.0/theaters/<id> endpoint."""
        theater_id = str(self.test_theaters[0]["_id"])
        
        response = self.client.get(f'/api/v1.0/theaters/{theater_id}')
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the response
        data = json.loads(response.data)
        
        # Should return the theater
        self.assertIn('theater', data)
        self.assertEqual(data['theater']['name'], "Test Theater 0")
    
    def test_watchlist_routes(self):
        """Test the watchlist endpoints."""
        # Add a movie to watchlist
        movie_id = str(self.test_movies[0]["_id"])
        
        response = self.client.post(
            f'/api/v1.0/users/watchlist/{movie_id}',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Get watchlist
        response = self.client.get(
            '/api/v1.0/users/watchlist',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the response
        data = json.loads(response.data)
        
        # Should have one movie in watchlist
        self.assertIn('watchlist', data)
        self.assertEqual(len(data['watchlist']), 1)
        self.assertEqual(data['watchlist'][0]['_id'], movie_id)
        
        # Remove movie from watchlist
        response = self.client.delete(
            f'/api/v1.0/users/watchlist/{movie_id}',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Watchlist should be empty
        updated_user = self.db.users.find_one({'_id': self.test_user_id})
        self.assertEqual(len(updated_user['watchlist']), 0)
    
    def test_get_user_ratings_route(self):
        """Test the GET /api/v1.0/users/ratings endpoint."""
        response = self.client.get(
            '/api/v1.0/users/ratings',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the response
        data = json.loads(response.data)
        
        # return ratings
        self.assertIn('ratings', data)
        self.assertEqual(len(data['ratings']), 5)  # All test ratings
    
    def test_locations_nearby_theaters_route(self):
        """Test the GET /api/v1.0/location/theaters endpoint."""
        # Mock the Google Places API integration
        with patch('app.routes.location.find_nearby_theaters') as mock_find_theaters:
            # Setup mock return value
            mock_find_theaters.return_value = self.test_theaters
            
            response = self.client.get(
                '/api/v1.0/location/theaters?lat=40.7484&lng=-73.9857&radius=5000'
            )
            
            # Check status code
            self.assertEqual(response.status_code, 200)
            
            # Parse the response
            data = json.loads(response.data)
            
            # return theaters
            self.assertIn('theaters', data)
            self.assertEqual(len(data['theaters']), 3)


if __name__ == "__main__":
    unittest.main()