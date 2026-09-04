// Dashboard visualizer logic
function onSessionVerified(user) {
    const dashboardUser = document.getElementById("dashboardUser");
    if (dashboardUser) dashboardUser.textContent = user.full_name;
    
    // Fetch stats and lists
    loadDashboardStats();
    loadResumes();
    loadJobRoles();
}

async function loadDashboardStats() {
    try {
        const response = await fetch("/api/v1/dashboard/stats");
        if (!response.ok) return;
        
        const data = await response.json();
        
        // Update stats metrics
        updateElementText("readinessScore", `${data.overall_readiness || 0}%`);
        updateElementText("readinessBand", data.readiness_band || "Not Started");
        
        const progress = document.getElementById("readinessProgress");
        if (progress) progress.style.width = `${data.overall_readiness || 0}%`;
        
        updateElementText("totalInterviews", data.total_interviews || 0);
        updateElementText("completedInterviews", data.completed_interviews || 0);
        updateElementText("skillGapsCount", data.priority_gaps ? data.priority_gaps.length : 0);
        
        // Update Active Roadmap Checklist
        const checklist = document.getElementById("roadmapChecklist");
        const rTitle = document.getElementById("roadmapTitle");
        const rFooter = document.getElementById("roadmapFooter");
        
        if (data.active_roadmap) {
            updateElementText("roadmapProgress", `${data.active_roadmap.progress_percent || 0}%`);
            if (rTitle) rTitle.textContent = data.active_roadmap.title;
            if (rFooter) {
                rFooter.style.display = "block";
                document.getElementById("roadmapFooterText").textContent = `${data.active_roadmap.completed_days} of ${data.active_roadmap.duration_days} items completed`;
                document.getElementById("roadmapReportLink").href = `/report/${data.active_roadmap.id}`; // actually matches interview_id inside active_roadmap structure from dashboard service
            }
            
            checklist.innerHTML = '';
            data.active_roadmap.items.forEach(item => {
                const checkedClass = item.is_completed ? "checked" : "";
                const completedClass = item.is_completed ? "completed" : "";
                checklist.innerHTML += `
                    <div class="roadmap-item-row ${completedClass}">
                        <div class="day-badge-col">
                            <div class="day-circle">D${item.day_number}</div>
                        </div>
                        <div class="roadmap-body-col ${completedClass}">
                            <h4>${item.skill_name}</h4>
                            <p>Targeting development to required proficiency level.</p>
                        </div>
                        <div class="roadmap-checkbox-col">
                            <div class="custom-checkbox ${checkedClass}" onclick="toggleRoadmapItem(${item.id}, this)">
                                <i class="fa-solid fa-check"></i>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        // Populate Gaps Table
        const gapsTable = document.getElementById("skillGapsTableBody");
        if (gapsTable) {
            if (data.priority_gaps && data.priority_gaps.length > 0) {
                gapsTable.innerHTML = '';
                data.priority_gaps.forEach(gap => {
                    let severityClass = gap.gap_severity === "high" ? "badge-high" : gap.gap_severity === "medium" ? "badge-medium" : "badge-low";
                    let priorityClass = gap.priority === "high" ? "badge-solid-red" : gap.priority === "medium" ? "badge-solid-yellow" : "badge-solid-green";
                    gapsTable.innerHTML += `
                        <tr>
                            <td><strong>${gap.skill_name}</strong></td>
                            <td><span class="badge badge-outline-cyan">${gap.claimed_level}</span></td>
                            <td><span class="badge badge-outline-cyan">${gap.demonstrated_level}</span></td>
                            <td><span class="badge ${severityClass}">${gap.gap_severity.toUpperCase()}</span></td>
                            <td><span class="badge ${priorityClass}">${gap.priority.toUpperCase()}</span></td>
                        </tr>
                    `;
                });
            }
        }
        
        // Populate Recent Interviews
        const recentContainer = document.getElementById("recentInterviewsContainer");
        if (recentContainer) {
            if (data.recent_interviews && data.recent_interviews.length > 0) {
                recentContainer.innerHTML = '';
                data.recent_interviews.forEach(intv => {
                    let actionBtn = '';
                    if (intv.status === 'completed') {
                        actionBtn = `<a href="/report/${intv.id}" class="btn btn-xs btn-outline-cyan">View Report <i class="fa-solid fa-square-poll-vertical"></i></a>`;
                    } else {
                        actionBtn = `<a href="/interview/${intv.id}" class="btn btn-xs btn-primary">Resume <i class="fa-solid fa-play"></i></a>`;
                    }
                    recentContainer.innerHTML += `
                        <div class="resume-row-item">
                            <div>
                                <h4 class="font-semibold text-sm">${intv.title}</h4>
                                <p class="text-xs text-muted">Created: ${intv.created_at} | Difficulty: ${intv.difficulty}</p>
                            </div>
                            <div>
                                ${actionBtn}
                            </div>
                        </div>
                    `;
                });
            }
        }
        
    } catch (err) {
        console.error("Failed to load dashboard stats:", err);
    }
}

async function loadResumes() {
    try {
        const response = await fetch("/api/v1/resumes");
        if (!response.ok) return;
        const resumes = await response.json();
        
        const dropdown = document.getElementById("selectResume");
        const listContainer = document.getElementById("resumesListContainer");
        
        if (dropdown) {
            dropdown.innerHTML = '<option value="">-- Choose Uploaded Resume --</option>';
            resumes.forEach(r => {
                dropdown.innerHTML += `<option value="${r.id}">${r.filename} (${r.parsed_status})</option>`;
            });
        }
        
        if (listContainer) {
            if (resumes.length === 0) {
                listContainer.innerHTML = '<div class="text-center text-muted pad-16">No resumes uploaded. Click Upload New to get started.</div>';
            } else {
                listContainer.innerHTML = '';
                resumes.forEach(r => {
                    const formattedDate = new Date(r.uploaded_at).toLocaleDateString();
                    listContainer.innerHTML += `
                        <div class="resume-row-item">
                            <div class="resume-meta-info">
                                <div class="resume-icon"><i class="fa-regular fa-file-pdf"></i></div>
                                <div>
                                    <div class="resume-title">${r.filename}</div>
                                    <div class="resume-date">Uploaded on ${formattedDate} | Status: ${r.parsed_status}</div>
                                </div>
                            </div>
                            <div>
                                <button class="btn btn-xs btn-outline-danger" onclick="deleteResume(${r.id})">
                                    <i class="fa-solid fa-trash-can"></i>
                                </button>
                            </div>
                        </div>
                    `;
                });
            }
        }
    } catch (err) {
        console.error("Failed to load resumes:", err);
    }
}

async function deleteResume(id) {
    if (!confirm("Are you sure you want to delete this resume?")) return;
    try {
        const response = await fetch(`/api/v1/resumes/${id}`, { method: "DELETE" });
        if (response.ok) {
            loadResumes();
            loadDashboardStats();
        }
    } catch (err) {
        console.error("Delete resume failed:", err);
    }
}

async function loadJobRoles() {
    try {
        const response = await fetch("/api/v1/jobs/roles");
        if (!response.ok) return;
        const roles = await response.json();
        
        const dropdown = document.getElementById("selectJobRole");
        if (dropdown) {
            dropdown.innerHTML = '<option value="">-- Choose Job Role --</option>';
            roles.forEach(r => {
                dropdown.innerHTML += `<option value="${r.id}">${r.title} (${r.department})</option>`;
            });
        }
    } catch (err) {
        console.error("Failed to load job roles:", err);
    }
}

async function toggleRoadmapItem(itemId, element) {
    try {
        const response = await fetch(`/api/v1/reports/roadmap/items/${itemId}/toggle`, {
            method: "PUT"
        });
        if (response.ok) {
            const data = await response.json();
            const row = element.closest(".roadmap-item-row");
            const body = row.querySelector(".roadmap-body-col");
            
            if (data.is_completed) {
                element.classList.add("checked");
                row.classList.add("completed");
                if (body) body.classList.add("completed");
            } else {
                element.classList.remove("checked");
                row.classList.remove("completed");
                if (body) body.classList.remove("completed");
            }
            // Reload dashboard stats to update progress counters
            loadDashboardStats();
        }
    } catch (err) {
        console.error("Toggle roadmap item failed:", err);
    }
}

async function launchCustomInterview() {
    const resumeId = document.getElementById("selectResume").value;
    const jobRoleId = document.getElementById("selectJobRole").value;
    const difficulty = document.getElementById("selectDifficulty").value;
    const totalQuestions = document.getElementById("selectQuestions").value;
    
    if (!resumeId || !jobRoleId) {
        alert("Please select both a resume and target job role before launching.");
        return;
    }
    
    try {
        const response = await fetch("/api/v1/interviews", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                resume_id: parseInt(resumeId),
                job_role_id: parseInt(jobRoleId),
                difficulty: difficulty,
                total_questions: parseInt(totalQuestions),
                interview_type: "mixed"
            })
        });
        
        if (!response.ok) {
            throw new Error("Failed to create interview session.");
        }
        
        const data = await response.json();
        // Redirect to interview screen
        window.location.href = `/interview/${data.id}`;
    } catch (err) {
        alert(err.message);
    }
}

function updateElementText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}
