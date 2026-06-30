// --- GLOBAL STATE ---
let currentWizardStep = 1;
let selectedWizardTone = "Professional";
let activeLetter = null; // Holds the currently generated/edited cover letter object
let savedLettersList = []; // Holds the user's saved cover letters list

// Preset template list names
const TEMPLATES_LIST = [
    "modern", "professional", "executive", "corporate", "minimal", 
    "google", "amazon", "microsoft", "blue", "dark", 
    "elegant", "creative", "graduate", "software-engineer", "ai-engineer"
];

// --- DASHBOARD NAVIGATION ---
function showDashView(viewName) {
    // Hide all views
    document.querySelectorAll('.dash-view').forEach(view => view.classList.add('hidden'));
    // Remove active styles from sidebar links
    document.querySelectorAll('.dash-sidebar-btn').forEach(btn => btn.classList.remove('active'));
    
    // Show target view
    document.getElementById(`view-${viewName}`).classList.remove('hidden');
    // Highlight side navigation button
    const activeBtn = document.getElementById(`sideBtn-${viewName}`);
    if (activeBtn) activeBtn.classList.add('active');
    
    // Run specific view loading logics
    if (viewName === 'letters') {
        loadSavedLetters();
    } else if (viewName === 'history') {
        loadHistoryLogs();
    } else if (viewName === 'profile') {
        loadUserProfileData();
    }
}

// --- RESUME DRAG & DROP FILE UPLOAD HANDLERS ---

// Trigger file inputs
function triggerResumeFileSelect() {
    document.getElementById('wizardResumeFileInput').click();
}

function triggerProfileResumeFileSelect() {
    document.getElementById('profileResumeFileInput').click();
}

// Drag & Drop Wizard Step 1 Visual feedback
function handleDragOver(e) {
    e.preventDefault();
    document.getElementById('wizardResumeUploadZone').classList.add('dragging');
}

function handleDragLeave(e) {
    e.preventDefault();
    document.getElementById('wizardResumeUploadZone').classList.remove('dragging');
}

function handleDrop(e) {
    e.preventDefault();
    const zone = document.getElementById('wizardResumeUploadZone');
    zone.classList.remove('dragging');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        performResumeUpload(file, 'wizard');
    }
}

function handleResumeFileChange(e) {
    if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0];
        performResumeUpload(file, 'wizard');
    }
}

// Drag & Drop Profile View Visual feedback
function handleDragOverProfile(e) {
    e.preventDefault();
    document.getElementById('profileResumeUploadZone').classList.add('dragging');
}

function handleDragLeaveProfile(e) {
    e.preventDefault();
    document.getElementById('profileResumeUploadZone').classList.remove('dragging');
}

function handleDropProfile(e) {
    e.preventDefault();
    const zone = document.getElementById('profileResumeUploadZone');
    zone.classList.remove('dragging');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        performResumeUpload(file, 'profile');
    }
}

function handleProfileResumeFileChange(e) {
    if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0];
        performResumeUpload(file, 'profile');
    }
}

// Perform File Upload via API
async function performResumeUpload(file, targetView) {
    const formData = new FormData();
    formData.append('file', file);
    
    const statusTextId = targetView === 'wizard' ? 'uploadStatusText' : 'profileUploadStatusText';
    const zoneId = targetView === 'wizard' ? 'wizardResumeUploadZone' : 'profileResumeUploadZone';
    
    const statusLabel = document.getElementById(statusTextId);
    const uploadZone = document.getElementById(zoneId);
    
    statusLabel.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i> Parsing resume semantics...`;
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/resume/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Parsing failed');
        }
        
        // Mark visual success
        uploadZone.classList.add('success');
        statusLabel.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400 mr-1"></i> Parsed: ${file.name}`;
        showToast("Resume parsed successfully! Form fields populated.", "Resume Extractor", "success");
        
        // Sync profile form states
        if (targetView === 'profile') {
            loadUserProfileData();
        } else {
            // Fill Wizard inputs directly
            const profile = data.profile;
            document.getElementById('wizFullname').value = profile.full_name || '';
            document.getElementById('wizEmail').value = profile.email || '';
            document.getElementById('wizPhone').value = profile.phone || '';
            document.getElementById('wizLocation').value = profile.location || '';
            document.getElementById('wizLinkedin').value = profile.linkedin || '';
            document.getElementById('wizPortfolio').value = profile.portfolio || '';
            
            document.getElementById('wizExperience').value = profile.experience_years || 0;
            document.getElementById('wizCurrentPos').value = profile.current_position || '';
            document.getElementById('wizPreviousPos').value = profile.previous_position || '';
            document.getElementById('wizIndustry').value = profile.industry || '';
            document.getElementById('wizSkills').value = profile.skills || '';
            document.getElementById('wizCerts').value = profile.certifications || '';
            document.getElementById('wizEducation').value = profile.education || '';
            document.getElementById('wizAchievements').value = profile.achievements || '';
        }
        
    } catch (err) {
        uploadZone.classList.remove('success');
        statusLabel.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-rose-500 mr-1"></i> Upload Failed. Try again.`;
        showToast(err.message, "Parsing Error", "error");
    }
}


// --- LOAD USER PROFILE DATA ---
async function loadUserProfileData() {
    try {
        const profile = await apiRequest('/api/auth/profile', 'GET');
        
        // Populate profile form inputs
        document.getElementById('profFullname').value = profile.full_name || '';
        document.getElementById('profEmail').value = profile.email || '';
        document.getElementById('profPhone').value = profile.phone || '';
        document.getElementById('profLocation').value = profile.location || '';
        document.getElementById('profLinkedin').value = profile.linkedin || '';
        document.getElementById('profPortfolio').value = profile.portfolio || '';
        document.getElementById('profExperience').value = profile.experience_years || 0;
        document.getElementById('profCurrentPos').value = profile.current_position || '';
        document.getElementById('profPreviousPos').value = profile.previous_position || '';
        document.getElementById('profIndustry').value = profile.industry || '';
        document.getElementById('profSkills').value = profile.skills || '';
        document.getElementById('profCerts').value = profile.certifications || '';
        document.getElementById('profEducation').value = profile.education || '';
        document.getElementById('profAchievements').value = profile.achievements || '';
        
        // Sync credit balance displays
        const user = await apiRequest('/api/auth/user', 'GET');
        updateCreditsDisplay(user.credits, user.subscription_status);
        
    } catch (err) {
        showToast(err.message, "Load Profile Error", "error");
    }
}

// --- SAVE PROFILE DETAILS ---
async function saveUserProfile(e) {
    e.preventDefault();
    const payload = {
        full_name: document.getElementById('profFullname').value,
        email: document.getElementById('profEmail').value,
        phone: document.getElementById('profPhone').value,
        location: document.getElementById('profLocation').value,
        linkedin: document.getElementById('profLinkedin').value,
        portfolio: document.getElementById('profPortfolio').value,
        experience_years: parseInt(document.getElementById('profExperience').value) || 0,
        current_position: document.getElementById('profCurrentPos').value,
        previous_position: document.getElementById('profPreviousPos').value,
        industry: document.getElementById('profIndustry').value,
        skills: document.getElementById('profSkills').value,
        certifications: document.getElementById('profCerts').value,
        education: document.getElementById('profEducation').value,
        achievements: document.getElementById('profAchievements').value
    };
    
    try {
        const res = await apiRequest('/api/auth/profile', 'PUT', payload);
        showToast(res.message, "Success", "success");
    } catch (err) {
        showToast(err.message, "Save Failed", "error");
    }
}

