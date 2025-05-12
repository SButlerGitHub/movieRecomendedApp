rating_schema = {
    "user_id": str,        
    "movie_id": str,       
    "rating": float,    
    "review": str,         
    "created_at": str,     
    "updated_at": str,     
    "helpful_votes": int,  
    "tags": list           
}

def validate_rating(rating):
    # Validation function to check fields for a rating 
    required_fields = ["user_id", "movie_id", "rating"]
    for field in required_fields:
        if field not in rating:
            return False, f"Missing required field: {field}"
    
    # Rating value validation
    if not isinstance(rating["rating"], (int, float)) or rating["rating"] < 1 or rating["rating"] > 5:
        return False, "Rating must be a number between 1 and 5"
        
    return True, "Valid rating data"