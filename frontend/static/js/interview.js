// Mock Interview screen controller
let currentQuestion = null;
let currentQuestionIndex = 0;
let totalQuestions = 5;
let timerInterval = null;
let secondsElapsed = 0;

function onSessionVerified(user) {
    // Initial fetch of interview metadata
    loadInterviewDetails();
}

async function loadInterviewDetails() {
    try {
        const response = await fetch(`/api/v1/interviews/${INTERVIEW_ID}`);
        if (!response.ok) return;
        const data = await response.json();
        
        document.getElementById("interviewTitle").textContent = data.title;
        document.getElementById("interviewDifficulty").textContent = data.difficulty.toUpperCase();
        totalQuestions = data.total_questions;
        
        // Render empty checklist steps
        renderSidebarSteps(data.current_question_index || 0, data.status);
        
        if (data.status === "completed") {
            window.location.href = `/report/${INTERVIEW_ID}`;
        } else if (data.status === "in_progress" && data.questions.length > 0) {
            // Already started, render messages and resume
            document.getElementById("startCover").style.display = "none";
            document.getElementById("chatInputArea").style.display = "block";
            
            const chatViewport = document.getElementById("chatViewport");
            chatViewport.innerHTML = '';
            
            data.questions.forEach((q, idx) => {
                // Render question
                appendChatMessage("ai", q.question_text);
                
                // If answered, render answer
                // Fetch details or iterate
            });
            
            // To make things easy, we start or fetch the active question
            resumeInterviewFlow();
        }
    } catch (err) {
        console.error("Failed to load interview details:", err);
    }
}

function renderSidebarSteps(activeIndex, status) {
    const list = document.getElementById("progressStepsList");
    list.innerHTML = '';
    
    for (let i = 1; i <= totalQuestions; i++) {
        let stateClass = '';
        let iconHtml = i;
        
        if (i < activeIndex || status === 'completed') {
            stateClass = 'completed';
            iconHtml = '<i class="fa-solid fa-check"></i>';
        } else if (i === activeIndex && status === 'in_progress') {
            stateClass = 'active';
        }
        
        list.innerHTML += `
            <div class="progress-step ${stateClass}">
                <div class="step-marker">${iconHtml}</div>
                <span>Question ${i}</span>
            </div>
        `;
    }
}

async function beginInterview() {
    document.getElementById("startCover").style.display = "none";
    document.getElementById("chatLoaderPanel").style.display = "block";
    document.getElementById("loaderText").textContent = "Iris is planning your customized interview...";
    
    try {
        const response = await fetch(`/api/v1/interviews/${INTERVIEW_ID}/start`, { method: "POST" });
        if (!response.ok) throw new Error("Could not start interview.");
        
        const data = await response.json();
        
        document.getElementById("chatLoaderPanel").style.display = "none";
        document.getElementById("chatInputArea").style.display = "block";
        
        // Show first question
        currentQuestion = data.first_question;
        currentQuestionIndex = 1;
        
        // Clear chat viewport and render
        const chatViewport = document.getElementById("chatViewport");
        chatViewport.innerHTML = '';
        appendChatMessage("ai", currentQuestion.question_text);
        
        renderSidebarSteps(1, "in_progress");
        startTimer();
    } catch (err) {
        alert(err.message);
        window.location.href = "/dashboard";
    }
}

async function resumeInterviewFlow() {
    // If resuming, start interview gets current active state safely
    try {
        const response = await fetch(`/api/v1/interviews/${INTERVIEW_ID}/start`, { method: "POST" });
        if (response.ok) {
            const data = await response.json();
            currentQuestion = data.first_question;
            
            // Render the last question
            const chatViewport = document.getElementById("chatViewport");
            chatViewport.innerHTML = '';
            appendChatMessage("ai", currentQuestion.question_text);
            
            currentQuestionIndex = data.first_question.sequence_num;
            renderSidebarSteps(currentQuestionIndex, "in_progress");
            startTimer();
        }
    } catch (err) {
        console.error(err);
    }
}

