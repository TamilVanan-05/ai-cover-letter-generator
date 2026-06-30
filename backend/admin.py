from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db, User, CoverLetter, ActivityLog, Feedback
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    """Decorator to verify that the authenticated JWT user is an administrator."""
    # We will load the user from db to verify role
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)


@admin_bp.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Aggregates SaaS metrics for administration visualizations (Chart.js dashboards)."""
    try:
        total_users = User.query.count()
        total_letters = CoverLetter.query.count()
        feedback_count = Feedback.query.count()
        
        # Calculate approximate AI tokens / credits used
        # We can sum default user starting credits versus total current credits
        total_credits_used = (total_users * 5) - db.session.query(func.sum(User.credits)).scalar()
        if total_credits_used is None or total_credits_used < 0:
            total_credits_used = 0
            
        # Get subscription splits
        sub_splits = db.session.query(User.subscription_status, func.count(User.id))\
            .group_by(User.subscription_status).all()
            
        sub_data = {status: count for status, count in sub_splits}
        
        # Activity breakdown for the past 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_generations = db.session.query(
            func.date(CoverLetter.date_created).label('date'),
            func.count(CoverLetter.id).label('count')
        ).filter(CoverLetter.date_created >= seven_days_ago)\
         .group_by(func.date(CoverLetter.date_created))\
         .order_by('date').all()
         
        gen_timeline = [{'date': str(row.date), 'count': row.count} for row in daily_generations]
        
        return jsonify({
            'total_users': total_users,
            'total_letters_generated': total_letters,
            'total_credits_used': total_credits_used,
            'feedback_received': feedback_count,
            'subscriptions': sub_data,
            'generation_timeline': gen_timeline
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve system statistics: {str(e)}'}), 500


@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Retrieves all registered accounts with credentials profile summary."""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([u.to_dict() for u in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Performs an administrative delete of a client user account and records."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if user.id == int(get_jwt_identity()):
            return jsonify({'error': 'You cannot delete your own administrative account'}), 400
            
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'User {user.username} deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/admin/feedback', methods=['GET'])
@admin_required
def get_feedback():
    """Retrieves all customer bug logs or improvement tickets."""
    try:
        feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
        return jsonify([f.to_dict() for f in feedbacks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/admin/feedback/<int:feedback_id>', methods=['DELETE'])
@admin_required
def delete_feedback(feedback_id):
    """Deletes feedback from the system admin panel."""
    try:
        fb = Feedback.query.get(feedback_id)
        if not fb:
            return jsonify({'error': 'Feedback entry not found'}), 404
        db.session.delete(fb)
        db.session.commit()
        return jsonify({'message': 'Feedback entry deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/admin/activities', methods=['GET'])
@admin_required
def get_system_activities():
    """Retrieves a timeline log of user events and actions."""
    try:
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(100).all()
        return jsonify([l.to_dict() for l in logs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
