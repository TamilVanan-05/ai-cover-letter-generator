from flask import Blueprint, render_template, request, jsonify, send_file, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db, User, Profile, CoverLetter, ActivityLog, Feedback
from backend.ai_engine import generate_cover_letter, improve_text
from backend.ats_engine import analyze_ats
from backend.export_engine import create_docx_file, send_cover_letter_email
import json

routes_bp = Blueprint('routes', __name__)

# --- WEB PAGE ROUTES ---

@routes_bp.route('/')
def landing_page():
    """Renders the main product marketing landing page."""
    return render_template('landing.html')


@routes_bp.route('/login')
def login_page():
    """Renders login, registration, and password reset form."""
    return render_template('login.html')


@routes_bp.route('/dashboard')
def dashboard_page():
    """Renders the SaaS dashboard workspace."""
    return render_template('dashboard.html')


@routes_bp.route('/admin')
def admin_page():
    """Renders the administrator panel."""
    return render_template('admin.html')


@routes_bp.route('/share/<token>')
def public_share_page(token):
    """Renders a public read-only page of the cover letter styled in its selected template."""
    letter = CoverLetter.query.filter_by(share_token=token).first()
    if not letter:
        abort(404, description="Cover Letter not found")
        
    user = User.query.get(letter.user_id)
    profile = Profile.query.filter_by(user_id=user.id).first()
    
    # Render a clean, standalone cover letter preview styled according to the template
    return render_template('share.html', letter=letter, profile=profile)


# --- REST API ENDPOINTS ---