function appendChatMessage(sender, text) {
    const chatViewport = document.getElementById("chatViewport");
    const avatar = sender === 'ai' ? '/static/img/ai_avatar.jpg' : '/static/img/ai_avatar.jpg'; // just visual placeholders
    const bubbleClass = sender === 'ai' ? 'ai' : 'candidate';
    
    const msg = document.createElement("div");
    msg.className = `chat-message ${bubbleClass}`;
    
    if (sender === 'ai') {
        msg.innerHTML = `
            <div class="avatar-col">
                <img src="${avatar}" alt="Iris" class="ai-avatar-small">
            </div>
            <div class="message-bubble-col">
                <div class="bubble">${text}</div>
            </div>
        `;
    } else {
        msg.innerHTML = `
            <div class="message-bubble-col">
                <div class="bubble">${text}</div>
            </div>
        `;
    }
    
    chatViewport.appendChild(msg);
    chatViewport.scrollTop = chatViewport.scrollHeight;
}

function startTimer() {
    clearInterval(timerInterval);
    secondsElapsed = 0;
    const timerDisplay = document.getElementById("interviewStopwatch");
    
    timerInterval = setInterval(() => {
        secondsElapsed++;
        let minutes = Math.floor(secondsElapsed / 60);
        let seconds = secondsElapsed % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function onAnswerInput() {
    const textarea = document.getElementById("answerTextarea");
    const countText = document.getElementById("wordCountText");
    const text = textarea.value.trim();
    const wordCount = text === '' ? 0 : text.split(/\s+/).length;
    countText.textContent = `Words: ${wordCount} (Min recommended: 20)`;
}

async function submitAnswer(e) {
    e.preventDefault();
    const textarea = document.getElementById("answerTextarea");
    const answer = textarea.value.trim();
    
    const wordCount = answer === '' ? 0 : answer.split(/\s+/).length;
    if (wordCount < 5) {
        alert("Please write a slightly more detailed response before submitting.");
        return;
    }
    
    // Stop Timer
    clearInterval(timerInterval);
    
    // Hide inputs, show loader
    document.getElementById("chatInputArea").style.display = "none";
    document.getElementById("chatLoaderPanel").style.display = "block";
    document.getElementById("loaderText").textContent = "Iris is analyzing your response and planning the next question...";
    
    // Render candidate message in chat
    appendChatMessage("candidate", answer);
    
    try {
        const response = await fetch(`/api/v1/interviews/${INTERVIEW_ID}/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_id: currentQuestion.id,
                answer_text: answer,
                time_taken_seconds: secondsElapsed
            })
        });
        
        if (!response.ok) throw new Error("Failed to submit answer.");
        
        const data = await response.json();
        textarea.value = '';
        document.getElementById("wordCountText").textContent = "Words: 0 (Min recommended: 20)";
        
        if (data.is_finished) {
            document.getElementById("loaderText").textContent = "Interview completed! Preparing your final evaluation report...";
            setTimeout(() => {
                window.location.href = `/report/${INTERVIEW_ID}`;
            }, 2000);
        } else {
            // Load next question
            currentQuestion = data.next_question;
            currentQuestionIndex = data.current_question_index;
            
            // Hide loader, show inputs
            document.getElementById("chatLoaderPanel").style.display = "none";
            document.getElementById("chatInputArea").style.display = "block";
            
            // Render next question
            appendChatMessage("ai", currentQuestion.question_text);
            
            renderSidebarSteps(currentQuestionIndex, "in_progress");
            startTimer();
        }
    } catch (err) {
        alert(err.message);
        // Fallback to restore inputs
        document.getElementById("chatLoaderPanel").style.display = "none";
        document.getElementById("chatInputArea").style.display = "block";
        startTimer();
    }
}

function confirmAbandon() {
    if (confirm("Are you sure you want to quit? Your progress in this session will not be graded.")) {
        window.location.href = "/dashboard";
    }
}