// --- SYNC PROFILE INTO WIZARD ---
async function loadProfileIntoWizard() {
    try {
        const profile = await apiRequest('/api/auth/profile', 'GET');
        
        // Sync Step 1 Details
        document.getElementById('wizFullname').value = profile.full_name || '';
        document.getElementById('wizEmail').value = profile.email || '';
        document.getElementById('wizPhone').value = profile.phone || '';
        document.getElementById('wizLocation').value = profile.location || '';
        document.getElementById('wizLinkedin').value = profile.linkedin || '';
        document.getElementById('wizPortfolio').value = profile.portfolio || '';
        
        // Sync Step 3 Details
        document.getElementById('wizExperience').value = profile.experience_years || 0;
        document.getElementById('wizCurrentPos').value = profile.current_position || '';
        document.getElementById('wizPreviousPos').value = profile.previous_position || '';
        document.getElementById('wizIndustry').value = profile.industry || '';
        document.getElementById('wizSkills').value = profile.skills || '';
        document.getElementById('wizCerts').value = profile.certifications || '';
        document.getElementById('wizEducation').value = profile.education || '';
        document.getElementById('wizAchievements').value = profile.achievements || '';
        
        showToast("Profile credentials synchronized to Wizard form fields.", "Synced", "success");
    } catch (err) {
        showToast("Failed to fetch profile: " + err.message, "Sync Failed", "error");
    }
}

// --- WIZARD NAVIGATION STEPPER ---
function updateWizardProgress() {
    // Hide all step sections
    document.querySelectorAll('.wizard-step-section').forEach(s => s.classList.add('hidden'));
    
    // Remove active and completed classes from steppers
    for (let i = 1; i <= 5; i++) {
        const indicator = document.getElementById(`wizardStepIndicator-${i}`);
        indicator.className = "step-item flex-1";
        if (i < currentWizardStep) {
            indicator.classList.add('completed');
        } else if (i === currentWizardStep) {
            indicator.classList.add('active');
        }
    }
    
    // Show current step section
    document.getElementById(`wizardStep-${currentWizardStep}`).classList.remove('hidden');
    
    // Configure buttons states
    document.getElementById('wizPrevBtn').disabled = (currentWizardStep === 1 || currentWizardStep === 5);
    
    const nextBtn = document.getElementById('wizNextBtn');
    if (currentWizardStep === 4) {
        nextBtn.innerHTML = `Generate AI Letter <i class="fa-solid fa-wand-magic-sparkles ml-1"></i>`;
    } else if (currentWizardStep === 5) {
        // Step 5 has editor, so hide standard next/prev button footer entirely
        document.getElementById('wizardNavButtons').classList.add('hidden');
    } else {
        document.getElementById('wizardNavButtons').classList.remove('hidden');
        nextBtn.innerHTML = `Next <i class="fa-solid fa-arrow-right ml-1"></i>`;
    }
}

function wizardNext() {
    if (currentWizardStep < 4) {
        currentWizardStep++;
        updateWizardProgress();
    } else if (currentWizardStep === 4) {
        currentWizardStep++;
        updateWizardProgress();
        triggerCoverLetterGeneration();
    }
}

function wizardPrev() {
    if (currentWizardStep > 1) {
        currentWizardStep--;
        updateWizardProgress();
    }
}

// Select tone on Step 4
function selectWizardTone(toneName) {
    selectedWizardTone = toneName;
    document.querySelectorAll('#toneSelectorGrid button').forEach(btn => btn.classList.remove('active'));
    const safeId = toneName.replace(' ', '');
    const activeBtn = document.getElementById(`toneBtn-${safeId}`);
    if (activeBtn) activeBtn.classList.add('active');
}

