import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask configuration
FLASK_APP = os.getenv('FLASK_APP', 'app.py')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key-change-in-production')

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/movie_recommendation_db')

# API keys for external services
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

# JWT settings
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-key-change-in-production')
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour in seconds

# Recommendation system settings
RECOMMENDATION_MIN_RATINGS = int(os.getenv('RECOMMENDATION_MIN_RATINGS', 5))
RECOMMENDATION_SIMILARITY_THRESHOLD = float(os.getenv('RECOMMENDATION_SIMILARITY_THRESHOLD', 0.3))

# Email config

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_SERVER = os.getenv('EMAIL_SERVER')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Other application settings
ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max upload

# Flask-specific configuration dictionary
flask_config = {
    'SECRET_KEY': SECRET_KEY,
    'DEBUG': DEBUG,
    'MAX_CONTENT_LENGTH': MAX_CONTENT_LENGTH,
}

