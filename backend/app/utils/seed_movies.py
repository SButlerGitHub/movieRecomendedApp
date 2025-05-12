import sys
import os
import pymongo
from bson import ObjectId

# Add parent directory 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def seed_movies():
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["film_recommendation"]
        movies_collection = db["movies"]
        
        # Sample movie data with proper ObjectIds
        sample_movies = [
            {
                "_id": ObjectId(),
                "title": "The Shawshank Redemption",
                "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                "genres": ["Drama"],
                "year": 1994,
                "director": "Frank Darabont",
                "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/8/81/ShawshankRedemptionMoviePoster.jpg",
                "average_rating": 4.7,
                "streaming_platforms": ["Netflix", "Amazon Prime"]
            },
            {
                "_id": ObjectId(),
                "title": "The Godfather",
                "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                "genres": ["Crime", "Drama"],
                "year": 1972,
                "director": "Francis Ford Coppola",
                "cast": ["Marlon Brando", "Al Pacino", "James Caan"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_ver1.jpg",
                "average_rating": 4.8,
                "streaming_platforms": ["HBO Max"]
            },
            {
                "_id": ObjectId(),
                "title": "The Dark Knight",
                "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                "genres": ["Action", "Crime", "Drama"],
                "year": 2008,
                "director": "Christopher Nolan",
                "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/1/1c/The_Dark_Knight_%282008_film%29.jpg",
                "average_rating": 4.6,
                "streaming_platforms": ["Netflix", "HBO Max"]
            },
            {
                "_id": ObjectId(),
                "title": "Pulp Fiction",
                "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
                "genres": ["Crime", "Drama"],
                "year": 1994,
                "director": "Quentin Tarantino",
                "cast": ["John Travolta", "Samuel L. Jackson", "Uma Thurman"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/3/3b/Pulp_Fiction_%281994%29_poster.jpg",
                "average_rating": 4.5,
                "streaming_platforms": ["Amazon Prime"]
            },
            {
                "_id": ObjectId(),
                "title": "The Lord of the Rings: The Return of the King",
                "description": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring.",
                "genres": ["Adventure", "Drama", "Fantasy"],
                "year": 2003,
                "director": "Peter Jackson",
                "cast": ["Elijah Wood", "Viggo Mortensen", "Ian McKellen"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/b/be/The_Lord_of_the_Rings_-_The_Return_of_the_King_%282003%29.jpg",
                "average_rating": 4.9,
                "streaming_platforms": ["HBO Max", "Amazon Prime"]
            },
            {
                "_id": ObjectId(),
                "title": "Inception",
                "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                "genres": ["Action", "Adventure", "Sci-Fi"],
                "year": 2010,
                "director": "Christopher Nolan",
                "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg",
                "average_rating": 4.4,
                "streaming_platforms": ["Netflix"]
            },
            {
                "_id": ObjectId(),
                "title": "The Matrix",
                "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
                "genres": ["Action", "Sci-Fi"],
                "year": 1999,
                "director": "Lana Wachowski, Lilly Wachowski",
                "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg",
                "average_rating": 4.3,
                "streaming_platforms": ["HBO Max"]
            },
            {
                "_id": ObjectId(),
                "title": "Parasite",
                "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                "genres": ["Comedy", "Drama", "Thriller"],
                "year": 2019,
                "director": "Bong Joon Ho",
                "cast": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong"],
                "image_url": "https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png",
                "average_rating": 4.6,
                "streaming_platforms": ["Amazon Prime", "Hulu"]
            }
        ]
        
        # Clear existing movies
        movies_collection.delete_many({})
        
        # Insert sample movies
        movies_collection.insert_many(sample_movies)
        print(f"Successfully inserted {len(sample_movies)} movies into the database")
        
        # Print movie titles that were inserted
        for movie in sample_movies:
            print(f"- {movie['title']} ({movie['year']})")
            
        return True
    except Exception as e:
        print(f"Error seeding movies: {str(e)}")
        return False

if __name__ == "__main__":
    seed_movies()