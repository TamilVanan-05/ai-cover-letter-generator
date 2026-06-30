from datetime import datetime
import secrets
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User accounts table storing authentication, roles, and SaaS credits."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    subscription_status = db.Column(db.String(50), default='Free Tier')  # 'Free Tier', 'Premium Pro', 'Enterprise'
    credits = db.Column(db.Integer, default=5)  # Generation credits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    cover_letters = db.relationship('CoverLetter', backref='user', lazy=True, cascade="all, delete-orphan")
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hashes and sets the user password."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verifies the hashed password."""
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        """Serializes user info for JSON output."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'subscription_status': self.subscription_status,
            'credits': self.credits,
            'created_at': self.created_at.isoformat()
        }


class Profile(db.Model):
    """Candidate professional details used to build the cover letter."""
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Personal Info
    full_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(150), nullable=True)
    portfolio = db.Column(db.String(150), nullable=True)
    
    # Professional Details
    experience_years = db.Column(db.Integer, default=0)
    current_position = db.Column(db.String(100), nullable=True)
    previous_position = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    
    # Text Blocks (stored as text/JSON lists)
    achievements = db.Column(db.Text, nullable=True)  # Line separated or bullet points
    skills = db.Column(db.Text, nullable=True)        # Comma separated
    certifications = db.Column(db.Text, nullable=True) # Comma separated
    education = db.Column(db.Text, nullable=True)     # Markdown / Text
    languages = db.Column(db.Text, nullable=True)     # Comma separated
    projects = db.Column(db.Text, nullable=True)      # Markdown / Text

    def to_dict(self):
        """Serializes user profile details."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name or '',
            'email': self.email or '',
            'phone': self.phone or '',
            'location': self.location or '',
            'linkedin': self.linkedin or '',
            'portfolio': self.portfolio or '',
            'experience_years': self.experience_years or 0,
            'current_position': self.current_position or '',
            'previous_position': self.previous_position or '',
            'industry': self.industry or '',
            'achievements': self.achievements or '',
            'skills': self.skills or '',
            'certifications': self.certifications or '',
            'education': self.education or '',
            'languages': self.languages or '',
            'projects': self.projects or ''
        }


class CoverLetter(db.Model):
    """Saved cover letters, corresponding input criteria, and ATS reports."""
    __tablename__ = 'cover_letters'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Info
    title = db.Column(db.String(100), nullable=False, default="Untitled Cover Letter")
    template_name = db.Column(db.String(50), nullable=False, default="modern")
    writing_style = db.Column(db.String(50), nullable=False, default="professional")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Job specifics input
    job_title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    hiring_manager = db.Column(db.String(100), nullable=True)
    job_description = db.Column(db.Text, nullable=False)
    job_location = db.Column(db.String(100), nullable=True)
    employment_type = db.Column(db.String(50), nullable=True)
    salary = db.Column(db.String(50), nullable=True)
    
    # AI Output
    content = db.Column(db.Text, nullable=False)
    
    # ATS Evaluator Results
    ats_score = db.Column(db.Integer, default=0)
    keywords_matched = db.Column(db.Text, nullable=True) # JSON list
    missing_skills = db.Column(db.Text, nullable=True)   # JSON list
    readability = db.Column(db.Integer, default=0)       # 0 - 100
    grammar_status = db.Column(db.String(50), default="Needs Review")
    action_verbs_count = db.Column(db.Integer, default=0)
    suggestions = db.Column(db.Text, nullable=True)      # JSON list
    
    # Metadata
    is_favorite = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(64), unique=True, default=lambda: secrets.token_hex(16))
    
    def to_dict(self):
        """Serializes cover letter record details."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'template_name': self.template_name,
            'writing_style': self.writing_style,
            'date_created': self.date_created.isoformat(),
            'date_updated': self.date_updated.isoformat(),
            'job_title': self.job_title,
            'company_name': self.company_name,
            'hiring_manager': self.hiring_manager or '',
            'job_description': self.job_description,
            'job_location': self.job_location or '',
            'employment_type': self.employment_type or '',
            'salary': self.salary or '',
            'content': self.content,
            'ats_score': self.ats_score,
            'keywords_matched': self.keywords_matched or '[]',
            'missing_skills': self.missing_skills or '[]',
            'readability': self.readability,
            'grammar_status': self.grammar_status,
            'action_verbs_count': self.action_verbs_count,
            'suggestions': self.suggestions or '[]',
            'is_favorite': self.is_favorite,
            'share_token': self.share_token
        }


class ActivityLog(db.Model):
    """User operations logging for dashboard history and auditing."""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }


class Feedback(db.Model):
    """System suggestions and reports filed by SaaS consumers."""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }
