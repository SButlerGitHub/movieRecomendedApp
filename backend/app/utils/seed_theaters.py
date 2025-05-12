import sys
import os
import pymongo
from datetime import datetime, timedelta
from bson import ObjectId
import random


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def seed_theaters():
    """Seed the database with sample theater data"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["film_recommendation"]
        theaters_collection = db["theaters"]
        movies_collection = db["movies"]
        
        # Get all movie IDs
        movies = list(movies_collection.find({}, {"_id": 1, "title": 1}))
        if not movies:
            print("No movies found in the database. Please run seed_movies.py first.")
            return False
            
        # Convert ObjectId to string
        movie_data = [{"id": str(movie["_id"]), "title": movie["title"]} for movie in movies]
        
        # Sample Belfast theaters with location data
        theaters = [
            {
                "name": "Odeon Belfast",
                "location": {
                    "type": "Point",
                    "coordinates": [-5.9302, 54.5973]  # [longitude, latitude]
                },
                "address": {
                    "street": "Victoria Square Shopping Centre, 1 Victoria Sq",
                    "city": "Belfast",
                    "state": "Northern Ireland",
                    "postal_code": "BT1 4QG",
                    "country": "UK"
                },
                "contact": {
                    "phone": "0333 006 7777",
                    "email": "info@odeon.co.uk",
                    "website": "https://www.odeon.co.uk/cinemas/belfast/"
                },
                "current_movies": generate_current_movies(movie_data[:5]),
                "amenities": ["IMAX", "Parking", "Wheelchair Access", "Food Court"],
                "rating": 4.2
            },
            {
                "name": "Movie House Dublin Road",
                "location": {
                    "type": "Point",
                    "coordinates": [-5.9337, 54.5946]
                },
                "address": {
                    "street": "14 Dublin Rd",
                    "city": "Belfast",
                    "state": "Northern Ireland",
                    "postal_code": "BT2 7HN",
                    "country": "UK"
                },
                "contact": {
                    "phone": "028 9024 5700",
                    "email": "info@moviehouse.co.uk",
                    "website": "https://www.moviehouse.co.uk/"
                },
                "current_movies": generate_current_movies(movie_data[2:7]),
                "amenities": ["Parking", "Wheelchair Access", "Snack Bar"],
                "rating": 4.0
            },
            {
                "name": "Cineworld Belfast",
                "location": {
                    "type": "Point",
                    "coordinates": [-5.9243, 54.6012]
                },
                "address": {
                    "street": "42 High St",
                    "city": "Belfast",
                    "state": "Northern Ireland",
                    "postal_code": "BT1 2BE",
                    "country": "UK"
                },
                "contact": {
                    "phone": "0330 333 4444",
                    "email": "customer.services@cineworld.co.uk",
                    "website": "https://www.cineworld.co.uk/"
                },
                "current_movies": generate_current_movies(movie_data[1:6]),
                "amenities": ["4DX", "ScreenX", "Parking", "Wheelchair Access", "Restaurant"],
                "rating": 4.3
            },
            {
                "name": "Queen's Film Theatre",
                "location": {
                    "type": "Point",
                    "coordinates": [-5.9341, 54.5845]
                },
                "address": {
                    "street": "20 University Square",
                    "city": "Belfast",
                    "state": "Northern Ireland",
                    "postal_code": "BT7 1PA",
                    "country": "UK"
                },
                "contact": {
                    "phone": "028 9097 1097",
                    "email": "info@qft.org.uk",
                    "website": "https://queensfilmtheatre.com/"
                },
                "current_movies": generate_current_movies(movie_data[3:8]),
                "amenities": ["Art House Films", "Wheelchair Access", "Cafe"],
                "rating": 4.5
            },
            {
                "name": "IMC Cinema",
                "location": {
                    "type": "Point",
                    "coordinates": [-5.9213, 54.5899]
                },
                "address": {
                    "street": "Kennedy Centre, 564-568 Falls Rd",
                    "city": "Belfast",
                    "state": "Northern Ireland",
                    "postal_code": "BT11 9AE",
                    "country": "UK"
                },
                "contact": {
                    "phone": "028 9024 3772",
                    "email": "info@imccinemas.co.uk",
                    "website": "https://www.imccinemas.co.uk/"
                },
                "current_movies": generate_current_movies(movie_data[:5]),
                "amenities": ["Parking", "Wheelchair Access", "Concessions"],
                "rating": 3.9
            }
        ]
        
        # Clear existing theaters
        theaters_collection.delete_many({})
        
        # Insert theaters
        theaters_collection.insert_many(theaters)
        print(f"Successfully inserted {len(theaters)} theaters")
        
        # Create index for geospatial queries
        theaters_collection.create_index([("location", pymongo.GEOSPHERE)])
        print("Created geospatial index for theaters collection")
        
        return True
    except Exception as e:
        print(f"Error seeding theaters: {str(e)}")
        return False

def generate_current_movies(movies):
    """Generate random showtimes for movies"""
    current_date = datetime.now()
    current_movies = []
    
    for movie in movies:
        # Generate 3-5 random showtimes for the next 7 days
        showtimes = []
        for day in range(7):
            show_date = current_date + timedelta(days=day)
            # Generate 2-4 showtimes per day
            num_showtimes = random.randint(2, 4)
            
            for _ in range(num_showtimes):
                # Generate random hour between 12:00 and 22:00
                hour = random.randint(12, 22)
                # Generate random minute (0, 15, 30, 45)
                minute = random.choice([0, 15, 30, 45])
                
                show_time = show_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                showtimes.append(show_time.strftime("%Y-%m-%d %H:%M"))
        
        current_movies.append({
            "movie_id": movie["id"],
            "showtimes": sorted(showtimes)
        })
    
    return current_movies

if __name__ == "__main__":
    seed_theaters()