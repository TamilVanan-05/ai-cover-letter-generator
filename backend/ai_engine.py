import google.generativeai as genai
from config import Config

# Configure Gemini if API key is present
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)

def generate_cover_letter(profile, job_details, writing_style):
    """Generates cover letters using Gemini API or a smart rule-based local NLP engine fallback."""
    
    # Extract details
    full_name = profile.get('full_name', 'Applicant Name')
    email = profile.get('email', '')
    phone = profile.get('phone', '')
    location = profile.get('location', '')
    linkedin = profile.get('linkedin', '')
    portfolio = profile.get('portfolio', '')
    
    job_title = job_details.get('job_title', 'Role')
    company = job_details.get('company_name', 'Target Company')
    manager = job_details.get('hiring_manager', '').strip() or 'Hiring Manager'
    job_desc = job_details.get('job_description', '')
    job_location = job_details.get('job_location', '').strip() or 'Remote'
    
    exp_years = profile.get('experience_years', 0)
    current_pos = profile.get('current_position', '')
    prev_pos = profile.get('previous_position', '')
    industry = profile.get('industry', 'Technology')
    achievements = profile.get('achievements', '')
    skills = profile.get('skills', '')
    education = profile.get('education', '')
    
    # Prompt for Gemini
    prompt = f"""
    You are an expert recruitment coach and ATS Optimization writer. Write a premium, highly tailored, and recruiter-approved cover letter based on the following details.
    
    CANDIDATE PROFILE:
    - Name: {full_name}
    - Location: {location}
    - Experience: {exp_years} years
    - Current Position: {current_pos}
    - Previous Position: {prev_pos}
    - Target Industry: {industry}
    - Key Skills: {skills}
    - Achievements: {achievements}
    - Education: {education}
    
    TARGET JOB DETAILS:
    - Title: {job_title}
    - Company: {company}
    - Hiring Manager: {manager}
    - Location: {job_location}
    - Description: {job_desc}
    
    WRITING STYLE SPECIFICATION:
    - Tone: {writing_style} (Options include Professional, Executive, Corporate, Friendly, Creative, Formal, Confident, Enthusiastic, Minimal, Luxury Executive)
    
    CRITICAL AI REQUIREMENTS:
    1. Read the job description and candidate details, identifying matching terms.
    2. Start with a direct, compelling opening salutation and paragraph.
    3. The body paragraph should map candidate's actual achievements ({achievements}) and skills ({skills}) to requirements mentioned in the job description.
    4. Highlight concrete metrics and years of experience.
    5. Maintain a natural, authoritative tone. Avoid buzzwords and generic sentences.
    6. Include a Call-To-Action (CTA) in the closing paragraph.
    7. Generate a professional sign-off with candidate's details ({full_name}, {email}, {phone}, {linkedin}, {portfolio}).
    8. Write the complete cover letter directly. Do not include markdown labels like "Dear Hiring Manager:" at the very top of your response, just return the content naturally.
    """
    
    if Config.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            # If API fails, fall through to fallback engine
            print(f"Gemini API generation failed: {e}. Falling back to local generator.")
            
    # Fallback Local Generator
    return generate_local_fallback(profile, job_details, writing_style)