// --- TRIGGER COVER LETTER GENERATION ---
async function triggerCoverLetterGeneration() {
    document.getElementById('wizardLoadingScreen').classList.remove('hidden');
    document.getElementById('wizardWorkspace').classList.add('hidden');
    
    const payload = {
        profile: {
            full_name: document.getElementById('wizFullname').value,
            email: document.getElementById('wizEmail').value,
            phone: document.getElementById('wizPhone').value,
            location: document.getElementById('wizLocation').value,
            linkedin: document.getElementById('wizLinkedin').value,
            portfolio: document.getElementById('wizPortfolio').value,
            experience_years: parseInt(document.getElementById('wizExperience').value) || 0,
            current_position: document.getElementById('wizCurrentPos').value,
            previous_position: document.getElementById('wizPreviousPos').value,
            industry: document.getElementById('wizIndustry').value,
            skills: document.getElementById('wizSkills').value,
            certifications: document.getElementById('wizCerts').value,
            education: document.getElementById('wizEducation').value,
            achievements: document.getElementById('wizAchievements').value
        },
        job_details: {
            job_title: document.getElementById('wizJobtitle').value,
            company_name: document.getElementById('wizCompany').value,
            hiring_manager: document.getElementById('wizManager').value,
            job_description: document.getElementById('wizDescription').value,
            job_location: document.getElementById('wizJobLoc').value,
            employment_type: document.getElementById('wizType').value,
            salary: document.getElementById('wizSalary').value
        },
        writing_style: selectedWizardTone,
        template_name: activeLetter ? activeLetter.template_name : "modern"
    };
    
    try {
        const response = await apiRequest('/api/cover-letter/generate', 'POST', payload);
        activeLetter = response;
        
        // Hide loading screen, show workspace
        document.getElementById('wizardLoadingScreen').classList.add('hidden');
        document.getElementById('wizardWorkspace').classList.remove('hidden');
        
        // Highlight active version tab
        updateVersionTabsVisuals(response.active_version);
        
        // Load active version content into editor
        document.getElementById('workspaceEditorText').value = response.content;
        document.getElementById('workspaceToneSelector').value = response.writing_style.charAt(0).toUpperCase() + response.writing_style.slice(1);
        
        // Load live preview
        updateLetterPreviewLive();
        
        // Render ATS report
        renderAtsReport(response);
        
        // Generate Template presets selection badges
        buildTemplateSelectorBadges();
        
        // Refresh credits remaining bar
        loadUserProfileData();
        
        showToast("Cover Letter generated successfully!", "Success", "success");
        
    } catch (err) {
        showToast(err.message, "Generation Failed", "error");
        currentWizardStep = 4;
        updateWizardProgress();
    }
}

// --- SWITCH COVER LETTER ACTIVE VERSION ---
async function switchActiveVersion(ver) {
    if (!activeLetter || !activeLetter.content_versions) return;
    
    activeLetter.active_version = ver;
    const activeText = activeLetter.content_versions[`version_${ver}`];
    
    // Update input box
    document.getElementById('workspaceEditorText').value = activeText;
    
    // Sync buttons active state
    updateVersionTabsVisuals(ver);
    
    // Update preview block
    updateLetterPreviewLive();
    
    try {
        // Persist version toggle to server
        const response = await apiRequest(`/api/cover-letters/${activeLetter.id}`, 'PUT', {
            active_version: ver
        });
        
        // Re-render ATS scores for this version
        renderAtsReport(response);
    } catch (e) {
        console.error("Failed to sync version switch with backend:", e);
    }
}

function updateVersionTabsVisuals(ver) {
    document.querySelectorAll('#versionSelectorTabs button').forEach(b => b.classList.remove('active'));
    const activeBtn = document.getElementById(`vBtn-${ver}`);
    if (activeBtn) activeBtn.classList.add('active');
}

