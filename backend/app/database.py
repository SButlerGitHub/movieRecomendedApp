from pymongo import MongoClient  #libraries 
from app.config import MONGO_URI  


def get_database(): #function 
    client = MongoClient(MONGO_URI)
    return client.movie_recommendation_db

# function accessing the collections 
def get_collections():
    db = get_database()
    return {
        'users': db.users,
        'movies': db.movies,
        'ratings': db.ratings,
        'theaters': db.theaters,
        'reviews': db.ratings  
    } 