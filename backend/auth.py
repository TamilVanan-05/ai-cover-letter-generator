from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.database import db, User, Profile, ActivityLog
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Helper to validate email format using regex."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Endpoint to handle user registration, password hashing, and auto profile generation."""
    data = request.get_json() or {}
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validations
    if not username or not email or not password:
        return jsonify({'error': 'Missing username, email, or password'}), 400
        
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
    if not validate_email(email):
        return jsonify({'error': 'Invalid email address format'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email address already registered'}), 400
        
    try:
        # Create User
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        # Set Admin role for first user or matching specific configurations
        if email.endswith('@aicoveradmin.com'):
            new_user.role = 'admin'
            
        db.session.add(new_user)
        db.session.flush() # Populate new_user.id
        
        # Initialize an empty profile for the user
        new_profile = Profile(
            user_id=new_user.id,
            full_name=username,
            email=email
        )
        db.session.add(new_profile)
        
        # Log activity
        log = ActivityLog(user_id=new_user.id, action="Register", details="User registered account successfully.")
        db.session.add(log)
        
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(identity=str(new_user.id))
        return jsonify({
            'message': 'User registered successfully!',
            'token': access_token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint for user login. Returns a JWT access token on success."""
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
        
    try:
        # Update user tokens / activity log
        log = ActivityLog(user_id=user.id, action="Login", details="User logged in successfully.")
        db.session.add(log)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'message': 'Login successful!',
            'token': access_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@auth_bp.route('/api/auth/user', methods=['GET'])
@jwt_required()
def get_current_user():
    """Gets the current authenticated user's credentials."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route('/api/auth/profile', methods=['GET', 'PUT'])
@jwt_required()
def user_profile():
    """GET user's professional profile, or PUT changes into database."""
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=int(user_id)).first()
    
    if not profile:
        # Auto-create profile if missing
        profile = Profile(user_id=int(user_id))
        db.session.add(profile)
        db.session.commit()
        
    if request.method == 'GET':
        return jsonify(profile.to_dict()), 200
        
    # PUT method
    data = request.get_json() or {}
    try:
        profile.full_name = data.get('full_name', profile.full_name)
        profile.email = data.get('email', profile.email)
        profile.phone = data.get('phone', profile.phone)
        profile.location = data.get('location', profile.location)
        profile.linkedin = data.get('linkedin', profile.linkedin)
        profile.portfolio = data.get('portfolio', profile.portfolio)
        
        profile.experience_years = int(data.get('experience_years', profile.experience_years or 0))
        profile.current_position = data.get('current_position', profile.current_position)
        profile.previous_position = data.get('previous_position', profile.previous_position)
        profile.industry = data.get('industry', profile.industry)
        
        # Multi line fields
        profile.achievements = data.get('achievements', profile.achievements)
        profile.skills = data.get('skills', profile.skills)
        profile.certifications = data.get('certifications', profile.certifications)
        profile.education = data.get('education', profile.education)
        profile.languages = data.get('languages', profile.languages)
        profile.projects = data.get('projects', profile.projects)
        
        # Log Profile update
        log = ActivityLog(user_id=int(user_id), action="Update Profile", details="Updated professional profile inputs.")
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully!', 'profile': profile.to_dict()}), 200
    except ValueError:
        return jsonify({'error': 'Invalid experience years format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Simulates sending a password reset link and email validation."""
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        # To prevent user enumeration, return a positive message even if email is missing.
        return jsonify({'message': 'If the email exists, a password reset link has been simulated.'}), 200
        
    # Simulate action
    log = ActivityLog(user_id=user.id, action="Forgot Password", details="Triggered email reset instructions.")
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Password reset verification code sent to email. Code is: 123456 (Dev sandbox simulation)',
        'dev_sandbox': True,
        'verification_code': '123456'
    }), 200


@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Resets the user's password using simulated validation codes."""
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    code = data.get('code', '').strip()
    new_password = data.get('new_password', '')
    
    if not email or not code or not new_password:
        return jsonify({'error': 'Email, verification code, and new password are required'}), 400
        
    if code != '123456':
        return jsonify({'error': 'Invalid verification code'}), 400
        
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    try:
        user.set_password(new_password)
        log = ActivityLog(user_id=user.id, action="Reset Password", details="Reset account password using reset token.")
        db.session.add(log)
        db.session.commit()
        return jsonify({'message': 'Password reset successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
