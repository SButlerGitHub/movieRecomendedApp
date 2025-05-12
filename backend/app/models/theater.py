from app.database import get_collections
from bson import ObjectId


#theaters collection
theater_schema = {
    "name": str,           # Name of the theater
    "location": {
        "type": "Point",
        "coordinates": list  # [longitude, latitude]
    },
    "address": {
        "street": str,
        "city": str,
        "state": str,
        "postal_code": str,
        "country": str
    },
    "contact": {
        "phone": str,
        "email": str,
        "website": str
    },
    "current_movies": [     # Movies currently showing
        {
            "movie_id": str,  # Reference to movie collection
            "showtimes": list  # List of datetime strings for showtimes
        }
    ],
    "amenities": list,      # List of amenities
    "rating": float,        # Average user rating for the theater
    "distance": float       # This can be calculated based on user location
}

def validate_theater(theater):
    # Validation function
    required_fields = ["name", "location", "address"]
    for field in required_fields:
        if field not in theater:
            return False, f"Missing required field: {field}"
    
    # Location validation function 
    if "location" in theater:
        if "type" not in theater["location"] or theater["location"]["type"] != "Point":
            return False, "Location must have type: 'Point'"
        if "coordinates" not in theater["location"] or len(theater["location"]["coordinates"]) != 2:
            return False, "Location must have valid coordinates [longitude, latitude]"
    
    return True, "Valid theater data"

def create_indexes():
    collections = get_collections()
    
    # Create geospatial index for theaters collection
    collections['theaters'].create_index([("location", "2dsphere")])
    print("Created geospatial index for theaters collection")

    # Create indexes for faster queries
    collections['ratings'].create_index([("user_id", 1), ("movie_id", 1)], unique=True)
    collections['movies'].create_index([("title", 1)])
    print("Created additional indexes for performance") 


def get_theaters_near_location(longitude, latitude, max_distance=20000):
    """
    Find theaters within a radius (in meters) of a given location
    Default is 20km 
    """
    theaters = get_collections()['theaters']
    
    # MongoDB geospatial query
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": max_distance
            }
        }
    }
    
    return list(theaters.find(query))

def get_theaters_showing_movie(movie_id, longitude=None, latitude=None, max_distance=None):
    """
    Find theaters showing a specific movie
    Filter by location if coordinates are provided
    """
    theaters = get_collections()['theaters']
    
    # Base query to find theaters showing the movie
    query = {
        "current_movies.movie_id": str(movie_id)
    }
    
    # Add location filter if coordinates are provided
    if longitude is not None and latitude is not None and max_distance is not None:
        query["location"] = {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": max_distance
            }
        }
    
    return list(theaters.find(query))