def generate_local_fallback(profile, job_details, writing_style):
    """Fallback generator using high-quality writing styles to compose letter elements."""
    
    full_name = profile.get('full_name', 'Applicant Name')
    email = profile.get('email', '')
    phone = profile.get('phone', '')
    location = profile.get('location', '')
    linkedin = profile.get('linkedin', '')
    portfolio = profile.get('portfolio', '')
    
    job_title = job_details.get('job_title', 'Role')
    company = job_details.get('company_name', 'Target Company')
    manager = job_details.get('hiring_manager', '').strip() or 'Hiring Manager'
    exp_years = profile.get('experience_years', 0)
    current_pos = profile.get('current_position', '')
    prev_pos = profile.get('previous_position', '')
    industry = profile.get('industry', 'Technology')
    
    # Process skills list
    skills_list = [s.strip() for s in profile.get('skills', '').split(',') if s.strip()]
    skills_str = ", ".join(skills_list[:4]) if skills_list else "core operations and technical execution"
    
    # Process achievements
    ach_list = [a.strip() for a in profile.get('achievements', '').split('\n') if a.strip()]
    main_ach = ach_list[0] if ach_list else f"Successfully led key projects and delivered results in {industry}."
    
    # Structure text by tone
    style = writing_style.lower()
    
    # 1. Salutation
    salutation = f"Dear {manager}," if manager != "Hiring Manager" else "Dear Hiring Manager,"
    
    # 2. Openings
    openings = {
        'professional': f"I am writing to express my strong interest in the {job_title} position at {company}. With {exp_years} years of dedicated experience in {industry}, particularly as a {current_pos or 'specialist'}, I am confident in my ability to drive key initiatives and support your team's objectives.",
        'executive': f"It is with great enthusiasm that I apply for the {job_title} leadership role at {company}. Throughout my career, including my tenure as {current_pos or 'a professional'}, I have specialized in building robust frameworks and executing growth strategies that align with corporate visions.",
        'corporate': f"Please accept this application for the position of {job_title} with {company}. My background in {industry} operations, combined with my history of high performance as {current_pos or 'an associate'}, matches the profile of the strategic contributor you are looking for.",
        'friendly': f"I was thrilled to see the opening for the {job_title} role at {company}! I have been following your company's milestones, and I would love to bring my {exp_years}+ years of expertise in {industry} to your vibrant team.",
        'creative': f"Every great company needs builders who think outside the box, and that is why I was drawn to the {job_title} position at {company}. Bringing an innovative approach and {exp_years} years of hands-on expertise, I am eager to redefine what is possible for your brand.",
        'formal': f"I am writing to formally submit my candidacy for the position of {job_title} at {company}. As a qualified professional with a strong foundation in {industry} (currently serving as {current_pos or 'a specialist'}), I present a verified record of diligence and expertise.",
        'confident': f"If you are seeking a results-driven leader who can immediately step into the {job_title} role and deliver high-impact results for {company}, my profile matches your requirements. I have spent the last {exp_years} years optimizing systems and scaling operations.",
        'enthusiastic': f"I am incredibly excited to apply for the {job_title} opening at {company}! My passion for {industry} and my accomplishments as {current_pos or 'a team lead'} make me uniquely suited to hit the ground running on day one.",
        'minimal': f"I am writing to apply for the {job_title} role at {company}. Based on my {exp_years} years of experience in {industry} and my technical background, I believe I can make an immediate contribution to your team.",
        'luxury executive': f"I am writing to propose my candidacy for the position of {job_title} at {company}. Throughout my distinguished career in the {industry} sector, I have orchestrated high-value strategies, optimized resource allocations, and consistently driven commercial excellence."
    }
    
    opening = openings.get(style, openings['professional'])
    
    # 3. Bodies
    bodies = {
        'professional': f"Currently, as a {current_pos or 'specialist'}, I focus on matching business needs with technical execution. In my previous role as {prev_pos or 'an analyst'}, I honed my skills in {skills_str}. My hands-on experience has taught me how to work cross-functionally and optimize core project flows. A key highlight of my career includes: '{main_ach}' which directly showcases my project ownership.",
        'executive': f"In my capacity as {current_pos or 'Director'}, I have managed budgets, spearheaded cross-functional alignments, and established performance indicators. Through the integration of {skills_str}, I ensure operational excellence. A testament to this is my achievement: '{main_ach}'. I look forward to bringing this level of execution and commercial focus to {company}.",
        'corporate': f"My career trajectory is built upon structured workflows and stakeholder satisfaction. While working as {current_pos or 'a manager'}, I successfully deployed systems centered around {skills_str}. Additionally, in my role as {prev_pos or 'specialist'}, I focused on efficiency metrics, culminating in my success: '{main_ach}'. I am prepared to apply these methodologies to {company}.",
        'friendly': f"I love solving complex puzzles, and that's exactly what I do every day in my current role as {current_pos or 'a designer'}. I've had the pleasure of leveraging {skills_str} to solve real-world problems. One accomplishment I'm particularly proud of is when I: '{main_ach}'. I'd love to share this positive energy and work ethic with the team at {company}!",
        'creative': f"I believe that traditional solutions aren't always enough for today's dynamic market. While working as {current_pos or 'creator'}, I have used {skills_str} to craft distinctive campaigns and systems. My work is best represented by this achievement: '{main_ach}'. I am eager to apply my creative problem-solving skills to the challenges ahead at {company}.",
        'formal': f"In the execution of my duties as {current_pos or 'Officer'}, I have maintained compliance and driven systematic improvements. I possess advanced capabilities in {skills_str}, which I have deployed to mitigate risks and streamline processes. Notably, I achieved the following milestone: '{main_ach}'. This structured approach will benefit {company}'s ongoing operations.",
        'confident': f"I have a track record of turning goals into realities. As {current_pos or 'Lead'}, I successfully led initiatives that relied heavily on {skills_str}. My standard of performance is reflected in my record: '{main_ach}'. I don't just manage projects; I deliver outcomes, and I am ready to do the same for the {job_title} position.",
        'enthusiastic': f"My dedication to this field drives me to constantly learn and improve. As {current_pos or 'a professional'}, I have put my skills in {skills_str} to work on highly collaborative projects. One of my absolute favorite wins was: '{main_ach}'. Bringing this level of drive and capability to {company} would be a privilege.",
        'minimal': f"My professional background includes working as {current_pos or 'a developer'}, where I utilized {skills_str} to meet project requirements. During this time, I accomplished the following: '{main_ach}'. I focus on clean code, concise communication, and direct execution.",
        'luxury executive': f"My professional ethos revolves around refined execution and strategic foresight. In my capacity as {current_pos or 'Executive'}, I have successfully leveraged {skills_str} to drive operational efficiency. A defining milestone of my career was: '{main_ach}'. I am prepared to offer this caliber of leadership and dedication to the {company} brand."
    }
    
    body = bodies.get(style, bodies['professional'])
    
    # 4. Closing
    closings = {
        'professional': f"I would welcome the opportunity to discuss how my experience and skills align with your needs. Thank you for your time and consideration of my application.",
        'executive': f"I am eager to explore how my strategic alignment can benefit your leadership goals. I look forward to an opportunity to speak with you soon.",
        'corporate': f"I am available at your earliest convenience to discuss how I can contribute to the team at {company}. Thank you for your review.",
        'friendly': f"I'd love to jump on a quick call or meet up to discuss how we can work together! Thanks so much for reading!",
        'creative': f"Let's connect to discuss how we can make amazing things happen for {company}. I appreciate your time and consideration!",
        'formal': f"I look forward to the possibility of an interview to discuss my suitability for this vacancy in greater detail. Thank you for your attention.",
        'confident': f"I am ready to demonstrate how my background will yield immediate value for your team. Let's schedule an interview to discuss this further.",
        'enthusiastic': f"I would be absolutely thrilled to speak with you! Let's arrange a time to connect soon. Thank you for this wonderful opportunity!",
        'minimal': f"I would appreciate the chance to discuss this opportunity. Thank you for your time.",
        'luxury executive': f"I welcome the opportunity to present my credentials in a formal discussion. I look forward to discussing how we can achieve exceptional milestones together."
    }
    
    closing = closings.get(style, closings['professional'])
    
    # 5. Sign-offs
    sign_off_phrase = "Sincerely," if style in ['professional', 'formal', 'corporate', 'executive', 'luxury executive', 'minimal'] else "Best regards,"
    
    signature_block = f"{sign_off_phrase}\n\n{full_name}"
    if email:
        signature_block += f"\nEmail: {email}"
    if phone:
        signature_block += f"\nPhone: {phone}"
    if linkedin:
        signature_block += f"\nLinkedIn: {linkedin}"
    if portfolio:
        signature_block += f"\nPortfolio: {portfolio}"
        
    return f"{salutation}\n\n{opening}\n\n{body}\n\n{closing}\n\n{signature_block}"