// --- DYNAMIC LIVE SHEET PREVIEW ---
function updateLetterPreviewLive() {
    const editorVal = document.getElementById('workspaceEditorText').value;
    
    // Render text formatting
    const nameVal = document.getElementById('wizFullname').value || 'APPLICANT NAME';
    const emailVal = document.getElementById('wizEmail').value || '';
    const phoneVal = document.getElementById('wizPhone').value || '';
    const locVal = document.getElementById('wizLocation').value || '';
    
    document.getElementById('previewHeaderName').textContent = nameVal.toUpperCase();
    
    let contactStr = `${locVal}`;
    if (phoneVal) contactStr += `  |  ${phoneVal}`;
    if (emailVal) contactStr += `  |  ${emailVal}`;
    
    const wizLinkedin = document.getElementById('wizLinkedin').value;
    if (wizLinkedin) contactStr += `  |  LinkedIn`;
    
    document.getElementById('previewHeaderContact').textContent = contactStr;
    
    let bodyText = editorVal;
    const salutationIndex = bodyText.search(/dear/i);
    if (salutationIndex !== -1 && salutationIndex < 150) {
        bodyText = bodyText.substring(salutationIndex);
    }
    
    document.getElementById('previewBodyContent').textContent = bodyText;
    
    // Update word count
    const wordCount = editorVal.trim().split(/\s+/).filter(w => w.length > 0).length;
    document.getElementById('wordCounter').textContent = `Words: ${wordCount}`;
    
    // Locally save editor modifications to global active object
    if (activeLetter && activeLetter.content_versions) {
        activeLetter.content_versions[`version_${activeLetter.active_version}`] = editorVal;
        
        // Debounced local saving to database
        debouncedDatabaseSave();
    }
}

// Debounce DB edits to prevent flooding requests
let saveTimeout = null;
function debouncedDatabaseSave() {
    if (saveTimeout) clearTimeout(saveTimeout);
    saveTimeout = setTimeout(async () => {
        if (!activeLetter) return;
        const currentText = document.getElementById('workspaceEditorText').value;
        try {
            await apiRequest(`/api/cover-letters/${activeLetter.id}`, 'PUT', {
                active_version: activeLetter.active_version,
                content: currentText
            });
        } catch (e) {
            console.error("Failed auto saving cover letter progress:", e);
        }
    }, 1500);
}

// --- TEMPLATES SELECTION ACCENTS ---
function buildTemplateSelectorBadges() {
    const container = document.getElementById('templatePresetBadges');
    if (!container) return;
    
    container.innerHTML = '';
    
    TEMPLATES_LIST.forEach(temp => {
        const isSelected = activeLetter && activeLetter.template_name === temp;
        const badge = document.createElement('button');
        badge.className = `btn btn-xs text-xs py-1 px-2.5 rounded border transition-all ${
            isSelected ? 'btn-primary border-primary' : 'btn-outline-glass border-gray-800 text-gray-400'
        }`;
        badge.textContent = temp.charAt(0).toUpperCase() + temp.slice(1).replace('-', ' ');
        badge.onclick = () => selectLetterTemplateStyle(temp, badge);
        container.appendChild(badge);
    });
}

async function selectLetterTemplateStyle(tempName, element) {
    if (!activeLetter) return;
    
    document.querySelectorAll('#templatePresetBadges button').forEach(b => {
        b.className = "btn btn-xs text-xs py-1 px-2.5 rounded border border-gray-800 text-gray-400 btn-outline-glass";
    });
    
    element.className = "btn btn-xs text-xs py-1 px-2.5 rounded border btn-primary border-primary";
    
    const sheet = document.getElementById('printableLetterPreview');
    sheet.className = "letter-sheet template-" + tempName;
    
    try {
        await apiRequest(`/api/cover-letters/${activeLetter.id}`, 'PUT', {
            template_name: tempName
        });
        activeLetter.template_name = tempName;
    } catch (e) {
        console.error("Failed to persist template selection:", e);
    }
}

// --- AI IMPROVEMENTS TEXT MANIPULATIONS ---
async function runAiImprovement(opType) {
    if (!activeLetter) return;
    
    const editor = document.getElementById('workspaceEditorText');
    const loadingMessage = `[Generating AI ${opType} revision...]`;
    editor.value = loadingMessage;
    
    try {
        const response = await apiRequest(`/api/cover-letters/${activeLetter.id}/improve`, 'POST', {
            operation: opType,
            tone: selectedWizardTone
        });
        
        activeLetter = response;
        editor.value = response.content;
        
        // Re-render
        updateLetterPreviewLive();
        renderAtsReport(response);
        showToast(`Refined text successfully! Applied: ${opType}`, "AI Editor", "success");
    } catch (err) {
        showToast(err.message, "AI Improvement Error", "error");
        editor.value = activeLetter.content_versions[`version_${activeLetter.active_version}`]; // revert
    }
}

