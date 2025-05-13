import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from bson import ObjectId
from datetime import datetime


from app.algorithms.content_based import ContentBasedRecommender
from app.algorithms.collaborative_filtering import CollaborativeFilteringRecommender
from app.algorithms.hybrid import HybridRecommender

# Import database models
from app.models.movie import Movie
from app.models.user import User
from app.models.ratings import Rating

# For database testing
import mongomock


class TestRecommendationAlgorithms(unittest.TestCase):
    """Test cases for movie recommendation algorithms."""

    def setUp(self):
        """Set up test data for recommendation algorithms."""
        
        self.client = mongomock.MongoClient()
        self.db = self.client.test_database
        
        # Sample users
        self.users = [
            {
                "_id": ObjectId(),
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password_hash": "hashed_password",
                "preferences": {"genres": ["Action", "Sci-Fi"] if i % 2 == 0 else ["Comedy", "Drama"]}
            } for i in range(10)
        ]
        
        # Sample movies with different genres
        self.movies = [
            {
                "_id": ObjectId(),
                "title": f"Action Movie {i}",
                "overview": f"An action-packed movie {i}",
                "genres": ["Action", "Adventure"],
                "release_date": "2023-01-01",
                "poster_path": f"/path/to/poster{i}.jpg",
                "tmdb_id": 10000 + i,
                "vote_average": 7.5,
                "keywords": ["hero", "explosion", "fight"]
            } for i in range(5)
        ] + [
            {
                "_id": ObjectId(),
                "title": f"Comedy Movie {i}",
                "overview": f"A hilarious comedy {i}",
                "genres": ["Comedy"],
                "release_date": "2023-02-01",
                "poster_path": f"/path/to/poster{i+5}.jpg",
                "tmdb_id": 20000 + i,
                "vote_average": 8.0,
                "keywords": ["funny", "laugh", "humor"]
            } for i in range(5)
        ] + [
            {
                "_id": ObjectId(),
                "title": f"Sci-Fi Movie {i}",
                "overview": f"A futuristic sci-fi movie {i}",
                "genres": ["Sci-Fi"],
                "release_date": "2023-03-01",
                "poster_path": f"/path/to/poster{i+10}.jpg",
                "tmdb_id": 30000 + i,
                "vote_average": 8.5,
                "keywords": ["future", "space", "technology"]
            } for i in range(5)
        ]
        
       
        self.ratings = []
        for i, user in enumerate(self.users):
            
            for movie in self.movies:
                
                if i % 2 == 0:
                    if "Action" in movie["genres"] or "Sci-Fi" in movie["genres"]:
                        rating_value = 4.5
                    else:
                        rating_value = 2.0
                
                else:
                    if "Comedy" in movie["genres"]:
                        rating_value = 4.5
                    else:
                        rating_value = 2.0
                        
                self.ratings.append({
                    "_id": ObjectId(),
                    "user_id": user["_id"],
                    "movie_id": movie["_id"],
                    "rating": rating_value,
                    "timestamp": datetime.now()
                })
        
        # Insert test data into mock database
        self.db.users.insert_many(self.users)
        self.db.movies.insert_many(self.movies)
        self.db.ratings.insert_many(self.ratings)
        
        
        self.content_based = ContentBasedRecommender(self.db)
        self.collaborative = CollaborativeFilteringRecommender(self.db)
        self.hybrid = HybridRecommender(self.db)

    def test_content_based_movie_similarity(self):
        """Test that content-based similarity works correctly based on movie features."""
        # Get two action movies
        action_movie_1 = self.movies[0]
        action_movie_2 = self.movies[1]
        
        # Get a comedy movie
        comedy_movie = self.movies[5]
        
        # Calculate similarity between two action movies
        similarity_action = self.content_based._calculate_movie_similarity(
            Movie(action_movie_1), Movie(action_movie_2)
        )
        
        # Calculate similarity between action and comedy movies
        similarity_different = self.content_based._calculate_movie_similarity(
            Movie(action_movie_1), Movie(comedy_movie)
        )
        
        # Action movies should be more similar to each other than to comedy movies
        self.assertGreater(similarity_action, similarity_different)

    def test_content_based_recommendations(self):
        """Test that content-based recommendations match user preferences."""
        # Get an 'action/sci-fi' preferring user
        action_user = User(self.users[0])
        
        # Get a 'comedy' preferring user
        comedy_user = User(self.users[1])
        
        # Get recommendations for action user
        action_user_recs = self.content_based.recommend(action_user._id, limit=5)
        
        # Get recommendations for comedy user
        comedy_user_recs = self.content_based.recommend(comedy_user._id, limit=5)
        
        # Count genre occurrences in recommendations
        action_genres_count = sum(1 for movie in action_user_recs 
                                if "Action" in movie.genres or "Sci-Fi" in movie.genres)
        comedy_genres_count = sum(1 for movie in comedy_user_recs if "Comedy" in movie.genres)
        
        # Action user should get maction/sci-fi recommendations
        self.assertGreaterEqual(action_genres_count, 3)
        
        # Comedy user should get comedy recommendations
        self.assertGreaterEqual(comedy_genres_count, 3)

    def test_collaborative_filtering_similarity(self):
        """Test that collaborative filtering correctly identifies similar users."""
        # Get two users with similar preferences 
        similar_user_1 = self.users[0]["_id"]
        similar_user_2 = self.users[2]["_id"]
        
        # Get two users with different preferences 
        different_user_1 = self.users[0]["_id"]
        different_user_2 = self.users[1]["_id"]
        
        # Get similarity scores
        similarity_same = self.collaborative._calculate_user_similarity(similar_user_1, similar_user_2)
        similarity_different = self.collaborative._calculate_user_similarity(different_user_1, different_user_2)
        
        # Users with similar preferences should have higher similarity
        self.assertGreater(similarity_same, similarity_different)

    def test_collaborative_filtering_recommendations(self):
        """Test that collaborative filtering provides appropriate recommendations."""
        # Get recommendations for an action/sci-fi preferring user
        action_user_id = self.users[0]["_id"]
        action_user_recs = self.collaborative.recommend(action_user_id, limit=5)
        
        # Action user should get mostly action/sci-fi recommendations
        action_genres_count = sum(1 for movie in action_user_recs 
                                if "Action" in movie.genres or "Sci-Fi" in movie.genres)
        
        self.assertGreaterEqual(action_genres_count, 3)
        
        # The recommendations should not include movies the user has already rated
        rated_movie_ids = [r["movie_id"] for r in self.ratings if r["user_id"] == action_user_id]
        rec_movie_ids = [movie._id for movie in action_user_recs]
        
        
        self.assertEqual(len(set(rated_movie_ids).intersection(set(rec_movie_ids))), 0)

    def test_hybrid_recommendation_combination(self):
        """Test that hybrid recommendations combine results from both algorithms."""
        
        self.hybrid.content_based = MagicMock()
        self.hybrid.collaborative = MagicMock()
        
        # Setup mock return values
        mock_movies = [Movie(self.movies[i]) for i in range(5)]
        self.hybrid.content_based.recommend.return_value = mock_movies[:3]  # First 3 movies
        self.hybrid.collaborative.recommend.return_value = mock_movies[2:]  # Last 3 movies (with overlap)
        
        # Get hybrid recommendations
        user_id = self.users[0]["_id"]
        hybrid_recs = self.hybrid.recommend(user_id, limit=5)
        
        
        self.hybrid.content_based.recommend.assert_called_once()
        self.hybrid.collaborative.recommend.assert_called_once()
        
        
        self.assertLessEqual(len(hybrid_recs), 5)
        
        
        rec_movie_ids = [movie._id for movie in hybrid_recs]
        content_movie_ids = [movie._id for movie in self.hybrid.content_based.recommend.return_value]
        collab_movie_ids = [movie._id for movie in self.hybrid.collaborative.recommend.return_value]
        
        self.assertTrue(any(mid in content_movie_ids for mid in rec_movie_ids))
        self.assertTrue(any(mid in collab_movie_ids for mid in rec_movie_ids))

    def test_recommendation_with_no_ratings(self):
        """Test recommendation behavior for users with no ratings."""
        # Create a new user with no ratings
        new_user = {
            "_id": ObjectId(),
            "username": "newuser",
            "email": "newuser@example.com",
            "password_hash": "hashed_password",
            "preferences": {"genres": ["Action"]}
        }
        self.db.users.insert_one(new_user)
        
        # Get recommendations for new user
        content_recs = self.content_based.recommend(new_user["_id"], limit=5)
        
        
        self.assertGreaterEqual(len(content_recs), 1)
        
        # Check if recommendations match user's genre preferences
        action_count = sum(1 for movie in content_recs if "Action" in movie.genres)
        self.assertGreaterEqual(action_count, 1)

    def test_recommendation_with_genre_filter(self):
        """Test that recommendations can be filtered by genre."""
        # Get recommendations for an action/sci-fi
        user_id = self.users[0]["_id"]
        genre_filter = ["Sci-Fi"]
        
        sci_fi_recs = self.content_based.recommend(
            user_id, limit=5, genre_filter=genre_filter
        )
        
        # All recommendations should be Sci-Fi movies
        for movie in sci_fi_recs:
            self.assertIn("Sci-Fi", movie.genres)

    def test_recommendation_diversity(self):
        """Test that recommendations have some diversity."""
        # Get a larger number of recommendations
        user_id = self.users[0]["_id"]
        recommendations = self.hybrid.recommend(user_id, limit=10)
        
        
        all_genres = []
        for movie in recommendations:
            all_genres.extend(movie.genres)
        unique_genres = set(all_genres)
        
        
        self.assertGreater(len(unique_genres), 1)

    def tearDown(self):
        """Clean up after each test."""
        self.client.drop_database("test_database")


if __name__ == "__main__":
    unittest.main()