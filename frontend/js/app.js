// Global state
let currentUser = null;
let currentInterview = null;

// Initialize app
function initApp() {
    if (!checkAuth()) return;

    const user = JSON.parse(localStorage.getItem('user'));
    if (user) {
        currentUser = user;
        document.getElementById('userName').textContent = user.full_name || user.email;
        document.getElementById('mainNav').style.display = 'block';
    }

    navigateTo('dashboard');
}

// Navigation
function navigateTo(page, params = {}) {
    switch(page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'resumes':
            loadResumes();
            break;
        case 'interviews':
            loadInterviews();
            break;
        case 'history':
            loadHistory();
            break;
        case 'upload-resume':
            showUploadResume();
            break;
        case 'start-interview':
            showStartInterview(params.resumeId);
            break;
        case 'interview':
            loadInterview(params.interviewId);
            break;
        case 'interview-result':
            loadInterviewResult(params.interviewId);
            break;
        default:
            loadDashboard();
    }
}

// Dashboard
async function loadDashboard() {
    const content = document.getElementById('mainContent');
    content.innerHTML = '<div class="container mt-4"><div class="text-center"><div class="spinner-border text-primary"></div></div></div>';

    try {
        const data = await dashboardAPI.get();

        content.innerHTML = `
            <div class="container mt-4">
                <h2 class="mb-4">Dashboard</h2>

                <div class="row">
                    <div class="col-md-3">
                        <div class="card stat-card bg-primary text-white">
                            <div class="card-body">
                                <h3>${data.total_interviews}</h3>
                                <p>Total Interviews</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card bg-success text-white">
                            <div class="card-body">
                                <h3>${data.completed_interviews}</h3>
                                <p>Completed</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card bg-info text-white">
                            <div class="card-body">
                                <h3>${data.average_score ? data.average_score.toFixed(1) : 'N/A'}</h3>
                                <p>Average Score</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card bg-warning text-white">
                            <div class="card-body">
                                <h3>${data.readiness_percentage ? Math.round(data.readiness_percentage) + '%' : 'N/A'}</h3>
                                <p>Readiness</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Recent Interviews</h5>
                            </div>
                            <div class="card-body">
                                ${data.recent_interviews.length > 0 ? `
                                    <div class="list-group">
                                        ${data.recent_interviews.map(interview => `
                                            <a href="#" class="list-group-item list-group-item-action" onclick="navigateTo('interview-result', {interviewId: ${interview.id}})">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <h6 class="mb-1">Interview #${interview.id}</h6>
                                                        <small class="text-muted">${new Date(interview.created_at).toLocaleDateString()}</small>
                                                    </div>
                                                    <span class="badge bg-${interview.status === 'completed' ? 'success' : interview.status === 'in_progress' ? 'primary' : 'secondary'}">
                                                        ${interview.status}
                                                    </span>
                                                </div>
                                            </a>
                                        `).join('')}
                                    </div>
                                ` : '<p class="text-muted">No interviews yet</p>'}
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card mb-3">
                            <div class="card-header">
                                <h5 class="mb-0">Top Strengths</h5>
                            </div>
                            <div class="card-body">
                                ${data.top_strengths.length > 0 ? `
                                    <ul class="list-unstyled">
                                        ${data.top_strengths.map(s => `<li><i class="bi bi-check-circle-fill text-success"></i> ${s}</li>`).join('')}
                                    </ul>
                                ` : '<p class="text-muted">Complete an interview to see strengths</p>'}
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Priority Gaps</h5>
                            </div>
                            <div class="card-body">
                                ${data.priority_gaps.length > 0 ? `
                                    <ul class="list-unstyled">
                                        ${data.priority_gaps.map(g => `<li><i class="bi bi-exclamation-circle-fill text-warning"></i> ${g}</li>`).join('')}
                                    </ul>
                                ` : '<p class="text-muted">No gaps identified yet</p>'}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-12 text-center">
                        <button class="btn btn-primary btn-lg" onclick="navigateTo('upload-resume')">
                            <i class="bi bi-upload"></i> Upload Resume & Start Interview
                        </button>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        showToast('Failed to load dashboard: ' + error.message, 'error');
        content.innerHTML = '<div class="container mt-4"><div class="alert alert-danger">Failed to load dashboard</div></div>';
    }
}

// Load Resumes
async function loadResumes() {
    const content = document.getElementById('mainContent');
    content.innerHTML = '<div class="container mt-4"><div class="text-center"><div class="spinner-border text-primary"></div></div></div>';

    try {
        const resumes = await resumeAPI.list();

        content.innerHTML = `
            <div class="container mt-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>My Resumes</h2>
                    <button class="btn btn-primary" onclick="navigateTo('upload-resume')">
                        <i class="bi bi-upload"></i> Upload Resume
                    </button>
                </div>

                ${resumes.length > 0 ? `
                    <div class="row">
                        ${resumes.map(resume => `
                            <div class="col-md-6 mb-3">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">${resume.filename}</h5>
                                        <p class="text-muted mb-2">
                                            <small>Uploaded: ${new Date(resume.created_at).toLocaleDateString()}</small>
                                        </p>
                                        <p class="mb-2">
                                            <span class="badge bg-${resume.is_parsed ? 'success' : 'warning'}">
                                                ${resume.is_parsed ? 'Parsed' : 'Parsing...'}
                                            </span>
                                        </p>
                                        <div class="btn-group" role="group">
                                            <button class="btn btn-sm btn-outline-primary" onclick="viewResumeProfile(${resume.id})" ${!resume.is_parsed ? 'disabled' : ''}>
                                                <i class="bi bi-eye"></i> View Profile
                                            </button>
                                            <button class="btn btn-sm btn-outline-success" onclick="navigateTo('start-interview', {resumeId: ${resume.id}})" ${!resume.is_parsed ? 'disabled' : ''}>
                                                <i class="bi bi-play"></i> Start Interview
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="deleteResume(${resume.id})">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div class="empty-state">
                        <i class="bi bi-file-earmark-text"></i>
                        <h4>No resumes uploaded yet</h4>
                        <p>Upload your resume to start your interview preparation</p>
                        <button class="btn btn-primary" onclick="navigateTo('upload-resume')">
                            <i class="bi bi-upload"></i> Upload Resume
                        </button>
                    </div>
                `}
            </div>
        `;
    } catch (error) {
        showToast('Failed to load resumes: ' + error.message, 'error');
    }
}

// Upload Resume
function showUploadResume() {
    const content = document.getElementById('mainContent');
    content.innerHTML = `
        <div class="container mt-4">
            <h2 class="mb-4">Upload Resume</h2>

            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <div class="file-upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                                <i class="bi bi-cloud-upload" style="font-size: 3rem; color: var(--primary-color);"></i>
                                <h4 class="mt-3">Drop your resume here or click to browse</h4>
                                <p class="text-muted">Supported formats: PDF, DOCX (Max 10MB)</p>
                                <input type="file" id="fileInput" accept=".pdf,.doc,.docx" style="display:none" onchange="handleFileSelect(event)">
                            </div>

                            <div id="uploadProgress" style="display:none" class="mt-3">
                                <div class="progress">
                                    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 100%"></div>
                                </div>
                                <p class="text-center mt-2">Uploading and parsing resume...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Setup drag and drop
    const uploadArea = document.getElementById('uploadArea');

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragging');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragging');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragging');
        const file = e.dataTransfer.files[0];
        if (file) uploadResume(file);
    });
}

async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) await uploadResume(file);
}

async function uploadResume(file) {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Invalid file type. Please upload PDF or DOCX', 'error');
        return;
    }

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showToast('File too large. Maximum size is 10MB', 'error');
        return;
    }

    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('uploadProgress').style.display = 'block';

    try {
        const resume = await resumeAPI.upload(file);
        showToast('Resume uploaded successfully!', 'success');

        // Wait a moment for parsing
        setTimeout(() => {
            navigateTo('start-interview', { resumeId: resume.id });
        }, 2000);
    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('uploadProgress').style.display = 'none';
    }
}

// Utility: Show Toast
function showToast(message, type = 'info') {
    const colors = {
        success: 'bg-success',
        error: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
    };

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white ${colors[type] || colors.info} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    document.getElementById('toastContainer').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initApp);