async function changeWorkspaceTone() {
    const toneVal = document.getElementById('workspaceToneSelector').value;
    selectedWizardTone = toneVal;
    runAiImprovement(`Change Tone to ${toneVal}`);
}

// Copy the Personalized hook to clipboard
function copyPersonalizedHook() {
    const hook = document.getElementById('personalizationHooksText').textContent.replace(/"/g, '').trim();
    navigator.clipboard.writeText(hook).then(() => {
        showToast("Admiration sentence copied! Paste it into your letter.", "Hook Copied", "success");
    });
}

// --- SAVED COVER LETTERS PORTFOLIO FOLDER ---
async function loadSavedLetters() {
    const grid = document.getElementById('lettersListGrid');
    if (!grid) return;
    
    grid.innerHTML = `
        <div class="text-center py-16 text-gray-400 w-full col-12">
            <i class="fa-solid fa-spinner fa-spin text-2xl mb-2"></i>
            <p class="text-xs">Fetching saved letters from server...</p>
        </div>
    `;
    
    try {
        savedLettersList = await apiRequest('/api/cover-letters', 'GET');
        renderSavedLettersList(savedLettersList);
    } catch (err) {
        grid.innerHTML = `
            <div class="alert alert-danger mx-auto max-w-sm text-center text-xs">
                Failed to load saved letters: ${err.message}
            </div>
        `;
    }
}

function renderSavedLettersList(list) {
    const grid = document.getElementById('lettersListGrid');
    if (!grid) return;
    
    if (list.length === 0) {
        grid.innerHTML = `
            <div class="text-center py-16 text-gray-500 w-full col-12">
                <i class="fa-solid fa-folder-open text-4xl mb-3"></i>
                <h5 class="text-base font-bold">No Saved Letters Yet</h5>
                <p class="text-xs max-w-sm mx-auto mt-2">Any cover letters you create using the AI wizard will be saved here for edit, export and sharing.</p>
                <button onclick="showDashView('wizard')" class="btn btn-primary-glow btn-sm mt-4 text-xs">Create New Letter</button>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = '';
    
    list.forEach(letter => {
        const col = document.createElement('div');
        col.className = "col-md-6 col-lg-4";
        
        const favClass = letter.is_favorite ? 'fa-solid text-pink-500' : 'fa-regular text-gray-500';
        
        col.innerHTML = `
            <div class="glass-panel p-5 h-100 flex flex-col justify-between hover:-translate-y-1 transition duration-300 border-t-4 border-indigo-500">
                <div>
                    <div class="flex justify-between items-center mb-3">
                        <span class="text-[10px] uppercase font-bold text-gray-500">${letter.template_name} Layout</span>
                        <button onclick="toggleFavoriteLetter(${letter.id}, this)" class="btn btn-link p-0 text-decoration-none">
                            <i class="${favClass} fa-heart text-sm"></i>
                        </button>
                    </div>
                    <h5 class="text-base font-bold mb-1 text-white line-clamp-1">${letter.title}</h5>
                    <p class="text-xs text-gray-400 mb-2">${letter.company_name} &bull; ${letter.job_title}</p>
                    <div class="flex items-center gap-2 mb-4">
                        <div class="badge bg-slate-900 border border-gray-800 text-[10px]">ATS: ${letter.ats_score}%</div>
                        <div class="badge bg-slate-900 border border-gray-800 text-[10px] text-gray-400 capitalize">${letter.writing_style}</div>
                    </div>
                    <p class="text-xs text-gray-400 line-clamp-3 mb-6 bg-slate-950/30 p-2.5 rounded font-serif italic">
                        "${letter.content.substring(0, 140)}..."
                    </p>
                </div>
                
                <div class="d-grid gap-2">
                    <div class="flex gap-2">
                        <button onclick="editSavedLetter(${letter.id})" class="btn btn-outline-glass btn-sm text-xs py-2 flex-grow"><i class="fa-solid fa-pen-to-square"></i> Open Editor</button>
                        <button onclick="duplicateSavedLetter(${letter.id})" class="btn btn-outline-glass btn-sm text-xs py-2" title="Duplicate"><i class="fa-solid fa-copy"></i></button>
                        <button onclick="deleteSavedLetter(${letter.id})" class="btn btn-outline-glass btn-sm text-xs py-2 text-red-400 hover:bg-red-500/10" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(col);
    });
}

