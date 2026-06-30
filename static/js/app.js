// --- GLOBAL TOAST ALERTS ---
function showToast(message, title = "Notification", type = "info") {
    const toastEl = document.getElementById('globalToast');
    if (!toastEl) return;
    
    document.getElementById('toastTitle').textContent = title;
    document.getElementById('toastMessage').textContent = message;
    
    const iconEl = document.getElementById('toastIcon');
    iconEl.className = "fa-solid mr-2 ";
    
    if (type === "success") {
        iconEl.className += "fa-circle-check text-emerald-400";
    } else if (type === "error") {
        iconEl.className += "fa-triangle-exclamation text-rose-500";
    } else {
        iconEl.className += "fa-circle-info text-indigo-400";
    }
    
    const bootstrapToast = new bootstrap.Toast(toastEl);
    bootstrapToast.show();
}

// --- GLOBAL API WRAPPER ---
async function apiRequest(url, method = 'GET', body = null) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        method,
        headers
    };
    
    if (body) {
        config.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            // Handle token expiry
            if (response.status === 401 && (data.error || '').includes("expired")) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                showToast("Your session has expired. Please log in again.", "Session Expired", "error");
                setTimeout(() => window.location.href = '/login', 2000);
            }
            throw new Error(data.error || 'API Request Failed');
        }
        return data;
    } catch (error) {
        console.error(`API Error on ${url}:`, error);
        throw error;
    }
}

// --- DYNAMIC NAVBAR CONFIGURATION ---
function configureNavbar() {
    const navAuth = document.getElementById('navAuthSection');
    if (!navAuth) return;
    
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
        try {
            const user = JSON.parse(userStr);
            let adminLink = '';
            
            // Show Admin Panel option if user is an admin
            if (user.role === 'admin') {
                adminLink = `<a href="/admin" class="btn btn-outline-glass px-3 py-1.5 text-xs font-semibold border-pink-500/50 hover:bg-pink-500/10 text-pink-400">Admin Control</a>`;
                const sideAdmin = document.getElementById('sideBtn-admin');
                if (sideAdmin) sideAdmin.classList.remove('hidden');
            }
            
            navAuth.innerHTML = `
                ${adminLink}
                <a href="/dashboard" class="btn btn-outline-glass px-3 py-1.5 text-xs font-semibold">My Workspace</a>
                <span class="text-xs text-gray-400 font-mono hidden md:inline">Hi, ${user.username}</span>
                <button onclick="handleLogout()" class="btn btn-primary-glow px-3 py-1.5 text-xs font-semibold">Logout</button>
            `;
        } catch (e) {
            console.error("Error configuring navbar details:", e);
        }
    } else {
        navAuth.innerHTML = `
            <a href="/login" class="btn btn-outline-glass px-4 py-2 text-sm font-medium">Log In</a>
            <a href="/login?signup=true" class="btn btn-primary-glow px-4 py-2 text-sm font-medium">Get Started Free</a>
        `;
    }
}

// --- LOGOUT HANDLER ---
function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showToast("Logged out successfully.", "Goodbye!", "success");
    setTimeout(() => window.location.href = '/', 1000);
}

// --- AUTHENTICATION ROUTINES ---
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await apiRequest('/api/auth/login', 'POST', { email, password });
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        showToast(response.message, "Success", "success");
        setTimeout(() => {
            if (response.user.role === 'admin') {
                window.location.href = '/admin';
            } else {
                window.location.href = '/dashboard';
            }
        }, 1200);
    } catch (err) {
        showToast(err.message, "Login Failed", "error");
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    
    try {
        const response = await apiRequest('/api/auth/register', 'POST', { username, email, password });
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        showToast(response.message, "Registration Complete", "success");
        setTimeout(() => window.location.href = '/dashboard', 1200);
    } catch (err) {
        showToast(err.message, "Sign Up Failed", "error");
    }
}

async function handleForgotPassword(e) {
    e.preventDefault();
    const email = document.getElementById('forgotEmail').value;
    
    try {
        const response = await apiRequest('/api/auth/forgot-password', 'POST', { email });
        showToast(response.message, "Code Sent", "success");
        
        // Auto-switch tabs to verify
        if (response.dev_sandbox) {
            document.getElementById('resetCode').value = response.verification_code;
        }
        
        // Switch section to verification box
        switchAuthTab('verify');
    } catch (err) {
        showToast(err.message, "Token Request Failed", "error");
    }
}

async function handleVerifyReset(e) {
    e.preventDefault();
    const email = document.getElementById('forgotEmail').value;
    const code = document.getElementById('resetCode').value;
    const new_password = document.getElementById('resetNewPassword').value;
    
    try {
        const response = await apiRequest('/api/auth/reset-password', 'POST', { email, code, new_password });
        showToast(response.message, "Password Reset", "success");
        setTimeout(() => switchAuthTab('login'), 1500);
    } catch (err) {
        showToast(err.message, "Verification Failed", "error");
    }
}

// --- FEEDBACK SUBMISSION ---
async function submitFooterFeedback() {
    const nameInput = document.getElementById('footerFeedbackName');
    const emailInput = document.getElementById('footerFeedbackEmail');
    const msgInput = document.getElementById('footerFeedbackMsg');
    
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const message = msgInput.value.trim();
    
    if (!name || !email || !message) {
        showToast("Please fill in all feedback form fields.", "Incomplete Fields", "error");
        return;
    }
    
    try {
        const response = await apiRequest('/api/feedback', 'POST', { name, email, message });
        showToast(response.message, "Feedback Submitted", "success");
        nameInput.value = "";
        emailInput.value = "";
        msgInput.value = "";
    } catch (err) {
        showToast(err.message, "Submission Failed", "error");
    }
}

// Automatically configure navbar when script loads
document.addEventListener("DOMContentLoaded", configureNavbar);
