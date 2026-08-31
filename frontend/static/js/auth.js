// Auth state management and dropdown helpers
document.addEventListener("DOMContentLoaded", function() {
    // Authenticate current session by fetching user metadata
    checkSession();
});

async function checkSession() {
    try {
        const response = await fetch("/api/v1/auth/me");
        if (!response.ok) {
            // Redirect to login if user is not authenticated and is on a protected page
            const path = window.location.pathname;
            if (path !== "/login" && path !== "/register" && path !== "/") {
                window.location.href = "/login";
            }
            return;
        }
        
        const data = await response.json();
        
        // Update user profile display in header
        const displayUsername = document.getElementById("displayUsername");
        const displayEmail = document.getElementById("displayEmail");
        const displayRole = document.getElementById("displayRole");
        
        if (displayUsername) displayUsername.textContent = data.full_name || "Candidate";
        if (displayEmail) displayEmail.textContent = data.email;
        if (displayRole) {
            displayRole.textContent = data.role === "admin" ? "Administrator" : "Candidate";
            displayRole.className = `role-badge ${data.role === 'admin' ? 'admin' : ''}`;
        }
        
        // Custom hooks for individual pages
        if (typeof onSessionVerified === "function") {
            onSessionVerified(data);
        }
    } catch (err) {
        console.error("Session check failed:", err);
    }
}

async function handleLogout(e) {
    if (e) e.preventDefault();
    try {
        const response = await fetch("/api/v1/auth/logout", { method: "POST" });
        if (response.ok) {
            window.location.href = "/login";
        }
    } catch (err) {
        console.error("Logout failed:", err);
    }
}