// Favorite toggle
async function toggleFavoriteLetter(id, element) {
    try {
        const res = await apiRequest(`/api/cover-letters/${id}/favorite`, 'POST');
        const icon = element.querySelector('i');
        
        if (res.is_favorite) {
            icon.className = "fa-solid fa-heart text-sm text-pink-500";
            showToast("Added to Favorites", "Favorites", "success");
        } else {
            icon.className = "fa-regular fa-heart text-sm text-gray-500";
            showToast("Removed from Favorites", "Favorites", "success");
        }
        
        // Refresh lists local cache
        const index = savedLettersList.findIndex(x => x.id === id);
        if (index !== -1) savedLettersList[index].is_favorite = res.is_favorite;
        
    } catch (e) {
        showToast(e.message, "Favorite Error", "error");
    }
}

async function duplicateSavedLetter(id) {
    try {
        await apiRequest(`/api/cover-letters/${id}/duplicate`, 'POST');
        showToast("Letter duplicated successfully!", "Duplicated", "success");
        loadSavedLetters();
    } catch (e) {
        showToast(e.message, "Failed to Duplicate", "error");
    }
}

async function deleteSavedLetter(id) {
    if (!confirm("Are you sure you want to delete this cover letter? This cannot be undone.")) return;
    
    try {
        const res = await apiRequest(`/api/cover-letters/${id}`, 'DELETE');
        showToast(res.message, "Deleted", "success");
        loadSavedLetters();
    } catch (e) {
        showToast(e.message, "Delete Failed", "error");
    }
}

async function editSavedLetter(id) {
    try {
        const letter = await apiRequest(`/api/cover-letters/${id}`, 'GET');
        activeLetter = letter;
        
        // Populate Wizard inputs for steps 1-3 to support live preview calculations
        document.getElementById('wizJobtitle').value = letter.job_title;
        document.getElementById('wizCompany').value = letter.company_name;
        document.getElementById('wizManager').value = letter.hiring_manager;
        document.getElementById('wizDescription').value = letter.job_description;
        document.getElementById('wizJobLoc').value = letter.job_location;
        document.getElementById('wizSalary').value = letter.salary;
        
        // Sync profile details
        const profile = await apiRequest('/api/auth/profile', 'GET');
        document.getElementById('wizFullname').value = profile.full_name || '';
        document.getElementById('wizEmail').value = profile.email || '';
        document.getElementById('wizPhone').value = profile.phone || '';
        document.getElementById('wizLocation').value = profile.location || '';
        
        // Open Step 5 workspace
        currentWizardStep = 5;
        updateWizardProgress();
        showDashView('wizard');
        
        document.getElementById('wizardLoadingScreen').className = "hidden";
        document.getElementById('wizardWorkspace').className = "row";
        
        document.getElementById('workspaceEditorText').value = letter.content;
        document.getElementById('workspaceToneSelector').value = letter.writing_style.charAt(0).toUpperCase() + letter.writing_style.slice(1);
        
        // Synchronize active version tabs classes
        updateVersionTabsVisuals(letter.active_version || 'a');
        
        // Render previews
        updateLetterPreviewLive();
        renderAtsReport(letter);
        buildTemplateSelectorBadges();
        
    } catch (e) {
        showToast("Failed to fetch letter: " + e.message, "Editor Error", "error");
    }
}

