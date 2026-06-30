// --- ADMINISTRATIVE STATE LOGS ---
let adminStats = null;
let timelineChartInstance = null;
let subscriptionChartInstance = null;

// --- INITIATE ADMIN PANEL DATA ---
async function initAdminPanel() {
    try {
        adminStats = await apiRequest('/api/admin/stats', 'GET');
        
        // 1. Fill overview text statistics
        document.getElementById('statTotalUsers').textContent = adminStats.total_users || 0;
        document.getElementById('statTotalLetters').textContent = adminStats.total_letters_generated || 0;
        document.getElementById('statCreditsUsed').textContent = adminStats.total_credits_used || 0;
        document.getElementById('statTotalFeedback').textContent = adminStats.feedback_received || 0;
        
        // 2. Render Chart.js dashboards
        renderAdminCharts(adminStats);
        
        // 3. Load user lists
        loadAdminUsersList();
        
        // 4. Load feedback tickets
        loadAdminFeedbackList();
        
        // 5. Load system activities logs
        loadAdminActivitiesList();
        
    } catch (e) {
        showToast("Failed to fetch admin stats: " + e.message, "Unauthorized", "error");
        setTimeout(() => window.location.href = '/dashboard', 2000);
    }
}

// --- RENDER DYNAMIC CHART.JS GRAPHS ---
function renderAdminCharts(stats) {
    // A. Generations Timeline Chart (Past 7 Days)
    const timelineCtx = document.getElementById('generationsTimelineChart');
    if (timelineCtx) {
        const timelineData = stats.generation_timeline || [];
        const labels = timelineData.map(d => d.date);
        const dataValues = timelineData.map(d => d.count);
        
        if (timelineChartInstance) timelineChartInstance.destroy();
        
        timelineChartInstance = new Chart(timelineCtx, {
            type: 'bar',
            data: {
                labels: labels.length ? labels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Letters Generated',
                    data: dataValues.length ? dataValues : [3, 5, 8, 12, 18, 14, 22],
                    backgroundColor: 'rgba(99, 102, 241, 0.4)',
                    borderColor: '#6366f1',
                    borderWidth: 2,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    x: {
                        ticks: { color: '#9ca3af' },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f3f4f6' } }
                }
            }
        });
    }
    
    // B. Subscription Plan Split Chart
    const subCtx = document.getElementById('subscriptionSplitChart');
    if (subCtx) {
        const subs = stats.subscriptions || {};
        const labels = Object.keys(subs).length ? Object.keys(subs) : ['Free Tier', 'Premium Pro', 'Enterprise'];
        const values = Object.keys(subs).length ? Object.values(subs) : [100, 45, 12];
        
        if (subscriptionChartInstance) subscriptionChartInstance.destroy();
        
        subscriptionChartInstance = new Chart(subCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.6)',  // Indigo
                        'rgba(236, 72, 153, 0.6)',  // Pink
                        'rgba(16, 185, 129, 0.6)'   // Emerald
                    ],
                    borderColor: 'rgba(11, 15, 25, 0.8)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#f3f4f6', boxWidth: 12 }
                    }
                }
            }
        });
    }
}

