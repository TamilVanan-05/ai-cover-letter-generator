// --- CLIENT SIDE PDF EXPORT (html2pdf.js) ---
function exportToPdf() {
    if (!activeLetter) {
        showToast("No active cover letter found to export.", "Export Failed", "error");
        return;
    }
    
    // Check if free user is out of bounds (pro check sandbox mock)
    const user = JSON.parse(localStorage.getItem('user'));
    
    const element = document.getElementById('printableLetterPreview');
    const filename = `${activeLetter.title.replace(/\s+/g, '_')}.pdf`;
    
    // Set html2pdf layout options
    const opt = {
        margin: [0.5, 0.5, 0.5, 0.5], // 0.5 inch borders
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
            scale: 2, // High resolution crisp text rendering
            useCORS: true,
            letterRendering: true
        },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    
    showToast("Generating high-resolution PDF print layout...", "Exporting PDF", "info");
    
    html2pdf().set(opt).from(element).save().then(() => {
        showToast("PDF Cover Letter downloaded successfully!", "Success", "success");
    }).catch(err => {
        showToast("Failed to compile PDF: " + err.message, "PDF Error", "error");
    });
}

// --- SECURE DOCX FILE DOWNLOAD ---
async function exportToDocx() {
    if (!activeLetter) {
        showToast("No active cover letter found to export.", "Export Failed", "error");
        return;
    }
    
    const user = JSON.parse(localStorage.getItem('user'));
    if (user.subscription_status === 'Free Tier') {
        showToast("Premium Pro subscription required to export Word (.docx) formats.", "Feature Locked", "error");
        return;
    }
    
    showToast("Compiling styled Microsoft Word document...", "Exporting DOCX", "info");
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/cover-letters/${activeLetter.id}/export/docx`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to download DOCX');
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `${activeLetter.title.replace(/\s+/g, '_')}.docx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        showToast("Word document downloaded successfully!", "Success", "success");
        
    } catch (e) {
        showToast(e.message, "DOCX Export Failed", "error");
    }
}

// --- COPY TEXT CONTENT TO CLIPBOARD ---
function copyToClipboard() {
    const textVal = document.getElementById('workspaceEditorText').value;
    if (!textVal) {
        showToast("No content to copy.", "Copy Failed", "error");
        return;
    }
    
    navigator.clipboard.writeText(textVal).then(() => {
        showToast("Cover Letter text copied to clipboard!", "Copied", "success");
    }).catch(err => {
        showToast("Clipboard copy failed: " + err.message, "Copy Error", "error");
    });
}

// --- PUBLIC SHARE LINK COPIER ---
function copyShareableLink() {
    if (!activeLetter || !activeLetter.share_token) {
        showToast("Generate a cover letter to share first.", "Share Failed", "error");
        return;
    }
    
    const shareUrl = `${window.location.origin}/share/${activeLetter.share_token}`;
    
    navigator.clipboard.writeText(shareUrl).then(() => {
        showToast("Shareable viewer link copied! Send it directly to recruiters.", "Link Copied", "success");
    }).catch(err => {
        showToast("Clipboard copy failed: " + err.message, "Copy Error", "error");
    });
}

// --- EMAIL MODAL DIALOG CONTROLS ---
let bootstrapEmailModal = null;

function triggerEmailModal() {
    if (!activeLetter) {
        showToast("Create a cover letter to send first.", "Send Failed", "error");
        return;
    }
    
    const modalEl = document.getElementById('emailExportModal');
    bootstrapEmailModal = new bootstrap.Modal(modalEl);
    bootstrapEmailModal.show();
}

async function sendCoverLetterEmailTrigger() {
    const email = document.getElementById('exportRecipEmail').value.trim();
    if (!email) {
        showToast("Please enter a recipient email address.", "Required Input", "error");
        return;
    }
    
    if (bootstrapEmailModal) bootstrapEmailModal.hide();
    showToast("Sending email via SMTP servers...", "Email Dispatch", "info");
    
    try {
        const response = await apiRequest(`/api/cover-letters/${activeLetter.id}/export/email`, 'POST', { email });
        showToast(response.message, "Email Sent", "success");
    } catch (e) {
        showToast(e.message, "Email Failed", "error");
    }
}
