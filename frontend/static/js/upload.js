// Resume uploading and claims editing flow
let tempSkillsList = [];
let tempProjectsList = [];

// Drag and drop events setup
const dropZone = document.getElementById("dropZone");
if (dropZone) {
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', e => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }, false);
}

function triggerFileInput() {
    document.getElementById("resumeFileInput").click();
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

async function uploadFile(file) {
    const progressContainer = document.getElementById("uploadProgress");
    const dropContainer = document.getElementById("dropZone");
    const progressBar = document.getElementById("uploadProgressBar");
    const uploadPercent = document.getElementById("uploadPercent");
    const uploadFileName = document.getElementById("uploadFileName");
    const uploadStatusText = document.getElementById("uploadStatusText");
    
    if (dropContainer) dropContainer.style.display = "none";
    if (progressContainer) progressContainer.style.display = "block";
    if (uploadFileName) uploadFileName.textContent = file.name;
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
        uploadStatusText.textContent = "Uploading resume file to server...";
        
        // Simple progress simulation or standard request
        progressBar.style.width = "40%";
        if (uploadPercent) uploadPercent.textContent = "40%";
        
        const response = await fetch("/api/v1/resumes/upload", {
            method: "POST",
            body: formData
        });
        
        progressBar.style.width = "75%";
        if (uploadPercent) uploadPercent.textContent = "75%";
        uploadStatusText.textContent = "AI model is parsing skills and achievements...";
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Failed to process resume.");
        }
        
        progressBar.style.width = "100%";
        if (uploadPercent) uploadPercent.textContent = "100%";
        
        // Load Parsed results into editor
        loadParsedData(data);
    } catch (err) {
        alert("Upload error: " + err.message);
        resetUpload();
    }
}

function resetUpload() {
    const progressContainer = document.getElementById("uploadProgress");
    const dropContainer = document.getElementById("dropZone");
    const resultSection = document.getElementById("parsedResultSection");
    
    if (dropContainer) dropContainer.style.display = "block";
    if (progressContainer) progressContainer.style.display = "none";
    if (resultSection) resultSection.style.display = "none";
    
    document.getElementById("resumeFileInput").value = '';
    tempSkillsList = [];
    tempProjectsList = [];
}

function loadParsedData(data) {
    document.getElementById("uploadProgress").style.display = "none";
    document.getElementById("parsedResultSection").style.display = "block";
    
    document.getElementById("parsedResumeId").value = data.id;
    
    const profile = data.candidate_profile || {};
    document.getElementById("profileName").value = profile.full_name || "";
    document.getElementById("profilePhone").value = profile.phone || "";
    document.getElementById("profileHeadline").value = profile.headline || "";
    document.getElementById("profileSummary").value = profile.summary || "";
    
    // Parse skills and projects
    tempSkillsList = profile.skills || [];
    tempProjectsList = profile.projects || [];
    
    renderSkillsClaims();
    renderProjectsList();
}

function renderSkillsClaims() {
    const list = document.getElementById("skillsClaimsList");
    list.innerHTML = '';
    
    tempSkillsList.forEach((skill, index) => {
        list.innerHTML += `
            <div class="skill-claim-row" data-index="${index}">
                <input type="text" class="form-control skill-name-input" value="${skill.skill_name || ''}" placeholder="Skill Name" onchange="updateSkillItem(${index}, 'skill_name', this.value)">
                
                <input type="text" class="form-control skill-category-input" value="${skill.category || 'technical'}" placeholder="Category" onchange="updateSkillItem(${index}, 'category', this.value)">
                
                <select class="form-control skill-level-select" onchange="updateSkillItem(${index}, 'claimed_level', this.value)">
                    <option value="beginner" ${skill.claimed_level === 'beginner' ? 'selected' : ''}>Beginner</option>
                    <option value="intermediate" ${skill.claimed_level === 'intermediate' ? 'selected' : ''}>Intermediate</option>
                    <option value="advanced" ${skill.claimed_level === 'advanced' ? 'selected' : ''}>Advanced</option>
                    <option value="expert" ${skill.claimed_level === 'expert' ? 'selected' : ''}>Expert</option>
                </select>
                
                <input type="text" class="form-control skill-exp-input" value="${skill.years_of_exp !== undefined ? skill.years_of_exp : '2'}" placeholder="Exp Years" onchange="updateSkillItem(${index}, 'years_of_exp', this.value)">
                
                <button class="btn-delete-row" onclick="deleteSkillRow(${index})" type="button">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
        `;
    });
}

function updateSkillItem(index, field, value) {
    if (field === 'years_of_exp') {
        tempSkillsList[index][field] = parseFloat(value) || 0.0;
    } else {
        tempSkillsList[index][field] = value;
    }
}

function addNewSkillClaimRow() {
    tempSkillsList.push({
        skill_name: "",
        category: "technical",
        claimed_level: "intermediate",
        years_of_exp: 2.0
    });
    renderSkillsClaims();
}

function deleteSkillRow(index) {
    tempSkillsList.splice(index, 1);
    renderSkillsClaims();
}

function renderProjectsList() {
    const container = document.getElementById("projectsList");
    container.innerHTML = '';
    
    tempProjectsList.forEach((proj, index) => {
        container.innerHTML += `
            <div class="project-claim-item" data-index="${index}">
                <button class="btn-delete-row project-delete-btn" onclick="deleteProjectItem(${index})" type="button">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
                <div class="form-row">
                    <div class="form-group flex-1">
                        <label>Project Title</label>
                        <input type="text" class="form-control" value="${proj.title || ''}" onchange="updateProjectItem(${index}, 'title', this.value)">
                    </div>
                </div>
                <div class="form-row margin-top-8">
                    <div class="form-group flex-1">
                        <label>Project Description & Technologies</label>
                        <textarea class="form-control" rows="2" onchange="updateProjectItem(${index}, 'description', this.value)">${proj.description || ''}</textarea>
                    </div>
                </div>
            </div>
        `;
    });
}

function updateProjectItem(index, field, value) {
    tempProjectsList[index][field] = value;
}

function addNewProjectRow() {
    tempProjectsList.push({
        title: "New Project",
        description: ""
    });
    renderProjectsList();
}

function deleteProjectItem(index) {
    tempProjectsList.splice(index, 1);
    renderProjectsList();
}

async function saveParsedProfile() {
    const resumeId = document.getElementById("parsedResumeId").value;
    const fullName = document.getElementById("profileName").value;
    const phone = document.getElementById("profilePhone").value;
    const headline = document.getElementById("profileHeadline").value;
    const summary = document.getElementById("profileSummary").value;
    
    // Construct payload
    const payload = {
        full_name: fullName,
        phone: phone,
        headline: headline,
        summary: summary,
        skills: tempSkillsList.filter(s => s.skill_name.trim() !== ""),
        projects: tempProjectsList.filter(p => p.title.trim() !== "")
    };
    
    try {
        const response = await fetch(`/api/v1/resumes/${resumeId}/profile`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error("Failed to save profile changes.");
        }
        
        // Redirect to dashboard
        window.location.href = "/dashboard";
    } catch (err) {
        alert(err.message);
    }
}
