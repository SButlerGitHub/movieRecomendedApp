from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from pymongo import MongoClient

# MongoDB Connection - Use the same connection as your other files
client = MongoClient("mongodb://localhost:27017/")
db = client["film_recommendation"]
users_collection = db["users"]
movies_collection = db["movies"]

watchlist_bp = Blueprint('watchlist', __name__)

@watchlist_bp.route('/users/watchlist', methods=['GET'])
@jwt_required()
def get_user_watchlist():
    """Get the current user's watchlist"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Get user's document
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get watchlist movie IDs (create if doesn't exist)
        watchlist_ids = user.get('watchlist', [])
        
        # Get movie details for each ID
        result = []
        for movie_id in watchlist_ids:
            try:
                movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
                
                if movie:
                    result.append({
                        'movie_id': movie_id,
                        'title': movie['title'],
                        'image_url': movie.get('image_url', ''),
                        'year': movie.get('year', ''),
                        'genres': movie.get('genres', []),
                        'director': movie.get('director', '')
                    })
            except Exception as e:
                print(f"Error processing movie {movie_id}: {str(e)}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error getting watchlist: {str(e)}")
        return jsonify({'error': f'Failed to get watchlist: {str(e)}'}), 500

@watchlist_bp.route('/users/watchlist/<movie_id>', methods=['POST'])
@jwt_required()
def add_to_watchlist(movie_id):
    """Add a movie to the user's watchlist"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Check if movie exists
        movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
            
        # Add to watchlist if not already in it
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$addToSet': {'watchlist': movie_id}}
        )
        
        if result.modified_count == 0:
            
            user = users_collection.find_one({
                '_id': ObjectId(user_id),
                'watchlist': movie_id
            })
            
            if user:
                return jsonify({'message': 'Movie already in watchlist'}), 200
            else:
                return jsonify({'error': 'Failed to update watchlist'}), 500
            
        return jsonify({'message': 'Movie added to watchlist successfully'}), 200
        
    except Exception as e:
        print(f"Error adding to watchlist: {str(e)}")
        return jsonify({'error': f'Failed to add to watchlist: {str(e)}'}), 500

@watchlist_bp.route('/users/watchlist/<movie_id>', methods=['DELETE'])
@jwt_required()
def remove_from_watchlist(movie_id):
    """Remove a movie from the user's watchlist"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Remove from watchlist
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$pull': {'watchlist': movie_id}}
        )
        
        if result.modified_count == 0:
            # Movie was not in watchlist or no update occurred
            return jsonify({'message': 'Movie was not in watchlist or no change made'}), 200
            
        return jsonify({'message': 'Movie removed from watchlist successfully'}), 200
        
    except Exception as e:
        print(f"Error removing from watchlist: {str(e)}")
        return jsonify({'error': f'Failed to remove from watchlist: {str(e)}'}), 500