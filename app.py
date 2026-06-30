import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import Config
from backend.database import db, User, Profile

def create_app():
    """Application factory for the Flask app."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load Configuration
    app.config.from_object(Config)
    
    # Initialize Database
    db.init_app(app)
    
    # Initialize JWT Manager
    jwt = JWTManager(app)
    
    # Register JWT error handlers for clean JSON responses
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({'error': 'Missing or invalid token. Please log in.'}), 401
        
    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired. Please log in again.'}), 401

    # Register Blueprints
    from backend.auth import auth_bp
    from backend.admin import admin_bp
    from backend.routes import routes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(routes_bp)
    
    # Database Initialization & Admin Setup
    with app.app_context():
        db.create_all()
        
        # Check if an admin user already exists, if not, create one
        admin_email = "admin@aicoveradmin.com"
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            try:
                admin = User(
                    username="System Administrator",
                    email=admin_email,
                    role="admin",
                    subscription_status="Enterprise",
                    credits=999
                )
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.flush()
                
                # Initialize empty profile for admin
                admin_profile = Profile(
                    user_id=admin.id,
                    full_name="System Administrator",
                    email=admin_email
                )
                db.session.add(admin_profile)
                db.session.commit()
                print("Default administrator account created successfully! Username: admin@aicoveradmin.com, Password: admin123")
            except Exception as e:
                db.session.rollback()
                print(f"Failed to create default admin account: {e}")
                
    return app

app = create_app()

if __name__ == '__main__':
    # Retrieve port from configurations
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
