import requests
from app.config import GOOGLE_PLACES_API_KEY 

def get_additional_theater_info(theater_name, location):
    """
    Fetch additional theater information from Google Places API
    """
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = f"{theater_name} cinema {location['city']}"
    
    params = {
        'query': query,
        'key': GOOGLE_PLACES_API_KEY
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            place = results[0]
            return {
                'place_id': place.get('place_id'),
                'rating': place.get('rating'),
                'user_ratings_total': place.get('user_ratings_total'),
                'photos': place.get('photos', []),
                'formatted_address': place.get('formatted_address')
            }
    
    return None