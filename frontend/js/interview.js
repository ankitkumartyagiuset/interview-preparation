// Start Interview Setup
async function showStartInterview(resumeId) {
    const content = document.getElementById('mainContent');
    content.innerHTML = '<div class="container mt-4"><div class="text-center"><div class="spinner-border text-primary"></div></div></div>';

    try {
        const [profile, jobRoles] = await Promise.all([
            resumeAPI.getProfile(resumeId),
            jobAPI.getRoles()
        ]);

        content.innerHTML = `
            <div class="container mt-4">
                <h2 class="mb-4">Start Interview</h2>

                <div class="row">
                    <div class="col-md-8">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h5>Candidate Profile</h5>
                            </div>
                            <div class="card-body">
                                <h6>${profile.full_name || 'N/A'}</h6>
                                <p class="text-muted">${profile.email || ''}</p>
                                <p><strong>Experience:</strong> ${profile.total_experience_years || 0} years</p>
                                <p><strong>Skills:</strong> ${profile.skills.slice(0, 10).map(s => s.skill_name).join(', ')}</p>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h5>Select Target Role</h5>
                            </div>
                            <div class="card-body">
                                <form id="interviewForm" onsubmit="createInterview(event, ${resumeId})">
                                    <div class="mb-3">
                                        <label class="form-label">Job Role</label>
                                        <select class="form-select" name="job_role_id" required>
                                            <option value="">Select a role...</option>
                                            ${jobRoles.map(role => `
                                                <option value="${role.id}">${role.title}</option>
                                            `).join('')}
                                        </select>
                                    </div>

                                    <div class="mb-3">
                                        <label class="form-label">Difficulty Level</label>
                                        <select class="form-select" name="difficulty" required>
                                            <option value="beginner">Beginner</option>
                                            <option value="intermediate" selected>Intermediate</option>
                                            <option value="advanced">Advanced</option>
                                            <option value="expert">Expert</option>
                                        </select>
                                    </div>

                                    <div class="alert alert-info">
                                        <i class="bi bi-info-circle"></i>
                                        <strong>About the Interview:</strong>
                                        <ul class="mb-0 mt-2">
                                            <li>Adaptive questions based on your resume and target role</li>
                                            <li>Real-time evaluation of your answers</li>
                                            <li>Comprehensive skill gap analysis</li>
                                            <li>Personalized improvement roadmap</li>
                                        </ul>
                                    </div>

                                    <button type="submit" class="btn btn-primary btn-lg w-100">
                                        <i class="bi bi-play-circle"></i> Start Interview
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h6>Interview Tips</h6>
                            </div>
                            <div class="card-body">
                                <ul class="small">
                                    <li>Find a quiet environment</li>
                                    <li>Take your time to think before answering</li>
                                    <li>Be specific and provide examples</li>
                                    <li>Explain your thought process</li>
                                    <li>Ask for clarification if needed</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        showToast('Failed to load interview setup: ' + error.message, 'error');
        navigateTo('resumes');
    }
}

async function createInterview(event, resumeId) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const data = {
        resume_id: resumeId,
        job_role_id: parseInt(form.job_role_id.value),
        difficulty: form.difficulty.value
    };

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating...';

    try {
        const interview = await interviewAPI.create(data);
        showToast('Interview created! Starting...', 'success');

        // Start interview
        setTimeout(async () => {
            try {
                const question = await interviewAPI.start(interview.id);
                currentInterview = {
                    id: interview.id,
                    questionNumber: 1,
                    currentQuestion: question
                };
                showInterviewQuestion();
            } catch (error) {
                showToast('Failed to start interview: ' + error.message, 'error');
                navigateTo('interviews');
            }
        }, 1000);

    } catch (error) {
        showToast('Failed to create interview: ' + error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-play-circle"></i> Start Interview';
    }
}

// Interview Question UI
function showInterviewQuestion() {
    if (!currentInterview) {
        navigateTo('interviews');
        return;
    }

    const question = currentInterview.currentQuestion;
    const content = document.getElementById('mainContent');

    content.innerHTML = `
        <div class="container mt-4">
            <div class="row justify-content-center">
                <div class="col-lg-10">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h3>Interview in Progress</h3>
                        <div>
                            <span class="badge bg-primary">Question ${question.question_number}</span>
                            <button class="btn btn-sm btn-outline-danger ms-2" onclick="finishInterviewEarly()">
                                End Interview
                            </button>
                        </div>
                    </div>

                    <div class="question-card">
                        <div class="mb-3">
                            <span class="badge bg-info">${question.question_type}</span>
                            ${question.skill_being_tested ? `
                                <span class="badge bg-secondary">${question.skill_being_tested}</span>
                            ` : ''}
                            ${question.is_followup ? `
                                <span class="badge bg-warning">Follow-up</span>
                            ` : ''}
                        </div>

                        <h4 class="mb-4">${question.question_text}</h4>

                        <form id="answerForm" onsubmit="submitAnswer(event)">
                            <div class="mb-3">
                                <label class="form-label">Your Answer</label>
                                <textarea
                                    class="form-control answer-input"
                                    name="answer"
                                    rows="8"
                                    placeholder="Type your answer here..."
                                    required
                                ></textarea>
                                <div class="form-text">Be specific and provide examples where possible</div>
                            </div>

                            <div class="d-flex justify-content-between">
                                <button type="button" class="btn btn-outline-secondary" onclick="showInterviewTips()">
                                    <i class="bi bi-lightbulb"></i> Tips
                                </button>
                                <button type="submit" class="btn btn-primary btn-lg">
                                    Submit Answer <i class="bi bi-arrow-right"></i>
                                </button>
                            </div>
                        </form>
                    </div>

                    <div class="alert alert-warning mt-3">
                        <i class="bi bi-info-circle"></i>
                        <strong>Note:</strong> This is an interview preparation assessment, not a hiring decision.
                    </div>
                </div>
            </div>
        </div>
    `;

    // Focus on textarea
    setTimeout(() => {
        document.querySelector('textarea[name="answer"]').focus();
    }, 100);
}

async function submitAnswer(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const answer = form.answer.value.trim();

    if (!answer) {
        showToast('Please provide an answer', 'warning');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Evaluating...';

    try {
        const nextQuestion = await interviewAPI.submitAnswer(currentInterview.id, {
            answer_text: answer
        });

        showToast('Answer submitted!', 'success');

        // Update current interview state
        currentInterview.questionNumber++;
        currentInterview.currentQuestion = nextQuestion;

        // Show next question
        setTimeout(() => {
            showInterviewQuestion();
        }, 500);

    } catch (error) {
        if (error.message.includes('Interview completed')) {
            showToast('Interview completed!', 'success');
            setTimeout(() => {
                finishInterview();
            }, 1000);
        } else {
            showToast('Failed to submit answer: ' + error.message, 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit Answer <i class="bi bi-arrow-right"></i>';
        }
    }
}

async function finishInterviewEarly() {
    if (!confirm('Are you sure you want to end the interview early?')) {
        return;
    }

    try {
        await interviewAPI.finish(currentInterview.id);
        showToast('Interview ended', 'info');
        finishInterview();
    } catch (error) {
        showToast('Error ending interview: ' + error.message, 'error');
    }
}

function finishInterview() {
    const interviewId = currentInterview.id;
    currentInterview = null;
    navigateTo('interview-result', { interviewId });
}

// Interview Result
async function loadInterviewResult(interviewId) {
    const content = document.getElementById('mainContent');
    content.innerHTML = '<div class="container mt-4"><div class="text-center"><div class="spinner-border text-primary"></div><p class="mt-3">Generating your interview report...</p></div></div>';

    try {
        const [report, skillGaps, roadmap] = await Promise.all([
            interviewAPI.getReport(interviewId),
            interviewAPI.getSkillGaps(interviewId),
            interviewAPI.getRoadmap(interviewId)
        ]);

        content.innerHTML = `
            <div class="container mt-4">
                <div class="text-center mb-4">
                    <h2>Interview Report</h2>
                    <div class="display-1 text-primary my-4">
                        ${Math.round(report.readiness_percentage || report.overall_score * 10)}%
                    </div>
                    <h4>Overall Readiness</h4>
                </div>

                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5>Technical</h5>
                                <div class="score-badge badge bg-primary">${(report.technical_score || 0).toFixed(1)}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5>Problem Solving</h5>
                                <div class="score-badge badge bg-info">${(report.problem_solving_score || 0).toFixed(1)}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h5>Communication</h5>
                                <div class="score-badge badge bg-success">${(report.communication_score || 0).toFixed(1)}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header bg-success text-white">
                                <h5 class="mb-0"><i class="bi bi-check-circle"></i> Strengths</h5>
                            </div>
                            <div class="card-body">
                                <ul>
                                    ${(report.strengths || []).map(s => `<li>${s}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header bg-warning text-dark">
                                <h5 class="mb-0"><i class="bi bi-exclamation-triangle"></i> Areas for Improvement</h5>
                            </div>
                            <div class="card-body">
                                <ul>
                                    ${(report.weaknesses || []).map(w => `<li>${w}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Skill Gap Analysis</h5>
                    </div>
                    <div class="card-body">
                        ${skillGaps.filter(g => g.priority === 'high' || g.priority === 'medium').map(gap => `
                            <div class="mb-3 p-3 border-start border-${gap.priority === 'high' ? 'danger' : 'warning'} border-3">
                                <h6>${gap.skill_name}</h6>
                                <div class="small">
                                    ${gap.claimed_level ? `<span class="badge bg-secondary">Claimed: ${gap.claimed_level}</span>` : ''}
                                    ${gap.demonstrated_level ? `<span class="badge bg-info">Demonstrated: ${gap.demonstrated_level}</span>` : ''}
                                    <span class="badge bg-${gap.priority === 'high' ? 'danger' : 'warning'}">${gap.priority} priority</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="bi bi-map"></i> Improvement Roadmap</h5>
                    </div>
                    <div class="card-body">
                        <p class="lead">${roadmap.description || ''}</p>
                        <p><strong>Estimated Duration:</strong> ${roadmap.estimated_duration_days || 0} days</p>

                        <div class="mt-4">
                            ${(roadmap.items || []).slice(0, 5).map(item => `
                                <div class="roadmap-item">
                                    <h6>${item.skill_name} - Day ${item.day_number || 0}</h6>
                                    <p class="mb-2"><strong>Target:</strong> ${item.current_level} → ${item.target_level}</p>
                                    <p class="mb-2"><strong>Focus:</strong></p>
                                    <ul class="small">
                                        ${(item.concepts_to_learn || []).slice(0, 3).map(c => `<li>${c}</li>`).join('')}
                                    </ul>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <div class="alert alert-info">
                    <strong>Disclaimer:</strong> This is an interview readiness assessment and skill gap analysis.
                    It is not a definitive hiring decision. Use this feedback to improve your preparation.
                </div>

                <div class="text-center mb-4">
                    <button class="btn btn-primary btn-lg" onclick="navigateTo('dashboard')">
                        <i class="bi bi-house"></i> Back to Dashboard
                    </button>
                    <button class="btn btn-outline-primary btn-lg ms-2" onclick="navigateTo('upload-resume')">
                        <i class="bi bi-arrow-repeat"></i> Start New Interview
                    </button>
                </div>
            </div>
        `;
    } catch (error) {
        showToast('Failed to load interview results: ' + error.message, 'error');
        content.innerHTML = '<div class="container mt-4"><div class="alert alert-danger">Failed to load interview results</div></div>';
    }
}

// Load Interviews List
async function loadInterviews() {
    const content = document.getElementById('mainContent');
    content.innerHTML = '<div class="container mt-4"><div class="text-center"><div class="spinner-border text-primary"></div></div></div>';

    try {
        const interviews = await interviewAPI.list();

        content.innerHTML = `
            <div class="container mt-4">
                <h2 class="mb-4">My Interviews</h2>

                ${interviews.length > 0 ? `
                    <div class="row">
                        ${interviews.map(interview => `
                            <div class="col-md-6 mb-3">
                                <div class="card interview-card" onclick="navigateTo('interview-result', {interviewId: ${interview.id}})">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <h5>Interview #${interview.id}</h5>
                                            <span class="badge bg-${interview.status === 'completed' ? 'success' : interview.status === 'in_progress' ? 'primary' : 'secondary'}">
                                                ${interview.status}
                                            </span>
                                        </div>
                                        <p class="text-muted mb-1">
                                            <i class="bi bi-calendar"></i> ${new Date(interview.created_at).toLocaleDateString()}
                                        </p>
                                        <p class="text-muted mb-0">
                                            <i class="bi bi-briefcase"></i> ${interview.difficulty}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div class="empty-state">
                        <i class="bi bi-chat-dots"></i>
                        <h4>No interviews yet</h4>
                        <p>Start your first interview to begin your preparation journey</p>
                        <button class="btn btn-primary" onclick="navigateTo('upload-resume')">
                            <i class="bi bi-play-circle"></i> Start Interview
                        </button>
                    </div>
                `}
            </div>
        `;
    } catch (error) {
        showToast('Failed to load interviews: ' + error.message, 'error');
    }
}

// Load History
async function loadHistory() {
    const content = document.getElementById('mainContent');
    content.innerHTML = '<div class="container mt-4"><div class="text-center"><div class="spinner-border text-primary"></div></div></div>';

    try {
        const progress = await dashboardAPI.getProgress();

        content.innerHTML = `
            <div class="container mt-4">
                <h2 class="mb-4">Interview History & Progress</h2>

                ${progress.interview_history.length > 0 ? `
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Interview History</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Role</th>
                                            <th>Score</th>
                                            <th>Readiness</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${progress.interview_history.map(item => `
                                            <tr>
                                                <td>${new Date(item.date).toLocaleDateString()}</td>
                                                <td>${item.role}</td>
                                                <td><span class="badge bg-primary">${(item.score || 0).toFixed(1)}</span></td>
                                                <td><span class="badge bg-info">${Math.round(item.readiness || 0)}%</span></td>
                                                <td>
                                                    <button class="btn btn-sm btn-outline-primary" onclick="navigateTo('interview-result', {interviewId: ${item.interview_id}})">
                                                        View Report
                                                    </button>
                                                </td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    ${progress.score_trend.length > 1 ? `
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Progress Trend</h5>
                            </div>
                            <div class="card-body">
                                <p class="text-muted">Your scores over time show ${progress.score_trend.length} completed interviews</p>
                            </div>
                        </div>
                    ` : ''}
                ` : `
                    <div class="empty-state">
                        <i class="bi bi-clock-history"></i>
                        <h4>No history yet</h4>
                        <p>Complete interviews to track your progress</p>
                    </div>
                `}
            </div>
        `;
    } catch (error) {
        showToast('Failed to load history: ' + error.message, 'error');
    }
}

// Helper functions
async function viewResumeProfile(resumeId) {
    try {
        const profile = await resumeAPI.getProfile(resumeId);
        // Show modal with profile details
        alert(`Profile for ${profile.full_name}\n\nSkills: ${profile.skills.map(s => s.skill_name).join(', ')}\n\nExperience: ${profile.total_experience_years} years`);
    } catch (error) {
        showToast('Failed to load profile: ' + error.message, 'error');
    }
}

async function deleteResume(resumeId) {
    if (!confirm('Are you sure you want to delete this resume?')) return;

    try {
        await resumeAPI.delete(resumeId);
        showToast('Resume deleted', 'success');
        loadResumes();
    } catch (error) {
        showToast('Failed to delete resume: ' + error.message, 'error');
    }
}

function showInterviewTips() {
    alert('Interview Tips:\n\n' +
        '1. Take your time to think before answering\n' +
        '2. Be specific and provide concrete examples\n' +
        '3. Explain your thought process\n' +
        '4. Mention technologies and tools you used\n' +
        '5. Discuss challenges and how you overcame them');
}
