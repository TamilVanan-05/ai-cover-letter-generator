// --- RENDER ATS COMPLIANCE REPORT TABS ---
function renderAtsReport(letter) {
    if (!letter) return;
    
    // Conic gradient circle score progress for overall ATS score
    const circle = document.getElementById('atsScoreCircle');
    const scoreVal = document.getElementById('atsScoreVal');
    
    const score = parseInt(letter.ats_score) || 0;
    scoreVal.textContent = score;
    
    let color = "#ef4444"; // default red
    if (score >= 80) {
        color = "#10b981"; // emerald
    } else if (score >= 60) {
        color = "#6366f1"; // indigo
    } else if (score >= 40) {
        color = "#f59e0b"; // amber
    }
    
    if (circle) {
        circle.style.background = `conic-gradient(${color} ${score * 3.6}deg, rgba(255, 255, 255, 0.05) 0deg)`;
    }
    
    // Extract suggestions payload JSON containing all analytical scores and suggestions
    let analysis = {};
    try {
        analysis = typeof letter.suggestions === 'string' ? JSON.parse(letter.suggestions) : letter.suggestions;
    } catch (e) {
        console.error("Error parsing ATS rich suggestions payload:", e);
    }
    
    // Default Fallback values in case the JSON is empty or old single-text structure
    const scores = analysis.scores || {
        keyword: Math.round(score * 0.9),
        grammar: letter.grammar_status === "Excellent" ? 95 : 70,
        tone: 80,
        readability: letter.readability || 75,
        formatting: 90,
        action_verbs: Math.min(100, (letter.action_verbs_count || 0) * 20),
        length: 80
    };
    
    const lengthAnalysis = analysis.length_analysis || "Review cover letter word count layout standard guidelines.";
    const recommendedSkills = analysis.recommended_skills || ["Cloud Architect", "CI/CD Pipelines", "System Scalability"];
    const grammarErrors = analysis.grammar_errors || [];
    
    const recruiterSug = analysis.recruiter_suggestions || {
        weak_sentences: ["I am applying for the job because my skills match.", "I want to work at your company."],
        strong_alternatives: ["I offer a verified record of accelerating deployment pipelines by 25% with zero downtime.", "I am eager to spearhead cloud infrastructure projects at your brand."],
        missing_metrics: "Add metrics to validate accomplishments (e.g. led team of 3 developer engineers).",
        better_closing_paragraph: "I look forward to discussing how my software design achievements align with your targets. Thank you for your time."
    };
    
    const smartSug = analysis.smart_suggestions || {
        certifications: ["AWS Certified Developer", "Certified Scrum Master"],
        technical_skills: ["Microservices", "Flask RESTful APIs", "Docker containerization"],
        soft_skills: ["Operational leadership", "Resource orchestration", "Stakeholder communications"],
        projects: ["Built high-throughput Flask microservices", "Deployed Docker containers to cloud servers"],
        career_tips: "Align your achievements to show metric-driven scaling latency drops."
    };
    
    const skillGap = analysis.skill_gap_analysis || {
        summary: "You are highly aligned, but incorporating cloud containerization and cloud orchestration will attract modern recruiters.",
        severity: "Medium"
    };

    // 1. Render Tab 1 - ATS Metric Horizontal bars
    setMetricProgressBar('atsMetricKeywordBar', 'atsMetricKeywordVal', scores.keyword);
    setMetricProgressBar('atsMetricGrammarBar', 'atsMetricGrammarVal', scores.grammar);
    setMetricProgressBar('atsMetricReadabilityBar', 'atsMetricReadabilityVal', scores.readability);
    setMetricProgressBar('atsMetricVerbsBar', 'atsMetricVerbsVal', scores.action_verbs);
    setMetricProgressBar('atsMetricFormattingBar', 'atsMetricFormattingVal', scores.formatting);
    
    document.getElementById('atsMetricLengthAnalysis').textContent = lengthAnalysis;
    
    const grammarLabel = document.getElementById('atsMetricGrammarStatus');
    if (grammarErrors.length > 0) {
        grammarLabel.innerHTML = `<span class="text-yellow-400 font-bold">${letter.grammar_status}:</span> ${grammarErrors.join(', ')}`;
    } else {
        grammarLabel.innerHTML = `<span class="text-emerald-400 font-bold">Excellent:</span> 0 grammar or punctuation bugs found.`;
    }

    // 2. Render Tab 2 - Skills Gap and Match arrays
    const matchedContainer = document.getElementById('atsTabKeywordsMatched');
    const missingContainer = document.getElementById('atsTabMissingSkills');
    const recomContainer = document.getElementById('atsTabRecommendedSkills');
    const skillGapSummaryText = document.getElementById('atsSkillGapSummary');
    
    if (skillGapSummaryText) {
        skillGapSummaryText.innerHTML = `<strong>Alignment:</strong> ${skillGap.summary} <span class="badge ${skillGap.severity === 'High' ? 'bg-rose-500' : 'bg-amber-500'} ml-2">${skillGap.severity} Severity</span>`;
    }
    
    let matchedKeywordsList = [];
    let missingKeywordsList = [];
    try {
        matchedKeywordsList = typeof letter.keywords_matched === 'string' ? JSON.parse(letter.keywords_matched) : letter.keywords_matched;
        missingKeywordsList = typeof letter.missing_skills === 'string' ? JSON.parse(letter.missing_skills) : letter.missing_skills;
    } catch (e) {
        console.error("Error parsing keyword matrices:", e);
    }
    
    renderSkillBadges(matchedContainer, matchedKeywordsList, "emerald", "check");
    renderSkillBadges(missingContainer, missingKeywordsList, "rose", "plus");
    renderSkillBadges(recomContainer, recommendedSkills, "indigo", "lightbulb");

    // 3. Render Tab 3 - Recruiter Feedback suggestions lists
    const weakUl = document.getElementById('atsRecruiterWeak');
    const strongUl = document.getElementById('atsRecruiterStrong');
    const metricsLabel = document.getElementById('atsRecruiterMetrics');
    const closingLabel = document.getElementById('atsRecruiterClosing');
    
    weakUl.innerHTML = '';
    recruiterSug.weak_sentences.forEach(s => {
        const li = document.createElement('li');
        li.className = "text-rose-400/90 italic";
        li.textContent = `"${s}"`;
        weakUl.appendChild(li);
    });
    
    strongUl.innerHTML = '';
    recruiterSug.strong_alternatives.forEach(s => {
        const li = document.createElement('li');
        li.className = "text-emerald-400 font-semibold";
        li.textContent = `"${s}"`;
        strongUl.appendChild(li);
    });
    
    metricsLabel.textContent = recruiterSug.missing_metrics;
    closingLabel.textContent = `"${recruiterSug.better_closing_paragraph}"`;

    // 4. Render Tab 4 - Smart AI Tips
    const certsContainer = document.getElementById('atsSmartCerts');
    const techContainer = document.getElementById('atsSmartTech');
    const softContainer = document.getElementById('atsSmartSoft');
    const projectsUl = document.getElementById('atsSmartProjects');
    const careerTipLabel = document.getElementById('atsSmartCareerTip');
    
    renderSkillBadges(certsContainer, smartSug.certifications, "indigo", "certificate");
    renderSkillBadges(techContainer, smartSug.technical_skills, "pink", "code");
    renderSkillBadges(softContainer, smartSug.soft_skills, "amber", "users");
    
    projectsUl.innerHTML = '';
    smartSug.projects.forEach(p => {
        const li = document.createElement('li');
        li.textContent = p;
        projectsUl.appendChild(li);
    });
    
    careerTipLabel.textContent = smartSug.career_tips;

    // 5. Render Tab 5 - Company Personalization Hooks text
    const personalizationHooksBox = document.getElementById('personalizationHooksText');
    if (letter.company_name && letter.company_name !== "Target Company") {
        personalizationHooksBox.textContent = `"I admire ${letter.company_name}'s innovation in engineering high-end operational SaaS components and your commitment to building scaled data pipelines."`;
    } else {
        personalizationHooksBox.textContent = `"I admire your company's commitment to building next-generation web products and fostering cross-functional product achievements."`;
    }

    // 6. Render bottom suggestions array
    const suggestionsUl = document.getElementById('atsSuggestionsList');
    suggestionsUl.innerHTML = '';
    
    let suggestionsList = [];
    if (analysis.suggestions_list) {
        suggestionsList = analysis.suggestions_list;
    } else {
        suggestionsList = ["Keep cover letter concise.", "Include action verbs.", "Ensure headers are filled."];
    }
    
    suggestionsList.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        suggestionsUl.appendChild(li);
    });
}

