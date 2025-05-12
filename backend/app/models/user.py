#users collection
user_schema = {
    "username": str,
    "email": str,
    "password_hash": str,
    "preferences": {
        "genres": list,
        "directors": list,
        "actors": list
    },
    "watch_history": list,  # List of movie IDs
    "created_at": str  # Date when user account was created 
}

def validate_user(user):
    # Validation function to check user has the required fields 
    required_fields = ["username", "email", "password_hash"]
    for field in required_fields:
        if field not in user:
            return False, f"Missing required field: {field}"
    return True, "Valid user data"