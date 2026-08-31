// Report visualizer logic
function onSessionVerified(user) {
    loadReportCard();
}

async function loadReportCard() {
    try {
        const response = await fetch(`/api/v1/reports/${INTERVIEW_ID}`);
        if (!response.ok) {
            alert("Scorecard is still being generated. Please wait.");
            window.location.href = "/dashboard";
            return;
        }
        
        const data = await response.json();
        
        // Update stats summary
        const formattedDate = new Date(data.created_at).toLocaleDateString();
        document.getElementById("reportDate").textContent = `Completed on: ${formattedDate}`;
        
        document.getElementById("overallScore").textContent = `${data.overall_readiness_score || 0}%`;
        document.getElementById("overallBand").textContent = data.readiness_band || "Developing";
        
        // Categories
        setCategoryScore("Technical", data.technical_score);
        setCategoryScore("Project", data.project_score);
        setCategoryScore("Problem", data.problem_solving_score);
        setCategoryScore("Communication", data.communication_score);
        setCategoryScore("HR", data.hr_score);
        
        // Summaries
        document.getElementById("reportSummary").textContent = data.summary || "No summary notes provided.";
        document.getElementById("reportRecommendation").textContent = data.recommendation || "No overall recommendation provided.";
        
        // Strengths & Weaknesses
        populateBullets("strengthsList", data.strengths_json, "Great communication and logic structure.");
        populateBullets("weaknessesList", data.weaknesses_json, "Review technical documentation details.");
        
        // Skill Gaps Table
        const gapsTable = document.getElementById("reportGapsTableBody");
        if (gapsTable && data.skill_gaps) {
            if (data.skill_gaps.length === 0) {
                gapsTable.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No specific skill gaps recorded.</td></tr>';
            } else {
                gapsTable.innerHTML = '';
                data.skill_gaps.forEach(gap => {
                    let severityClass = gap.gap_severity === "high" ? "badge-high" : gap.gap_severity === "medium" ? "badge-medium" : "badge-low";
                    let priorityClass = gap.priority === "high" ? "badge-solid-red" : gap.priority === "medium" ? "badge-solid-yellow" : "badge-solid-green";
                    gapsTable.innerHTML += `
                        <tr>
                            <td><strong>${gap.skill_name}</strong></td>
                            <td><span class="badge badge-outline-cyan">${gap.category.toUpperCase()}</span></td>
                            <td><span class="badge badge-outline-cyan">${gap.claimed_level}</span></td>
                            <td><span class="badge badge-outline-cyan">${gap.demonstrated_level}</span></td>
                            <td><span class="badge ${severityClass}">${gap.gap_severity.toUpperCase()}</span></td>
                            <td><span class="badge ${priorityClass}">${gap.priority.toUpperCase()}</span></td>
                        </tr>
                    `;
                });
            }
        }
        
        // Roadmap Daily checklist
        const roadmapScroll = document.getElementById("roadmapScrollChecklist");
        if (roadmapScroll && data.roadmap) {
            renderRoadmapList(data.roadmap.items);
        }
        
        // Fetch detailed questions & answers & evaluations
        loadQuestionsReview();
    } catch (err) {
        console.error("Failed to load scorecard data:", err);
    }
}