// --- TAB 1: USERS LISTS ---
async function loadAdminUsersList() {
    const tbody = document.getElementById('adminUsersTableBody');
    if (!tbody) return;
    
    try {
        const users = await apiRequest('/api/admin/users', 'GET');
        tbody.innerHTML = '';
        
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-gray-500 py-4">No users found.</td></tr>`;
            return;
        }
        
        users.forEach(u => {
            const date = new Date(u.created_at).toLocaleDateString();
            const row = document.createElement('tr');
            
            // Highlight role
            const badgeColor = u.role === 'admin' ? 'bg-pink-500/10 text-pink-400 border-pink-500/20' : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
            
            row.innerHTML = `
                <td>
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center font-bold text-xs">${u.username.substring(0,2).toUpperCase()}</div>
                        <div>
                            <span class="font-bold text-white">${u.username}</span>
                            <span class="badge ${badgeColor} text-[9px] block w-max mt-0.5">${u.role.toUpperCase()}</span>
                        </div>
                    </div>
                </td>
                <td class="font-mono text-xs text-gray-400">${u.email}</td>
                <td><span class="badge bg-slate-900 border border-gray-800 text-xs">${u.subscription_status}</span></td>
                <td class="font-bold">${u.credits} credits</td>
                <td class="text-xs text-gray-400">${date}</td>
                <td class="text-center">
                    <button onclick="deleteUserAdmin(${u.id}, '${u.username}')" class="btn btn-sm btn-outline-glass py-1.5 px-2 text-xs text-red-400 hover:bg-red-500/10" title="Delete User">
                        <i class="fa-solid fa-user-minus"></i> Remove
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">Failed to fetch users: ${e.message}</td></tr>`;
    }
}

async function deleteUserAdmin(id, name) {
    if (!confirm(`Are you absolutely sure you want to delete user ${name}? This will purge their profile and cover letter history logs.`)) return;
    
    try {
        const res = await apiRequest(`/api/admin/users/${id}`, 'DELETE');
        showToast(res.message, "User Deleted", "success");
        initAdminPanel(); // Refresh stats and timelines
    } catch (e) {
        showToast(e.message, "Failed to Delete", "error");
    }
}

// --- TAB 2: FEEDBACK LOGS ---
async function loadAdminFeedbackList() {
    const tbody = document.getElementById('adminFeedbackTableBody');
    if (!tbody) return;
    
    try {
        const feedback = await apiRequest('/api/admin/feedback', 'GET');
        tbody.innerHTML = '';
        
        if (feedback.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-gray-500 py-4">No logged user suggestions.</td></tr>`;
            return;
        }
        
        feedback.forEach(f => {
            const date = new Date(f.timestamp).toLocaleDateString();
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="font-bold text-white">${f.name}</td>
                <td class="font-mono text-xs text-gray-400">${f.email}</td>
                <td class="max-w-xs text-xs line-clamp-1" title="${f.message}">${f.message}</td>
                <td class="text-xs text-gray-400">${date}</td>
                <td class="text-center">
                    <button onclick="deleteFeedbackAdmin(${f.id})" class="btn btn-sm btn-outline-glass py-1.5 px-2 text-xs text-red-400 hover:bg-red-500/10" title="Delete Ticket">
                        <i class="fa-solid fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">Failed to fetch feedback logs: ${e.message}</td></tr>`;
    }
}

async function deleteFeedbackAdmin(id) {
    try {
        const res = await apiRequest(`/api/admin/feedback/${id}`, 'DELETE');
        showToast(res.message, "Ticket Purged", "success");
        loadAdminFeedbackList();
    } catch (e) {
        showToast(e.message, "Purge Failed", "error");
    }
}

// --- TAB 3: SYSTEM AUDIT TRAIL LOGS ---
async function loadAdminActivitiesList() {
    const tbody = document.getElementById('adminActivityTableBody');
    if (!tbody) return;
    
    try {
        const logs = await apiRequest('/api/admin/activities', 'GET');
        tbody.innerHTML = '';
        
        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-gray-500 py-4">No audit logs found.</td></tr>`;
            return;
        }
        
        logs.forEach(l => {
            const date = new Date(l.timestamp).toLocaleString();
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="font-mono text-xs text-gray-400">User #${l.user_id}</td>
                <td><span class="badge bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${l.action}</span></td>
                <td class="text-xs text-gray-400 font-mono">${date}</td>
                <td class="text-xs text-gray-300">${l.details || 'Successfully logged action'}</td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-4">Failed to fetch audit trails: ${e.message}</td></tr>`;
    }
}

// Run init when dashboard DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    // Confirm client is logged in before initialization
    if (localStorage.getItem('token')) {
        initAdminPanel();
    } else {
        window.location.href = '/login';
    }
});
