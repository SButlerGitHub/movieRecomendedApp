from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta



def create_app():
    app = Flask(__name__)

    # Config
    app.config['JWT_SECRET_KEY'] = 'secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

    # Initialize JWT
    jwt = JWTManager(app)
    
    # Enable CORS for all routes with all origins
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Properly scoped imports
    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    from app.routes.ratings import ratings_bp
    from app.routes.theaters import theaters_bp
    from app.routes.watchlist import watchlist_bp
    from app.routes.recommendation import recommendation_bp
    from app.routes.location import location_bp
    from app.routes.reviews import reviews_bp


    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movies_bp, url_prefix='/api')
    app.register_blueprint(ratings_bp, url_prefix='/api')
    app.register_blueprint(theaters_bp, url_prefix='/api')
    app.register_blueprint(watchlist_bp, url_prefix='/api')
    app.register_blueprint(recommendation_bp, url_prefix='/api')
    app.register_blueprint(location_bp, url_prefix='/api')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    


    # Test route to check if API is working
    @app.route('/api/test')
    def test_connection():
        return jsonify({'message': 'Backend connection successful!'})

    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome to the Film Finder API!'})

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
