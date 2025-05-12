from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

ratings_bp = Blueprint('ratings', __name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["film_recommendation"]
ratings_collection = db["ratings"]
movies_collection = db["movies"]
users_collection = db["users"]

@ratings_bp.route('/movies/<movie_id>/rate', methods=['POST'])
@jwt_required()
def rate_movie(movie_id):
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Get rating data
        data = request.get_json()
        if 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400
            
        # Validate rating
        rating = float(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if movie exists
        movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404
            
        # Check if user exists
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Check if user has already rated this movie
        existing_rating = ratings_collection.find_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
        
        now = datetime.now().isoformat()
        
        if existing_rating:
            # Update existing rating
            ratings_collection.update_one(
                {'_id': existing_rating['_id']},
                {'$set': {
                    'rating': rating,
                    'updated_at': now
                }}
            )
        else:
            # Create new rating
            rating_data = {
                'user_id': user_id,
                'movie_id': movie_id,
                'rating': rating,
                'created_at': now,
                'updated_at': now
            }
            ratings_collection.insert_one(rating_data)
            
        # Update movie's average rating
        update_movie_average_rating(movie_id)
        
        # Get updated movie to return new average rating
        updated_movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
        new_average_rating = updated_movie.get('average_rating', 0)
        
        return jsonify({
            'message': 'Rating submitted successfully',
            'movie_id': movie_id,
            'rating': rating,
            'new_average_rating': new_average_rating
        }), 200
        
    except Exception as e:
        print(f"Error rating movie: {str(e)}")
        return jsonify({'error': f'Failed to rate movie: {str(e)}'}), 500
        
def update_movie_average_rating(movie_id):
    """Update a movie's average rating based on all user ratings"""
    # Get all ratings for the movie
    ratings = list(ratings_collection.find({'movie_id': movie_id}))
    
    if not ratings:
        return
        
    # Calculate average rating
    total_rating = sum(r['rating'] for r in ratings)
    average_rating = round(total_rating / len(ratings), 1)
    
    # Update movie with new average rating
    movies_collection.update_one(
        {'_id': ObjectId(movie_id)},
        {'$set': {'average_rating': average_rating}}
    )

@ratings_bp.route('/users/ratings', methods=['GET'])
@jwt_required()
def get_user_ratings():
    """Get all ratings by the current user"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Get user's ratings
        user_ratings = list(ratings_collection.find({'user_id': user_id}))
        
        # Get movie details for each rating
        result = []
        for rating in user_ratings:
            movie_id = rating['movie_id']
            try:
                movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
                
                if movie:
                    result.append({
                        'rating_id': str(rating['_id']),
                        'movie_id': movie_id,
                        'rating': rating['rating'],
                        'created_at': rating.get('created_at', ''),
                        'movie_title': movie['title'],
                        'movie_image': movie.get('image_url', ''),
                        'movie_year': movie.get('year', ''),
                        'genres': movie.get('genres', []),
                        'director': movie.get('director', '')
                    })
            except Exception as e:
                print(f"Error processing rating {rating['_id']}: {str(e)}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error getting user ratings: {str(e)}")
        return jsonify({'error': f'Failed to get user ratings: {str(e)}'}), 500

@ratings_bp.route('/movies/<movie_id>/ratings', methods=['GET'])
def get_movie_ratings(movie_id):
    """Get all ratings for a specific movie"""
    try:
        ratings = list(ratings_collection.find({'movie_id': movie_id}))
        
        # Format ratings for response
        formatted_ratings = []
        for rating in ratings:
            # Get user details
            user_id = rating['user_id']
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            
            if user:
                formatted_ratings.append({
                    'rating_id': str(rating['_id']),
                    'rating': rating['rating'],
                    'created_at': rating.get('created_at', ''),
                    'user_id': user_id,
                    'username': user.get('username', 'Anonymous')
                })
        
        return jsonify(formatted_ratings), 200
        
    except Exception as e:
        print(f"Error getting movie ratings: {str(e)}")
        return jsonify({'error': f'Failed to get movie ratings: {str(e)}'}), 500

@ratings_bp.route('/users/ratings/<rating_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(rating_id):
    """Delete a user's rating"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Find the rating
        rating = ratings_collection.find_one({
            '_id': ObjectId(rating_id),
            'user_id': user_id  # Ensure the rating belongs to the user
        })
        
        if not rating:
            return jsonify({'error': 'Rating not found or not authorized to delete'}), 404
            
        # Get the movie ID before deleting the rating
        movie_id = rating['movie_id']
        
        # Delete the rating
        ratings_collection.delete_one({'_id': ObjectId(rating_id)})
        
        # Update the movie's average rating
        update_movie_average_rating(movie_id)
        
        return jsonify({'message': 'Rating deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting rating: {str(e)}")
        return jsonify({'error': f'Failed to delete rating: {str(e)}'}), 500