function renderRoadmapList(items) {
    const roadmapScroll = document.getElementById("roadmapScrollChecklist");
    if (!roadmapScroll) return;
    
    // Calculate roadmap completion percentage
    const completedCount = items.filter(it => it.is_completed).length;
    const totalCount = items.length || 1;
    const percent = Math.round((completedCount / totalCount) * 100);
    document.getElementById("roadmapHeaderPercent").textContent = `${percent}%`;
    
    if (items.length === 0) {
        roadmapScroll.innerHTML = '<div class="text-center text-muted pad-16">No daily tasks populated.</div>';
        return;
    }
    
    roadmapScroll.innerHTML = '';
    items.forEach(item => {
        const checkedClass = item.is_completed ? "checked" : "";
        const completedClass = item.is_completed ? "completed" : "";
        
        // Format concept chips
        let chipsHtml = '';
        if (item.concepts_json) {
            item.concepts_json.forEach(c => {
                chipsHtml += `<span class="chip">${c}</span>`;
            });
        }
        
        // Format practice tasks list
        let tasksHtml = '';
        if (item.practice_tasks_json) {
            tasksHtml = '<ul class="roadmap-subtasks margin-top-8" style="list-style: disc; padding-left: 20px; font-size: 0.75rem; color: var(--text-muted);">';
            item.practice_tasks_json.forEach(t => {
                tasksHtml += `<li class="margin-bottom-4">${t}</li>`;
            });
            tasksHtml += '</ul>';
        }
        
        roadmapScroll.innerHTML += `
            <div class="roadmap-item-row ${completedClass}">
                <div class="day-badge-col">
                    <div class="day-circle">D${item.day_number}</div>
                </div>
                <div class="roadmap-body-col ${completedClass}">
                    <h4 class="font-semibold text-sm">${item.skill_name}</h4>
                    <p class="text-xs text-muted"><strong>Current:</strong> ${item.current_level} &rarr; <strong>Target:</strong> ${item.target_level}</p>
                    <div class="concepts-chips">${chipsHtml}</div>
                    ${tasksHtml}
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

async function toggleRoadmapItem(itemId, element) {
    try {
        const response = await fetch(`/api/v1/reports/roadmap/items/${itemId}/toggle`, {
            method: "PUT"
        });
        if (response.ok) {
            // Reload roadmap checklist only to stay efficient
            const reportResponse = await fetch(`/api/v1/reports/${INTERVIEW_ID}`);
            if (reportResponse.ok) {
                const data = await reportResponse.json();
                if (data.roadmap) {
                    renderRoadmapList(data.roadmap.items);
                }
            }
        }
    } catch (err) {
        console.error("Toggle roadmap item failed:", err);
    }
}

async function loadQuestionsReview() {
    try {
        const response = await fetch(`/api/v1/interviews/${INTERVIEW_ID}`);
        if (!response.ok) return;
        const data = await response.json();
        
        const accordion = document.getElementById("questionsAccordion");
        if (accordion && data.questions) {
            if (data.questions.length === 0) {
                accordion.innerHTML = '<div class="text-center text-muted pad-16">No questions logged in this session.</div>';
                return;
            }
            
            accordion.innerHTML = '';
            
            data.questions.forEach((q, idx) => {
                const hasAnswer = q.answer !== null && q.answer !== undefined;
                const answerText = hasAnswer ? q.answer.answer_text : "No response submitted.";
                const duration = hasAnswer ? `${q.answer.time_taken_seconds} seconds` : "N/A";
                
                const hasEval = hasAnswer && q.answer.evaluation !== null && q.answer.evaluation !== undefined;
                const score = hasEval ? q.answer.evaluation.score : 0.0;
                const feedbackSummary = hasEval ? q.answer.evaluation.feedback_summary : "No evaluation generated.";
                
                // Formulate collapsible card
                accordion.innerHTML += `
                    <div class="accordion-item" id="accItem-${q.id}">
                        <div class="accordion-header" onclick="toggleAccordion(${q.id})">
                            <div class="accordion-header-left">
                                <span class="badge badge-outline-cyan">Q${q.sequence_num}</span>
                                <span class="font-semibold text-sm">${q.question_text.substring(0, 70)}...</span>
                            </div>
                            <div class="flex-row align-center gap-12">
                                <span class="badge ${score >= 7.5 ? 'badge-solid-green' : score >= 5.5 ? 'badge-solid-yellow' : 'badge-solid-red'}">Score: ${score}/10</span>
                                <i class="fa-solid fa-chevron-down toggle-icon" id="accIcon-${q.id}"></i>
                            </div>
                        </div>
                        <div class="accordion-body" id="accBody-${q.id}">
                            <div class="accordion-body-row">
                                <h5>Full AI Question</h5>
                                <p class="text-main font-medium">${q.question_text}</p>
                                <p class="text-xs text-muted margin-top-4">Topic: ${q.target_skill} | Category: ${q.category} | Difficulty: ${q.difficulty}</p>
                            </div>
                            <hr class="margin-y-12" style="border-top: 1px solid var(--border-color);">
                            <div class="accordion-body-row">
                                <h5>Your Answer (${duration})</h5>
                                <p class="text-main italic" style="white-space: pre-wrap;">"${answerText}"</p>
                            </div>
                            <hr class="margin-y-12" style="border-top: 1px solid var(--border-color);">
                            <div class="accordion-body-row">
                                <h5>AI Evaluation Feedback</h5>
                                <p class="text-violet leading-relaxed">${feedbackSummary}</p>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
    } catch (err) {
        console.error("Failed to load questions review list:", err);
    }
}

function toggleAccordion(id) {
    const item = document.getElementById(`accItem-${id}`);
    const body = document.getElementById(`accBody-${id}`);
    const icon = document.getElementById(`accIcon-${id}`);
    
    if (item.classList.contains("open")) {
        item.classList.remove("open");
        body.style.display = "none";
        icon.className = "fa-solid fa-chevron-down toggle-icon";
    } else {
        item.classList.add("open");
        body.style.display = "block";
        icon.className = "fa-solid fa-chevron-up toggle-icon";
    }
}

function setCategoryScore(categoryName, scoreVal) {
    const scoreEl = document.getElementById(`score${categoryName}`);
    const barEl = document.getElementById(`bar${categoryName}`);
    if (scoreEl) scoreEl.textContent = `${scoreVal || 0}%`;
    if (barEl) barEl.style.width = `${scoreVal || 0}%`;
}

function populateBullets(elementId, itemsList, fallbackText) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    if (!itemsList || itemsList.length === 0) {
        el.innerHTML = `<li>${fallbackText}</li>`;
        return;
    }
    
    el.innerHTML = '';
    itemsList.forEach(item => {
        el.innerHTML += `<li>${item}</li>`;
    });
}
