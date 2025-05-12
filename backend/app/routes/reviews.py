from flask import Blueprint, request, jsonify
from app.database import get_collections
from bson import ObjectId


#blueprint for the routes
reviews_bp = Blueprint('reviews', __name__)


# Get reviews for a movie
@reviews_bp.route('/movies/<movie_id>/reviews', methods=['GET'])
def get_movie_reviews(movie_id):
    try:
        collections = get_collections()
        ratings = collections['ratings']
        
        # Find all ratings for this movie that have a review
        reviews = list(ratings.find({
            'movie_id': movie_id,
            'review': {'$exists': True, '$ne': ''}
        }))
        
        # Format the reviews for the frontend
        formatted_reviews = []
        for review in reviews:
            # Get username from users collection
            user = collections['users'].find_one({'_id': ObjectId(review['user_id'])})
            username = user['username'] if user else 'Anonymous'
            
            formatted_reviews.append({
                'id': str(review['_id']),
                'username': username,
                'rating': review['rating'],
                'review': review['review'],
                'created_at': review.get('created_at', datetime.datetime.now())
            })
            
        return jsonify(formatted_reviews)
    except Exception as e:
        print(f"Error getting movie reviews: {e}")
        return jsonify({'error': 'Failed to load reviews'}), 500


@reviews_bp.route('/movies/<movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    try:
        # Check if user is authenticated
        
        user_id = request.user_id  
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
            
        data = request.json
        rating = data.get('rating')
        review = data.get('review', '')
        
        if not rating or not isinstance(rating, (int, float)):
            return jsonify({'error': 'Valid rating required'}), 400
            
        collections = get_collections()
        ratings = collections['ratings']
        
        # Check if user already rated this movie
        existing_rating = ratings.find_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
        
        now = datetime.datetime.now()
        
        if existing_rating:
            # Update existing rating
            ratings.update_one(
                {'_id': existing_rating['_id']},
                {'$set': {
                    'rating': rating,
                    'review': review,
                    'updated_at': now
                }}
            )
        else:
            # Create new rating
            ratings.insert_one({
                'user_id': user_id,
                'movie_id': movie_id,
                'rating': rating,
                'review': review,
                'created_at': now,
                'updated_at': now
            })
            
        # Update average rating in movies collection
        all_ratings = list(ratings.find({'movie_id': movie_id}))
        avg_rating = sum(r['rating'] for r in all_ratings) / len(all_ratings) if all_ratings else 0
        
        collections['movies'].update_one(
            {'_id': ObjectId(movie_id)},
            {'$set': {'average_rating': avg_rating}}
        )
        
        return jsonify({'success': True, 'message': 'Rating submitted successfully'})
    except Exception as e:
        print(f"Error rating movie: {e}")
        return jsonify({'error': 'Failed to submit rating'}), 500

# Get user rating for a movie
@reviews_bp.route('/movies/<movie_id>/user-rating', methods=['GET'])
def get_user_movie_rating(movie_id):
    try:
        # Check if user is authenticated
        user_id = request.user_id  
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
            
        collections = get_collections()
        ratings = collections['ratings']
        
        user_rating = ratings.find_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
        
        if not user_rating:
            return jsonify({'error': 'User has not rated this movie'}), 404
            
        return jsonify({
            'id': str(user_rating['_id']),
            'rating': user_rating['rating'],
            'review': user_rating.get('review', ''),
            'created_at': user_rating.get('created_at')
        })
    except Exception as e:
        print(f"Error getting user rating: {e}")
        return jsonify({'error': 'Failed to get user rating'}), 500