// Search and complex filters/sorting
function searchSavedLetters() {
    const query = document.getElementById('lettersSearchInput').value.toLowerCase();
    const filtered = savedLettersList.filter(l => 
        l.title.toLowerCase().includes(query) || 
        l.company_name.toLowerCase().includes(query) ||
        l.job_title.toLowerCase().includes(query)
    );
    renderSavedLettersList(filtered);
}

function filterSavedLetters() {
    const filterVal = document.getElementById('lettersFilterSelect').value;
    let listCopy = [...savedLettersList];
    
    // 1. Filtering
    if (filterVal === 'favorites') {
        listCopy = listCopy.filter(l => l.is_favorite);
    }
    
    // 2. Sorting
    if (filterVal === 'title') {
        listCopy.sort((x, y) => x.title.localeCompare(y.title));
    } else if (filterVal === 'company') {
        listCopy.sort((x, y) => x.company_name.localeCompare(y.company_name));
    } else if (filterVal === 'score') {
        listCopy.sort((x, y) => y.ats_score - x.ats_score); // Descending match
    }
    
    renderSavedLettersList(listCopy);
}

// --- LOGTIMELINE VIEWER ---
async function loadHistoryLogs() {
    const tbody = document.getElementById('historyLogsTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = `<tr><td colspan="3" class="text-center text-gray-500 py-4"><i class="fa-solid fa-spinner fa-spin mr-2"></i> Querying audit trails...</td></tr>`;
    
    try {
        const response = await apiRequest('/api/admin/activities', 'GET');
        if (response.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="text-center text-gray-500 py-4">No logged history actions found.</td></tr>`;
            return;
        }
        
        tbody.innerHTML = '';
        response.forEach(log => {
            const date = new Date(log.timestamp).toLocaleString();
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${log.action}</span></td>
                <td class="text-gray-400 font-mono text-xs">${date}</td>
                <td>${log.details || 'Successfully logged action.'}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="3" class="text-center text-danger py-4">Failed to fetch usage logs: ${e.message}</td></tr>`;
    }
}

// --- SAAS CREDIT UPDATES & DEV TOOLKITS ---
function updateCreditsDisplay(credits, status) {
    document.getElementById('userCreditVal').textContent = `${credits} / 5`;
    const bar = document.getElementById('userCreditBar');
    if (bar) {
        const percent = (credits / 5) * 100;
        bar.style.width = `${percent}%`;
        if (credits === 0) {
            bar.className = "bg-rose-500 h-full";
        } else if (credits <= 2) {
            bar.className = "bg-amber-500 h-full";
        } else {
            bar.className = "bg-indigo-500 h-full";
        }
    }
    
    // Update subscription plan label
    document.getElementById('subsStatusVal').textContent = status;
}

async function refillCreditsDev() {
    try {
        const res = await apiRequest('/api/credits/refill', 'POST');
        showToast(res.message, "Developer Sandbox", "success");
        loadUserProfileData();
    } catch (e) {
        showToast(e.message, "Credit Refill Failed", "error");
    }
}

async function upgradeTierSimulate() {
    try {
        const user = JSON.parse(localStorage.getItem('user'));
        user.subscription_status = 'Premium Pro';
        user.credits = 999;
        localStorage.setItem('user', JSON.stringify(user));
        
        updateCreditsDisplay(999, 'Premium Pro');
        showToast("Upgraded account package simulated successfully! Unlimited access granted.", "Premium Pro Active", "success");
    } catch (e) {
        showToast(e.message, "Upgrade Error", "error");
    }
}

async function resetAccountDev() {
    if (!confirm("Reset database settings? This will clear all data and reset sandbox entries.")) return;
    localStorage.clear();
    showToast("Sandbox database cleared. Logging out...", "Sandbox Reset", "warning");
    setTimeout(() => window.location.href = '/', 1500);
}

// Init dashboard views
document.addEventListener("DOMContentLoaded", () => {
    if (!localStorage.getItem('token')) {
        window.location.href = '/login';
    } else {
        loadUserProfileData();
        updateWizardProgress();
    }
});