// Helper to set progress bar states
function setMetricProgressBar(barId, labelId, score) {
    const bar = document.getElementById(barId);
    const label = document.getElementById(labelId);
    if (bar && label) {
        bar.style.width = `${score}%`;
        label.textContent = `${score}%`;
        
        // Dynamic colors
        if (score >= 80) {
            bar.className = "bg-emerald-500 h-full";
        } else if (score >= 60) {
            bar.className = "bg-indigo-500 h-full";
        } else if (score >= 40) {
            bar.className = "bg-amber-500 h-full";
        } else {
            bar.className = "bg-rose-500 h-full";
        }
    }
}

// Helper to render lists as HTML badges
function renderSkillBadges(container, list, colorName, iconName) {
    if (!container) return;
    container.innerHTML = '';
    
    if (!list || list.length === 0) {
        container.innerHTML = '<span class="text-[10px] text-gray-500">None suggested or present.</span>';
        return;
    }
    
    list.forEach(item => {
        const badge = document.createElement('span');
        badge.className = `badge bg-${colorName}-500/10 text-${colorName}-400 border border-${colorName}-500/20 text-[10px] px-2 py-1`;
        badge.innerHTML = `<i class="fa-solid fa-${iconName} text-[8px] mr-1"></i> ${item}`;
        container.appendChild(badge);
    });
}

// Switching ATS Dashboard tabs in real-time
function switchAtsReportTab(tabId) {
    // Hide all contents
    document.querySelectorAll('.ats-tab-content').forEach(c => c.classList.add('hidden'));
    // Remove active styles
    document.querySelectorAll('#atsReportTabs button').forEach(b => b.classList.remove('active'));
    
    // Show target content tab
    const content = document.getElementById(`atsTab-${tabId}`);
    const activeBtn = document.getElementById(`tabBtn-${tabId}`);
    
    if (content) content.classList.remove('hidden');
    if (activeBtn) activeBtn.classList.add('active');
}
