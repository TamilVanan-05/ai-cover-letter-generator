// --- RENDER ATS COMPLIANCE REPORT ---
function renderAtsReport(letter) {
    if (!letter) return;
    
    // 1. Conic gradient circle score progress
    const circle = document.getElementById('atsScoreCircle');
    const scoreVal = document.getElementById('atsScoreVal');
    
    const score = parseInt(letter.ats_score) || 0;
    scoreVal.textContent = score;
    
    // Conic gradient mapping
    let color = "#ef4444"; // default red
    if (score >= 80) {
        color = "#10b981"; // emerald
    } else if (score >= 60) {
        color = "#6366f1"; // indigo
    } else if (score >= 40) {
        color = "#f59e0b"; // amber
    }
    
    circle.style.background = `conic-gradient(${color} ${score * 3.6}deg, rgba(255, 255, 255, 0.05) 0deg)`;
    
    // 2. Readability indicators
    document.getElementById('atsReadabilityVal').textContent = `${letter.readability} / 100`;
    document.getElementById('atsVerbsCount').textContent = `${letter.action_verbs_count} verbs`;
    
    // 3. Grammar alignment
    const grammarLabel = document.getElementById('atsGrammarVal');
    grammarLabel.textContent = letter.grammar_status || 'Excellent';
    if ((letter.grammar_status || '').includes("Warning")) {
        grammarLabel.className = "text-yellow-400";
    } else {
        grammarLabel.className = "text-emerald-400";
    }
    
    // 4. Keyword Badges Present vs Missing
    const presentContainer = document.getElementById('atsKeywordsMatched');
    const missingContainer = document.getElementById('atsMissingSkills');
    
    presentContainer.innerHTML = '';
    missingContainer.innerHTML = '';
    
    let matchedKeywordsList = [];
    let missingKeywordsList = [];
    
    try {
        matchedKeywordsList = typeof letter.keywords_matched === 'string' ? JSON.parse(letter.keywords_matched) : letter.keywords_matched;
        missingKeywordsList = typeof letter.missing_skills === 'string' ? JSON.parse(letter.missing_skills) : letter.missing_skills;
    } catch (e) {
        console.error("Error parsing keyword matrices:", e);
    }
    
    // Matched Badges
    if (!matchedKeywordsList || matchedKeywordsList.length === 0) {
        presentContainer.innerHTML = '<span class="text-[10px] text-gray-500">None found. Adjust description.</span>';
    } else {
        matchedKeywordsList.forEach(kw => {
            const badge = document.createElement('span');
            badge.className = "badge bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-1";
            badge.innerHTML = `<i class="fa-solid fa-check text-[8px] mr-1"></i> ${kw}`;
            presentContainer.appendChild(badge);
        });
    }
    
    // Missing Badges
    if (!missingKeywordsList || missingKeywordsList.length === 0) {
        missingContainer.innerHTML = '<span class="text-[10px] text-emerald-400 font-bold"><i class="fa-solid fa-circle-check"></i> 100% Core Keyword Coverage</span>';
    } else {
        missingKeywordsList.forEach(kw => {
            const badge = document.createElement('span');
            badge.className = "badge bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[10px] px-2 py-1";
            badge.innerHTML = `<i class="fa-solid fa-plus text-[8px] mr-1"></i> ${kw}`;
            missingContainer.appendChild(badge);
        });
    }
    
    // 5. Suggestions bullet listings
    const suggestionsUl = document.getElementById('atsSuggestionsList');
    suggestionsUl.innerHTML = '';
    
    let suggestionsList = [];
    try {
        suggestionsList = typeof letter.suggestions === 'string' ? JSON.parse(letter.suggestions) : letter.suggestions;
    } catch (e) {
        console.error("Error parsing recommendations logs:", e);
    }
    
    if (!suggestionsList || suggestionsList.length === 0) {
        suggestionsList = ["Your cover letter is highly optimized and ready for job applications!"];
    }
    
    suggestionsList.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        suggestionsUl.appendChild(li);
    });
}
