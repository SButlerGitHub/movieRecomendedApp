from flask import Blueprint, jsonify
from bson import ObjectId
import pymongo

# Create blueprint
movies_bp = Blueprint('movies', __name__)

# Connect to MongoDB directly
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["film_recommendation"]
movies_collection = db["movies"]

@movies_bp.route('/movies', methods=['GET'])
def get_movies():
    try:
        # Get all movies from database
        movies = list(movies_collection.find({}))
        
        # Convert ObjectId to string for JSON serialization
        for movie in movies:
            movie['_id'] = str(movie['_id'])
            
        return jsonify(movies), 200
        
    except Exception as e:
        print(f"Error getting movies: {str(e)}")
        return jsonify({'error': 'Failed to get movies'}), 500

@movies_bp.route('/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    try:
        # Get movie by ID
        movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
            
        # Convert ObjectId to string 
        movie['_id'] = str(movie['_id'])
            
        return jsonify(movie), 200
        
    except Exception as e:
        print(f"Error getting movie: {str(e)}")
        return jsonify({'error': 'Failed to get movie'}), 500