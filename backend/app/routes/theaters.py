from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import math

theaters_bp = Blueprint('theaters', __name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["film_recommendation"]
theaters_collection = db["theaters"]
movies_collection = db["movies"]

@theaters_bp.route('/theaters', methods=['GET'])
def get_theaters():
    """Get all theaters or theaters near a location"""
    try:
        # Check if location parameters are provided
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        
        if lat and lng:
            # Get theaters near location
            max_distance = request.args.get('distance', default=20, type=int) * 1000  # Convert km to meters
            
            # Geospatial query
            query = {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lng, lat]
                        },
                        "$maxDistance": max_distance
                    }
                }
            }
            
            theaters = list(theaters_collection.find(query))
            
            # Calculate distance for each theater
            for theater in theaters:
                theater['_id'] = str(theater['_id'])
                
                # Calculate distance in kilometers
                theater_coords = theater['location']['coordinates']
                distance = calculate_distance(lat, lng, theater_coords[1], theater_coords[0])
                theater['distance'] = round(distance, 1)
                
                # Add movie details to each theater's current movies
                if 'current_movies' in theater:
                    for movie_item in theater['current_movies']:
                        movie_id = movie_item['movie_id']
                        try:
                            movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
                            if movie:
                                movie_item['movie_details'] = {
                                    '_id': str(movie['_id']),
                                    'title': movie['title'],
                                    'image_url': movie.get('image_url', ''),
                                    'year': movie.get('year', ''),
                                    'average_rating': movie.get('average_rating', 0)
                                }
                        except:
                            # If unable to convert to ObjectId, skip this movie
                            pass
                
        else:
            # Get all theaters
            theaters = list(theaters_collection.find())
            for theater in theaters:
                theater['_id'] = str(theater['_id'])
                
                # Add movie details to each theater's current movies
                if 'current_movies' in theater:
                    for movie_item in theater['current_movies']:
                        movie_id = movie_item['movie_id']
                        try:
                            movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
                            if movie:
                                movie_item['movie_details'] = {
                                    '_id': str(movie['_id']),
                                    'title': movie['title'],
                                    'image_url': movie.get('image_url', ''),
                                    'year': movie.get('year', ''),
                                    'average_rating': movie.get('average_rating', 0)
                                }
                        except:
                            # If unable to convert to ObjectId, skip this movie
                            pass
        
        return jsonify(theaters), 200
        
    except Exception as e:
        print(f"Error getting theaters: {str(e)}")
        return jsonify({'error': f'Failed to get theaters: {str(e)}'}), 500

@theaters_bp.route('/theaters/<theater_id>', methods=['GET'])
def get_theater(theater_id):
    """Get a specific theater by ID"""
    try:
        theater = theaters_collection.find_one({'_id': ObjectId(theater_id)})
        if not theater:
            return jsonify({'error': 'Theater not found'}), 404
            
        theater['_id'] = str(theater['_id'])
        
        # Get current movies with details
        if 'current_movies' in theater:
            for movie_item in theater['current_movies']:
                movie_id = movie_item['movie_id']
                try:
                    movie = movies_collection.find_one({'_id': ObjectId(movie_id)})
                    if movie:
                        movie_item['movie_details'] = {
                            '_id': str(movie['_id']),
                            'title': movie['title'],
                            'image_url': movie.get('image_url', ''),
                            'year': movie.get('year', ''),
                            'average_rating': movie.get('average_rating', 0),
                            'genres': movie.get('genres', [])
                        }
                except:
                    # If unable to convert to ObjectId, skip this movie
                    pass
        
        return jsonify(theater), 200
        
    except Exception as e:
        print(f"Error getting theater: {str(e)}")
        return jsonify({'error': f'Failed to get theater: {str(e)}'}), 500

@theaters_bp.route('/movies/<movie_id>/theaters', methods=['GET'])
def get_theaters_for_movie(movie_id):
    """Get theaters showing a specific movie"""
    try:
        # Check if location parameters are provided
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        
        # Base query to find theaters showing the movie
        query = {
            "current_movies.movie_id": str(movie_id)
        }
        
        if lat and lng:
            # Get theaters near location
            max_distance = request.args.get('distance', default=20, type=int) * 1000  # Convert km to meters
            
            # Add geospatial constraints to query
            query["location"] = {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "$maxDistance": max_distance
                }
            }
        
        theaters = list(theaters_collection.find(query))
        
        # Format response
        formatted_theaters = []
        for theater in theaters:
            # Basic theater info
            theater_data = {
                '_id': str(theater['_id']),
                'name': theater['name'],
                'address': theater['address'],
                'location': theater['location']
            }
            
            # Add distance if location was provided
            if lat and lng:
                theater_coords = theater['location']['coordinates']
                distance = calculate_distance(lat, lng, theater_coords[1], theater_coords[0])
                theater_data['distance'] = round(distance, 1)
            
            # Add showtimes for the requested movie
            for movie_item in theater['current_movies']:
                if movie_item['movie_id'] == str(movie_id):
                    theater_data['showtimes'] = movie_item.get('showtimes', [])
                    break
            
            formatted_theaters.append(theater_data)
        
        return jsonify(formatted_theaters), 200
        
    except Exception as e:
        print(f"Error getting theaters for movie: {str(e)}")
        return jsonify({'error': f'Failed to get theaters for movie: {str(e)}'}), 500

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    # Earth radius in kilometers
    earth_radius = 6371
    
    # Convert coordinates from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c
    
    return distance