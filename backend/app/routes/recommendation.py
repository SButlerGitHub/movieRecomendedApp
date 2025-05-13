from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from pymongo import MongoClient  

client = MongoClient("mongodb://localhost:27017/")
db = client["film_recommendation"]
users_collection = db["users"]
movies_collection = db["movies"]
ratings_collection = db["ratings"]

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized movie recommendations for the current user"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Generate recommendations based on user preferences
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user or 'preferences' not in user:
            # If user has no preferences, return top-rated movies
            pipeline = [
                {
                    '$lookup': {
                        'from': 'ratings',
                        'localField': '_id',
                        'foreignField': 'movie_id',
                        'as': 'ratings'
                    }
                },
                {
                    '$addFields': {
                        'ratings_count': {'$size': '$ratings'},
                        'average_rating': {'$avg': '$ratings.rating'}
                    }
                },
                {
                    '$match': {
                        'ratings_count': {'$gte': 3}
                    }
                },
                {
                    '$sort': {
                        'average_rating': -1,
                        'ratings_count': -1
                    }
                },
                {
                    '$limit': 10
                }
            ]
            
            recommended_movies = list(movies_collection.aggregate(pipeline))
        else:
            # Get user's already rated movies
            user_ratings = list(ratings_collection.find({'user_id': user_id}))
            rated_movie_ids = [ObjectId(rating['movie_id']) for rating in user_ratings]
            
            # Get user's preferences
            preferred_genres = user['preferences'].get('genres', [])
            preferred_directors = user['preferences'].get('directors', [])
            preferred_actors = user['preferences'].get('actors', [])
            
            # Find movies matching user preferences that user hasn't rated
            query = {
                '_id': {'$nin': rated_movie_ids}
            }
            
            # Add preference filters if available
            if preferred_genres:
                query['genres'] = {'$in': preferred_genres}
            
            if preferred_directors:
                query['director'] = {'$in': preferred_directors}
            
            
            
            # Find matching movies
            matching_movies = list(movies_collection.find(query).limit(20))
            
            # Score movies based on preference match
            scored_movies = []
            for movie in matching_movies:
                score = 0
                
                # Add score for genre matches
                for genre in movie.get('genres', []):
                    if genre in preferred_genres:
                        score += 1
                
                # Add score for director match (higher weight)
                if movie.get('director') in preferred_directors:
                    score += 3
                
                # Add score for actor matches
                for actor in movie.get('cast', []):
                    if actor in preferred_actors:
                        score += 2
                
                movie['preference_score'] = score
                scored_movies.append(movie)
            
            # Sort by preference score, descending
            recommended_movies = sorted(scored_movies, key=lambda x: x.get('preference_score', 0), reverse=True)[:10]
        
        # Format response
        result = []
        for movie in recommended_movies:
            result.append({
                'movie_id': str(movie['_id']),
                'title': movie['title'],
                'image_url': movie.get('image_url', ''),
                'year': movie.get('year', ''),
                'genres': movie.get('genres', []),
                'director': movie.get('director', ''),
                'average_rating': movie.get('average_rating', 0),
                'match_score': movie.get('preference_score', 0)
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return jsonify({'error': f'Failed to generate recommendations: {str(e)}'}), 500

@recommendation_bp.route('/recommendations/genre/<genre>', methods=['GET'])
def get_genre_recommendations(genre):
    """Get recommendations for a specific genre"""
    try:
        # Find movies in this genre
        pipeline = [
            {
                '$match': {
                    'genres': genre
                }
            },
            {
                '$lookup': {
                    'from': 'ratings',
                    'localField': '_id',
                    'foreignField': 'movie_id',
                    'as': 'ratings'
                }
            },
            {
                '$addFields': {
                    'average_rating': {'$avg': '$ratings.rating'},
                    'ratings_count': {'$size': '$ratings'}
                }
            },
            {
                '$match': {
                    'ratings_count': {'$gte': 1}
                }
            },
            {
                '$sort': {'average_rating': -1}
            },
            {
                '$limit': 10
            }
        ]
        
        genre_movies = list(movies_collection.aggregate(pipeline))
        
        # Format response
        result = []
        for movie in genre_movies:
            result.append({
                'movie_id': str(movie['_id']),
                'title': movie['title'],
                'image_url': movie.get('image_url', ''),
                'year': movie.get('year', ''),
                'genres': movie.get('genres', []),
                'director': movie.get('director', ''),
                'average_rating': movie.get('average_rating', 0)
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error generating genre recommendations: {str(e)}")
        return jsonify({'error': f'Failed to generate genre recommendations: {str(e)}'}), 500