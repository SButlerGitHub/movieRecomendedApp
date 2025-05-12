#movie collection
movie_schema = {
    "title": str,
    "description": str,
    "genres": list,  # List of genre strings
    "year": int,
    "director": str,
    "cast": list,    # List of actor names
    "image_url": str,
    "streaming_platforms": list,  # Where the movie is available to stream
    "average_rating": float
}

def validate_movie(movie): #validation function used to check a movie is valid
    
    required_fields = ["title", "year", "genres"]
    for field in required_fields:
        if field not in movie:
            return False, f"Missing required field: {field}"
    return True, "Valid movie data" 