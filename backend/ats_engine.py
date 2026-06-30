import re
import json
import google.generativeai as genai
from config import Config

# List of common professional action verbs for ATS
ACTION_VERBS = [
    "led", "directed", "managed", "spearheaded", "orchestrated", "developed", 
    "implemented", "engineered", "designed", "created", "built", "optimized", 
    "streamlined", "accelerated", "boosted", "delivered", "coordinated", 
    "maximized", "automated", "transformed", "formulated", "supervised",
    "executed", "negotiated", "pioneered", "implemented", "resolved"
]

def analyze_ats(profile, job_description, cover_letter_content=None):
    """Analyzes profile, job description, and cover letter text to compute detailed recruiter scoring."""
    
    job_desc_lower = job_description.lower()
    content_to_analyze = (cover_letter_content or "").strip()
    
    # 1. Extract profile skills
    profile_skills = [s.strip().lower() for s in profile.get('skills', '').split(',') if s.strip()]
    profile_certs = [c.strip().lower() for c in profile.get('certifications', '').split(',') if c.strip()]
    achievements = profile.get('achievements', '').lower()
    
    # 2. Match keywords present in Job Description
    keywords_found = []
    missing_skills = []
    recommended_skills = []
    
    # Check profile skills against Job Description
    for skill in profile_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', job_desc_lower):
            keywords_found.append(skill.title())
            
    # Common industry terms to extract missing and recommended skills
    common_terms = [
        "python", "javascript", "react", "node", "sql", "aws", "docker", "kubernetes",
        "ci/cd", "agile", "scrum", "project management", "product management", "ui/ux",
        "css", "html", "git", "cloud", "security", "machine learning", "ai", "data analysis",
        "communication", "leadership", "collaboration", "problem solving", "critical thinking",
        "finance", "sales", "marketing", "operations", "recruiting", "hr", "customer service"
    ]
    
    for term in common_terms:
        if re.search(r'\b' + re.escape(term) + r'\b', job_desc_lower):
            if term not in profile_skills:
                missing_skills.append(term.title())
            else:
                if term.title() not in keywords_found:
                    keywords_found.append(term.title())
        else:
            # Recommended skills not directly in JD but highly related to tech/corporate jobs
            if term not in profile_skills and len(recommended_skills) < 4:
                recommended_skills.append(term.title())
                
    # 3. Calculate Keyword Match Percentage
    total_relevant_jd_skills = len(keywords_found) + len(missing_skills)
    if total_relevant_jd_skills > 0:
        keyword_score = int((len(keywords_found) / total_relevant_jd_skills) * 100)
    else:
        keyword_score = 65
        
    # 4. Action Verbs Evaluation
    action_verbs_found = []
    search_space = content_to_analyze.lower() if content_to_analyze else achievements
    for verb in ACTION_VERBS:
        if re.search(r'\b' + re.escape(verb) + r'\b', search_space):
            action_verbs_found.append(verb)
            
    action_verbs_score = min((len(action_verbs_found) / 5) * 100, 100) if action_verbs_found else 30
    action_verbs_score = int(action_verbs_score)
    
    # 5. Readability Index (Flesch-like average sentence length rules)
    analysis_text = content_to_analyze or job_description
    word_count = len(analysis_text.split()) or 1
    sentences = re.split(r'[.!?]+', analysis_text)
    sentence_count = len([s for s in sentences if s.strip()]) or 1
    avg_sentence_len = word_count / sentence_count
    
    if avg_sentence_len < 13:
        readability_score = 90  # Extremely clear, simple
    elif avg_sentence_len < 19:
        readability_score = 80  # Professional standard
    elif avg_sentence_len < 25:
        readability_score = 65  # Executive complex
    else:
        readability_score = 45  # Verbose, hard to read
        
    # 6. Formatting Score (Completeness of personal header fields)
    required_fields = ['full_name', 'email', 'phone', 'location']
    filled_fields = [f for f in required_fields if profile.get(f)]
    formatting_score = int((len(filled_fields) / len(required_fields)) * 100)
    
    # 7. Word Count & Length Analysis (ideal is 250-400 words)
    letter_words = len(content_to_analyze.split()) if content_to_analyze else 0
    if not content_to_analyze:
        length_score = 70
        length_analysis = "Cover letter content is missing or in draft state."
    elif letter_words < 150:
        length_score = 50
        length_analysis = f"Cover letter is too short ({letter_words} words). Ideal length is 250-400 words. Expand on achievements."
    elif letter_words < 250:
        length_score = 85
        length_analysis = f"Cover letter is slightly short ({letter_words} words). Consider adding details about target project mappings."
    elif letter_words <= 400:
        length_score = 100
        length_analysis = f"Perfect word count ({letter_words} words)! Excellent concise recruiter engagement layout."
    else:
        length_score = 75
        length_analysis = f"Cover letter is verbose ({letter_words} words). Keep it under 400 words to maintain reader focus."
        
    # 8. Grammar & Syntax Analysis (Try to check with LanguageTool, otherwise local rules)
    grammar_score = 95
    grammar_errors_list = []
    
    # Try importing language-tool-python (will fail if not present or Java is missing)
    try:
        import language_tool_python
        tool = language_tool_python.LanguageTool('en-US')
        matches = tool.check(content_to_analyze)
        if matches:
            grammar_errors_list = [f"Line {m.row+1}: {m.message} ('{content_to_analyze[m.offset:m.offset+m.errorLength]}')" for m in matches[:3]]
            grammar_score = max(40, 100 - len(matches) * 5)
    except Exception:
        # Heuristics: search for double spaces, lack of sentence casing, capitalization
        if content_to_analyze:
            if "  " in content_to_analyze:
                grammar_errors_list.append("Double spacing detected. Clean up formatting.")
                grammar_score -= 10
            # Check lowercase sentence starts
            sentences_list = re.split(r'[.!?]+\s+', content_to_analyze)
            for s in sentences_list[:5]:
                if s and s[0].islower() and not s.startswith("http"):
                    grammar_errors_list.append("Sentence starts with lowercase character.")
                    grammar_score -= 15
                    break
                    
    grammar_status = "Excellent" if grammar_score >= 90 else ("Good" if grammar_score >= 70 else "Needs Work")
    if not content_to_analyze:
        grammar_status = "Needs Review"
        grammar_score = 50
        
    # 9. Professional Tone Score (based on vocab matches)
    tone_score = 85
    if content_to_analyze:
        professional_vocab = ["expertise", "pioneered", "accelerated", "strategic", "collaborative", "achieved", "delivered", "industry"]
        vocab_matches = [v for v in professional_vocab if v in content_to_analyze.lower()]
        tone_score = min(100, 60 + len(vocab_matches) * 5)
        
    # 10. Generate Suggestions and Recruiter Feedback (utilizing Gemini if key exists)
    recruiter_suggestions = {
        "weak_sentences": [
            "I am writing to apply for the position because I need a job.",
            "I have good communication skills and work hard."
        ],
        "strong_alternatives": [
            "I am eager to apply my 5+ years of software design expertise to accelerate target outcomes at your company.",
            "I offer a proven history of cross-functional team leadership, delivering 3 distinct web applications under tight deadlines."
        ],
        "missing_metrics": "Differentiate achievements by adding numbers: e.g., 'led team of 4 developers', 'boosted API responses by 22%'.",
        "better_closing_paragraph": "I look forward to discussing how my experience in building scalable solutions matches your technical requirements in an interview. Thank you for your time."
    }
    
    smart_suggestions = {
        "certifications": ["AWS Certified Developer", "Certified Scrum Master (CSM)"],
        "technical_skills": ["CI/CD pipelines", "RESTful API Integration", "Docker Containerization"],
        "soft_skills": ["Cross-functional communication", "Resource optimization", "Critical planning"],
        "projects": ["High-throughput microservices using Flask and Gunicorn", "Autoscale deployments on AWS cloud infrastructures"],
        "career_tips": "Align your portfolio projects to showcase system scale and low latency rather than simple CRUD apps."
    }
    
    skill_gap_analysis = {
        "summary": "You have a solid alignment, but incorporating containerization and cloud orchestration in your achievements will lock in recruiter focus.",
        "severity": "Medium"
    }
    
    # Heuristic recommendations list
    suggestions = []
    if len(missing_skills) > 0:
        suggestions.append(f"Incorporate missing core skills: {', '.join(missing_skills[:3])} into your achievements.")
    if len(action_verbs_found) < 3:
        suggestions.append("Inject powerful recruiter-friendly action verbs like 'spearheaded', 'orchestrated', or 'streamlined'.")
    if not any(char.isdigit() for char in achievements):
        suggestions.append("Add measurable metrics (e.g. 'boosted efficiency by 25%') to validate achievements.")
    if readability_score < 60:
        suggestions.append("Break down complex, long sentences to improve structural readability and flow.")
    if grammar_score < 80:
        suggestions.append("Run grammar checks to fix spacing or sentence casing alerts.")
        
    if not suggestions:
        suggestions.append("Your cover letter is highly optimized and ready for job applications!")
        
    # Attempt to use Gemini for premium suggestions if key is configured
    if Config.GEMINI_API_KEY and content_to_analyze:
        prompt = f"""
        You are a Senior Recruiter and ATS Expert. Analyze this cover letter against the job description.
        
        COVER LETTER:
        {content_to_analyze}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide constructive recruiter feedback.
        You MUST respond with ONLY a valid raw JSON object matching this structure (no markdown wrappers):
        {{
            "weak_sentences": ["List 2 weak or generic sentences in the cover letter"],
            "strong_alternatives": ["Provide 2 high-impact, metrics-driven replacement sentences"],
            "missing_metrics": "One sentence advice on where to add percentages/numbers",
            "better_closing_paragraph": "A highly compelling closing paragraph with Call to Action",
            "suggested_certifications": ["List 2 relevant certifications for this role"],
            "suggested_technical_skills": ["List 2 suggested tech skills to learn"],
            "suggested_soft_skills": ["List 2 suggested soft skills"],
            "suggested_projects": ["List 1-2 projects the candidate should add"],
            "career_tips": "One piece of valuable search advice",
            "skill_gap_summary": "A short summary of key skill gaps"
        }}
        """
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            if response and response.text:
                clean_res = response.text.strip()
                if clean_res.startswith("```"):
                    lines = clean_res.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    clean_res = "\n".join(lines).strip()
                    
                parsed_res = json.loads(clean_res)
                
                # Override templates with Gemini responses
                recruiter_suggestions["weak_sentences"] = parsed_res.get("weak_sentences", recruiter_suggestions["weak_sentences"])
                recruiter_suggestions["strong_alternatives"] = parsed_res.get("strong_alternatives", recruiter_suggestions["strong_alternatives"])
                recruiter_suggestions["missing_metrics"] = parsed_res.get("missing_metrics", recruiter_suggestions["missing_metrics"])
                recruiter_suggestions["better_closing_paragraph"] = parsed_res.get("better_closing_paragraph", recruiter_suggestions["better_closing_paragraph"])
                
                smart_suggestions["certifications"] = parsed_res.get("suggested_certifications", smart_suggestions["certifications"])
                smart_suggestions["technical_skills"] = parsed_res.get("suggested_technical_skills", smart_suggestions["technical_skills"])
                smart_suggestions["soft_skills"] = parsed_res.get("suggested_soft_skills", smart_suggestions["soft_skills"])
                smart_suggestions["projects"] = parsed_res.get("suggested_projects", smart_suggestions["projects"])
                smart_suggestions["career_tips"] = parsed_res.get("career_tips", smart_suggestions["career_tips"])
                
                skill_gap_analysis["summary"] = parsed_res.get("skill_gap_summary", skill_gap_analysis["summary"])
        except Exception as e:
            print(f"Gemini ATS advice fetch failed: {e}. Using rules-based recommendations.")
            
    # Calculate Overall Weighted ATS Score
    # 35% Keyword Match, 15% Grammar, 15% Readability, 10% Tone, 15% Action Verbs, 10% Formatting
    ats_score = int(
        (keyword_score * 0.35) + 
        (grammar_score * 0.15) + 
        (readability_score * 0.15) + 
        (tone_score * 0.10) + 
        (action_verbs_score * 0.15) + 
        (formatting_score * 0.10)
    )
    ats_score = max(15, min(ats_score, 100))
    
    # Store everything inside suggestions payload JSON
    rich_suggestions_payload = {
        "suggestions_list": suggestions,
        "grammar_errors": grammar_errors_list,
        "recruiter_suggestions": recruiter_suggestions,
        "smart_suggestions": smart_suggestions,
        "skill_gap_analysis": skill_gap_analysis,
        "scores": {
            "keyword": keyword_score,
            "grammar": grammar_score,
            "tone": tone_score,
            "readability": readability_score,
            "formatting": formatting_score,
            "action_verbs": action_verbs_score,
            "length": length_score
        },
        "length_analysis": length_analysis,
        "recommended_skills": recommended_skills
    }
    
    return {
        'ats_score': ats_score,
        'keywords_matched': json.dumps(keywords_found),
        'missing_skills': json.dumps(missing_skills),
        'readability': readability_score,
        'grammar_status': grammar_status,
        'action_verbs_count': len(action_verbs_found),
        'suggestions': json.dumps(rich_suggestions_payload)
    }