@routes_bp.route('/api/cover-letter/generate', methods=['POST'])
@jwt_required()
def api_generate_letter():
    """Creates a new cover letter record by compiling profile inputs and job descriptions."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Check subscription credit balance
    if user.credits <= 0 and user.subscription_status == 'Free Tier':
        return jsonify({
            'error': 'Insufficient credits. Please upgrade your subscription package to gain unlimited access.',
            'out_of_credits': True
        }), 402
        
    data = request.get_json() or {}
    
    # We expect candidate details and job details in the payload. 
    # If not provided, we extract them from the user's Profile record.
    profile_data = data.get('profile', {})
    job_details = data.get('job_details', {})
    writing_style = data.get('writing_style', 'professional')
    template_name = data.get('template_name', 'modern')
    title = data.get('title', f"Cover Letter for {job_details.get('company_name', 'Company')}")
    
    # If profile_data is not provided, load from db
    db_profile = Profile.query.filter_by(user_id=user.id).first()
    if not profile_data and db_profile:
        profile_data = db_profile.to_dict()
    elif db_profile:
        # Save submitted profile changes to database profile to keep it synced
        db_profile.full_name = profile_data.get('full_name', db_profile.full_name)
        db_profile.email = profile_data.get('email', db_profile.email)
        db_profile.phone = profile_data.get('phone', db_profile.phone)
        db_profile.location = profile_data.get('location', db_profile.location)
        db_profile.linkedin = profile_data.get('linkedin', db_profile.linkedin)
        db_profile.portfolio = profile_data.get('portfolio', db_profile.portfolio)
        db_profile.experience_years = int(profile_data.get('experience_years', db_profile.experience_years or 0))
        db_profile.current_position = profile_data.get('current_position', db_profile.current_position)
        db_profile.previous_position = profile_data.get('previous_position', db_profile.previous_position)
        db_profile.industry = profile_data.get('industry', db_profile.industry)
        db_profile.skills = profile_data.get('skills', db_profile.skills)
        db_profile.achievements = profile_data.get('achievements', db_profile.achievements)
        db_profile.certifications = profile_data.get('certifications', db_profile.certifications)
        db_profile.education = profile_data.get('education', db_profile.education)
        db_profile.languages = profile_data.get('languages', db_profile.languages)
        db_profile.projects = profile_data.get('projects', db_profile.projects)
        
    try:
        # 1. Run AI Generation
        letter_content = generate_cover_letter(profile_data, job_details, writing_style)
        
        # 2. Run ATS Analysis
        ats_results = analyze_ats(profile_data, job_details.get('job_description', ''))
        
        # 3. Create CoverLetter in db
        new_letter = CoverLetter(
            user_id=user.id,
            title=title,
            template_name=template_name,
            writing_style=writing_style,
            job_title=job_details.get('job_title', ''),
            company_name=job_details.get('company_name', ''),
            hiring_manager=job_details.get('hiring_manager', ''),
            job_description=job_details.get('job_description', ''),
            job_location=job_details.get('job_location', ''),
            employment_type=job_details.get('employment_type', ''),
            salary=job_details.get('salary', ''),
            content=letter_content,
            ats_score=ats_results['ats_score'],
            keywords_matched=ats_results['keywords_matched'],
            missing_skills=ats_results['missing_skills'],
            readability=ats_results['readability'],
            grammar_status=ats_results['grammar_status'],
            action_verbs_count=ats_results['action_verbs_count'],
            suggestions=ats_results['suggestions']
        )
        
        # Deduct 1 credit for free tier user
        if user.subscription_status == 'Free Tier':
            user.credits -= 1
            
        db.session.add(new_letter)
        
        # Log activity
        log = ActivityLog(user_id=user.id, action="Generate Letter", details=f"Generated letter for {new_letter.company_name}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify(new_letter.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to generate cover letter: {str(e)}'}), 500


@routes_bp.route('/api/cover-letters', methods=['GET'])
@jwt_required()
def api_get_letters():
    """Returns a list of all cover letters created by the authenticated user."""
    user_id = get_jwt_identity()
    letters = CoverLetter.query.filter_by(user_id=int(user_id)).order_by(CoverLetter.date_updated.desc()).all()
    return jsonify([l.to_dict() for l in letters]), 200


@routes_bp.route('/api/cover-letters/<int:letter_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def api_letter_detail(letter_id):
    """GET details, PUT updates, or DELETE a specific cover letter resource."""
    user_id = int(get_jwt_identity())
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first()
    
    if not letter:
        return jsonify({'error': 'Cover Letter not found or unauthorized'}), 404
        
    if request.method == 'GET':
        return jsonify(letter.to_dict()), 200
        
    elif request.method == 'PUT':
        data = request.get_json() or {}
        try:
            letter.title = data.get('title', letter.title)
            letter.content = data.get('content', letter.content)
            letter.template_name = data.get('template_name', letter.template_name)
            letter.writing_style = data.get('writing_style', letter.writing_style)
            
            # Recalculate ATS score in case the content was edited manually on the frontend
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                ats_results = analyze_ats(profile.to_dict(), letter.job_description)
                letter.ats_score = ats_results['ats_score']
                letter.keywords_matched = ats_results['keywords_matched']
                letter.missing_skills = ats_results['missing_skills']
                letter.readability = ats_results['readability']
                letter.grammar_status = ats_results['grammar_status']
                letter.action_verbs_count = ats_results['action_verbs_count']
                letter.suggestions = ats_results['suggestions']
                
            db.session.commit()
            return jsonify(letter.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update letter: {str(e)}'}), 500
            
    elif request.method == 'DELETE':
        try:
            db.session.delete(letter)
            log = ActivityLog(user_id=user_id, action="Delete Letter", details=f"Deleted cover letter: {letter.title}")
            db.session.add(log)
            db.session.commit()
            return jsonify({'message': 'Cover Letter deleted successfully.'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500


@routes_bp.route('/api/cover-letters/<int:letter_id>/favorite', methods=['POST'])
@jwt_required()
def api_toggle_favorite(letter_id):
    """Toggles the favorite flag of a cover letter."""
    user_id = int(get_jwt_identity())
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first()
    
    if not letter:
        return jsonify({'error': 'Cover Letter not found'}), 404
        
    try:
        letter.is_favorite = not letter.is_favorite
        db.session.commit()
        return jsonify({'message': 'Favorite status toggled', 'is_favorite': letter.is_favorite}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@routes_bp.route('/api/cover-letters/<int:letter_id>/duplicate', methods=['POST'])
@jwt_required()
def api_duplicate_letter(letter_id):
    """Creates a direct copy of an existing cover letter."""
    user_id = int(get_jwt_identity())
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first()
    
    if not letter:
        return jsonify({'error': 'Cover letter not found'}), 404
        
    try:
        dup = CoverLetter(
            user_id=user_id,
            title=f"Copy of {letter.title}",
            template_name=letter.template_name,
            writing_style=letter.writing_style,
            job_title=letter.job_title,
            company_name=letter.company_name,
            hiring_manager=letter.hiring_manager,
            job_description=letter.job_description,
            job_location=letter.job_location,
            employment_type=letter.employment_type,
            salary=letter.salary,
            content=letter.content,
            ats_score=letter.ats_score,
            keywords_matched=letter.keywords_matched,
            missing_skills=letter.missing_skills,
            readability=letter.readability,
            grammar_status=letter.grammar_status,
            action_verbs_count=letter.action_verbs_count,
            suggestions=letter.suggestions
        )
        db.session.add(dup)
        db.session.commit()
        return jsonify(dup.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@routes_bp.route('/api/cover-letters/<int:letter_id>/improve', methods=['POST'])
@jwt_required()
def api_improve_letter(letter_id):
    """Invokes AI edit modifiers (Shorten, Expand, Rewrite, Tones)."""
    user_id = int(get_jwt_identity())
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first()
    
    if not letter:
        return jsonify({'error': 'Cover Letter not found'}), 404
        
    data = request.get_json() or {}
    operation = data.get('operation', 'Improve Writing')
    tone = data.get('tone', letter.writing_style)
    
    try:
        # Run AI text transformation
        improved_content = improve_text(letter.content, operation, tone)
        
        # Save to letter
        letter.content = improved_content
        letter.writing_style = tone.lower()
        
        # Recalculate ATS
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            ats_results = analyze_ats(profile.to_dict(), letter.job_description)
            letter.ats_score = ats_results['ats_score']
            letter.keywords_matched = ats_results['keywords_matched']
            letter.missing_skills = ats_results['missing_skills']
            letter.readability = ats_results['readability']
            letter.grammar_status = ats_results['grammar_status']
            letter.action_verbs_count = ats_results['action_verbs_count']
            letter.suggestions = ats_results['suggestions']
            
        db.session.commit()
        return jsonify(letter.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process improvement: {str(e)}'}), 500


@routes_bp.route('/api/cover-letters/<int:letter_id>/export/docx', methods=['GET'])
@jwt_required()
def api_export_docx(letter_id):
    """Generates and downloads a DOCX file of the cover letter."""
    user_id = int(get_jwt_identity())
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first()
    
    if not letter:
        return jsonify({'error': 'Cover Letter not found'}), 404
        
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
        
    try:
        # Compile document data
        doc_data = {
            'full_name': profile.full_name or 'Applicant',
            'email': profile.email or '',
            'phone': profile.phone or '',
            'location': profile.location or '',
            'linkedin': profile.linkedin or '',
            'hiring_manager': letter.hiring_manager or '',
            'company_name': letter.company_name or '',
            'job_location': letter.job_location or '',
            'content': letter.content
        }
        
        file_stream = create_docx_file(doc_data)
        
        filename = f"{letter.title.replace(' ', '_')}.docx"
        return send_file(
            file_stream,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'DOCX generation error: {str(e)}'}), 500


@routes_bp.route('/api/cover-letters/<int:letter_id>/export/email', methods=['POST'])
@jwt_required()
def api_email_letter(letter_id):
    """Sends the cover letter text via email (mock sandbox simulation)."""
    user_id = int(get_jwt_identity())
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first()
    
    if not letter:
        return jsonify({'error': 'Cover Letter not found'}), 404
        
    data = request.get_json() or {}
    email_to = data.get('email', '').strip()
    
    if not email_to:
        return jsonify({'error': 'Recipient email is required'}), 400
        
    try:
        subject = f"Cover Letter for {letter.job_title} at {letter.company_name}"
        success, msg = send_cover_letter_email(email_to, subject, letter.content)
        
        if success:
            log = ActivityLog(user_id=user_id, action="Email Letter", details=f"Emailed cover letter to {email_to}")
            db.session.add(log)
            db.session.commit()
            return jsonify({'message': msg}), 200
        else:
            return jsonify({'error': msg}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Allows user feedback submissions from landing page and dashboard."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()
    
    if not name or not email or not message:
        return jsonify({'error': 'All fields are required.'}), 400
        
    try:
        fb = Feedback(name=name, email=email, message=message)
        db.session.add(fb)
        db.session.commit()
        return jsonify({'message': 'Thank you! Your feedback has been received.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@routes_bp.route('/api/share/<token>', methods=['GET'])
def api_get_shared_letter(token):
    """Publicly fetches cover letter details by its secure share token."""
    letter = CoverLetter.query.filter_by(share_token=token).first()
    if not letter:
        return jsonify({'error': 'Cover Letter not found'}), 404
        
    user = User.query.get(letter.user_id)
    profile = Profile.query.filter_by(user_id=user.id).first()
    
    return jsonify({
        'title': letter.title,
        'template_name': letter.template_name,
        'job_title': letter.job_title,
        'company_name': letter.company_name,
        'content': letter.content,
        'full_name': profile.full_name if profile else 'Applicant',
        'email': profile.email if profile else '',
        'phone': profile.phone if profile else '',
        'location': profile.location if profile else '',
        'linkedin': profile.linkedin if profile else '',
        'portfolio': profile.portfolio if profile else ''
    }), 200


@routes_bp.route('/api/credits/refill', methods=['POST'])
@jwt_required()
def refill_credits_sandbox():
    """Developer sandbox tool allowing users to reset their credits for testing."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    user.credits = 5
    db.session.commit()
    return jsonify({'message': 'Credits refilled! (Sandbox tool)', 'credits': user.credits}), 200
