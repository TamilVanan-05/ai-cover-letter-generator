import re
import json

# List of common professional action verbs for ATS
ACTION_VERBS = [
    "led", "directed", "managed", "spearheaded", "orchestrated", "developed", 
    "implemented", "engineered", "designed", "created", "built", "optimized", 
    "streamlined", "accelerated", "boosted", "delivered", "coordinated", 
    "maximized", "automated", "transformed", "formulated", "supervised"
]

def analyze_ats(profile, job_description):
    """Analyzes a profile and cover letter against the target job description to compute ATS scores."""
    
    job_desc_lower = job_description.lower()
    
    # 1. Extract Profile details
    profile_skills = [s.strip().lower() for s in profile.get('skills', '').split(',') if s.strip()]
    profile_certs = [c.strip().lower() for c in profile.get('certifications', '').split(',') if c.strip()]
    achievements = profile.get('achievements', '').lower()
    
    # 2. Extract potential keywords from Job Description
    # We look for common tech terms, soft skills, and nouns inside the JD
    # We can also do a basic keyword match with the candidate's skills
    keywords_found = []
    missing_skills = []
    
    # If the user has explicitly entered skills, check which ones are in the job description
    for skill in profile_skills:
        # Match as whole word or substring
        if re.search(r'\b' + re.escape(skill) + r'\b', job_desc_lower):
            keywords_found.append(skill.title())
        else:
            # If not found in JD, but exists in profile, it is a bonus.
            pass
            
    # Try to extract required skills from Job Description that are NOT in profile
    # Common industry terms: Python, Javascript, React, SQL, Project Management, etc.
    common_terms = [
        "python", "javascript", "react", "node", "sql", "aws", "docker", "kubernetes",
        "ci/cd", "agile", "scrum", "project management", "product management", "ui/ux",
        "css", "html", "git", "cloud", "security", "machine learning", "ai", "data analysis",
        "communication", "leadership", "collaboration", "problem solving", "critical thinking",
        "finance", "sales", "marketing", "operations", "recruiting", "hr", "customer service"
    ]
    
    for term in common_terms:
        # Check if the term is in the JD
        if re.search(r'\b' + re.escape(term) + r'\b', job_desc_lower):
            # Check if this term is NOT in candidate's skills
            if term not in profile_skills:
                missing_skills.append(term.title())
            else:
                if term.title() not in keywords_found:
                    keywords_found.append(term.title())
                    
    # 3. Compute Keyword Match Ratio
    total_relevant_jd_skills = len(keywords_found) + len(missing_skills)
    if total_relevant_jd_skills > 0:
        match_percentage = (len(keywords_found) / total_relevant_jd_skills) * 100
    else:
        match_percentage = 60.0 # Default base
        
    # 4. Action Verbs Checker
    action_verbs_found = []
    # Check verbs in achievements
    for verb in ACTION_VERBS:
        if re.search(r'\b' + re.escape(verb) + r'\b', achievements):
            action_verbs_found.append(verb)
            
    # 5. Readability Analysis
    # Let's compute a simple readability score based on text complexity (sentence length)
    word_count = len(job_description.split())
    sentence_count = len(re.split(r'[.!?]+', job_description)) or 1
    avg_sentence_len = word_count / sentence_count
    
    # Heuristics for readability index
    if avg_sentence_len < 12:
        readability_score = 90  # Extremely clear, simple
    elif avg_sentence_len < 18:
        readability_score = 80  # Professional standard
    elif avg_sentence_len < 25:
        readability_score = 65  # Executive complex
    else:
        readability_score = 45  # Verbose, hard to read
        
    # 6. Grammar & Formatting status
    grammar_status = "Excellent"
    if len(profile.get('full_name', '')) < 3 or not profile.get('email', ''):
        grammar_status = "Warning: Incomplete Header"
    
    # 7. Suggestions List
    suggestions = []
    if len(missing_skills) > 0:
        suggestions.append(f"Incorporate missing core skills: {', '.join(missing_skills[:3])} into your achievements.")
    if len(action_verbs_found) < 3:
        suggestions.append("Inject powerful recruiter-friendly action verbs like 'spearheaded', 'orchestrated', or 'streamlined'.")
    if not any(char.isdigit() for char in achievements):
        suggestions.append("Add measurable metrics (e.g. 'boosted efficiency by 25%', 'led team of 5') to validate your achievements.")
    if len(profile_certs) == 0:
        suggestions.append("Mention relevant certifications or credentials to increase credibility.")
    if readability_score < 60:
        suggestions.append("Break down complex, long sentences to improve structural readability and flow.")
        
    if not suggestions:
        suggestions.append("Your cover letter is highly optimized and ready for job applications!")
        
    # 8. Compute final ATS Score
    # Weighted average:
    # 50% keyword match, 25% action verbs, 15% readability, 10% formatting/profile completeness
    action_verbs_score = min((len(action_verbs_found) / 4) * 100, 100) if action_verbs_found else 40
    profile_complete_score = 100 if (profile.get('full_name') and profile.get('email') and profile.get('phone')) else 50
    
    ats_score = int(
        (match_percentage * 0.50) + 
        (action_verbs_score * 0.20) + 
        (readability_score * 0.20) + 
        (profile_complete_score * 0.10)
    )
    
    # Constrain score
    ats_score = max(10, min(ats_score, 100))
    
    return {
        'ats_score': ats_score,
        'keywords_matched': json.dumps(keywords_found),
        'missing_skills': json.dumps(missing_skills),
        'readability': readability_score,
        'grammar_status': grammar_status,
        'action_verbs_count': len(action_verbs_found),
        'suggestions': json.dumps(suggestions)
    }