def improve_text(text, operation, style_tone):
    """Handles AI text transformations: Shorten, Expand, Rewrite, Tones adjustment, and humanization."""
    prompt = f"""
    You are an expert editor. Perform the '{operation}' command on the following text.
    Ensure the resulting text adopts a '{style_tone}' tone and is highly polished, professional, and readable.
    Maintain the core message, but make the text sound more natural, recruiter-approved, and flow flawlessly.
    
    ORIGINAL TEXT:
    {text}
    
    Generate ONLY the improved text directly. Do not add markdown labels or comments.
    """
    
    if Config.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini API improve failed: {e}. Falling back to local NLP editor.")
            
    # Local Text Transformation Fallback
    return local_text_improve(text, operation, style_tone)


def local_text_improve(text, operation, style_tone):
    """Rule-based text helper that manipulates paragraphs locally for basic sandbox edits."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        return text
        
    op = operation.lower()
    
    # If shortening
    if 'shorten' in op:
        shortened = []
        for p in paragraphs:
            # Keep first 2 sentences of each paragraph
            sentences = re.split(r'(?<=[.!?])\s+', p)
            shortened.append(" ".join(sentences[:2]))
        return "\n\n".join(shortened)
        
    # If expanding
    elif 'expand' in op:
        expanded = []
        for i, p in enumerate(paragraphs):
            if i == 1: # Add detail in the body
                expanded.append(p + " Furthermore, I have a history of driving efficiency metrics, aligning cross-functional teams, and implementing scalable solutions to complex problems.")
            else:
                expanded.append(p)
        return "\n\n".join(expanded)
        
    # If rewriting / humanizing
    elif 'rewrite' in op or 'humanize' in op:
        rewritten = []
        for p in paragraphs:
            # Do minor wording replacements to simulate rewrites
            p_mod = p.replace("express my strong interest", "let you know how excited I am to apply")
            p_mod = p_mod.replace("express my candidacy", "apply for the open position")
            p_mod = p_mod.replace("highly collaborative", "high-performance")
            p_mod = p_mod.replace("dedicated experience", "valuable background")
            rewritten.append(p_mod)
        return "\n\n".join(rewritten)
        
    # For tone adjustments
    elif 'tone' in op or 'optimize' in op:
        # Append professional emphasis sentences matching the tone
        if 'executive' in style_tone.lower() or 'luxury' in style_tone.lower():
            if len(paragraphs) > 2:
                paragraphs[1] += f" This aligns with my commitment to high-level strategic planning and business outcome optimization."
        elif 'friendly' in style_tone.lower():
            if len(paragraphs) > 2:
                paragraphs[1] += f" I'm really looking forward to joining your collaborative culture!"
        elif 'grammar' in op:
            # Simulates correction, return clean copy
            return text
            
        return "\n\n".join(paragraphs)
        
    return text
