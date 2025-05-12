from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId
from app.utils import generate_reset_token, send_reset_email


# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Connect to MongoDB directly
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["film_recommendation"]
users_collection = db["users"]
ratings_collection = db["ratings"]
movies_collection = db["movies"]

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # Get user data from request
        data = request.get_json()
        print(f"Received registration data: {data}")
        
        # Validate required fields
        if not all(key in data for key in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check if user exists
        if users_collection.find_one({'email': data['email']}):
            return jsonify({'error': 'User already exists'}), 400
            
        # Create user document
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password_hash': generate_password_hash(data['password']),
            'preferences': {
                'genres': [],
                'directors': [],
                'actors': []
            },
            'watch_history': [],
            'created_at': datetime.now().isoformat()
        }
        
        # Insert user into database
        result = users_collection.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        # Create JWT token
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(days=7)
        )
        
        # Prepare user response (exclude password)
        user_response = {
            'id': user_id,
            'username': user_data['username'],
            'email': user_data['email']
        }
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': user_response
        }), 201
        
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # Get login data
        data = request.get_json()
        print(f"Received login data: {data}")
        
        # Validate required fields
        if not all(key in data for key in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
            
        # Find user by email
        user = users_collection.find_one({'email': data['email']})
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
            
        # Check password
        if not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
            
        # Create JWT token
        access_token = create_access_token(
            identity=str(user['_id']),
            expires_delta=timedelta(days=7)
        )
        
        # Prepare user response
        user_response = {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email']
        }
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user_response
        }), 200
        
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500



@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        
        # Find user by ID
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's ratings to derive preferences
        ratings = list(ratings_collection.find({'user_id': user_id}))
        
        # Initialize preferences if not exists
        if 'preferences' not in user:
            user['preferences'] = {
                'genres': [],
                'directors': [],
                'actors': []
            }
        
        # Derive preferences from ratings if user has rated movies
        if ratings:
            # Track counts for each preference
            genre_counts = {}
            director_counts = {}
            actor_counts = {}
            
            # Get movies user has rated highly (4+ stars)
            high_ratings = [r for r in ratings if r['rating'] >= 4]
            for rating in high_ratings:
                try:
                    movie = movies_collection.find_one({'_id': ObjectId(rating['movie_id'])})
                    if movie:
                        # Count genres
                        for genre in movie.get('genres', []):
                            if genre in genre_counts:
                                genre_counts[genre] += 1
                            else:
                                genre_counts[genre] = 1
                        
                        # Count directors
                        director = movie.get('director')
                        if director:
                            if director in director_counts:
                                director_counts[director] += 1
                            else:
                                director_counts[director] = 1
                        
                        # Count actors
                        for actor in movie.get('cast', [])[:3]:  # Use top 3 actors from each movie
                            if actor in actor_counts:
                                actor_counts[actor] += 1
                            else:
                                actor_counts[actor] = 1
                except Exception as e:
                    print(f"Error processing movie {rating['movie_id']}: {str(e)}")
            
            # Sort preferences by count and take top items
            sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
            sorted_directors = sorted(director_counts.items(), key=lambda x: x[1], reverse=True)
            sorted_actors = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Store preference counts
            user['preferences']['genre_counts'] = genre_counts
            user['preferences']['director_counts'] = director_counts
            user['preferences']['actor_counts'] = actor_counts
            
            # Get top preferences (limiting to top 5 of each)
            user['preferences']['genres'] = [genre for genre, _ in sorted_genres[:5]]
            user['preferences']['directors'] = [director for director, _ in sorted_directors[:5]]
            user['preferences']['actors'] = [actor for actor, _ in sorted_actors[:5]]
            
            # Update user preferences in database
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'preferences': user['preferences']}}
            )
        
        # Format user data for response
        user_data = {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'preferences': user['preferences'],
            'created_at': user.get('created_at', '')
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        return jsonify({'error': f'Failed to get user profile: {str(e)}'}), 500



@auth_bp.route('/users/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        username = data.get('username')
        email = data.get('email')

        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400

        # Check if email is taken
        email = email.lower()

        existing_user = users_collection.find_one({
            'email': email,
            '_id': {'$ne': ObjectId(user_id)}  
        })
        if existing_user:
            return jsonify({'error': 'Email is already taken'}), 400

        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'username': username,
                'email': email,
                'updated_at': datetime.now()
            }}
        )

        updated_user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not updated_user:
            return jsonify({'error': 'User not found'}), 404

        if 'password' in updated_user:
            updated_user.pop('password')

        updated_user['_id'] = str(updated_user['_id'])

        return jsonify(updated_user)
    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500



@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password_request():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'message': 'If an account with that email exists, a password reset link has been sent'}), 200

        reset_token = generate_reset_token()

        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {
                'reset_token': reset_token,
                'reset_token_expiry': datetime.datetime.now() + datetime.timedelta(hours=1)
            }}
        )

        send_reset_email(email, reset_token)

        return jsonify({'message': 'If an account with that email exists, a password reset link has been sent'}), 200
    except Exception as e:
        print(f"Error requesting password reset: {e}")
        return jsonify({'error': 'Failed to request password reset'}), 500

