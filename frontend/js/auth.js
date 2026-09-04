// Authentication functions
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        showLoginPage();
        return false;
    }
    return true;
}

function showLoginPage() {
    document.getElementById('mainNav').style.display = 'none';
    document.getElementById('mainContent').innerHTML = `
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow">
                        <div class="card-body p-5">
                            <h2 class="text-center mb-4">
                                <i class="bi bi-mortarboard-fill text-primary"></i>
                                Interview Platform
                            </h2>

                            <ul class="nav nav-pills nav-fill mb-4" id="authTabs" role="tablist">
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active" id="login-tab" data-bs-toggle="pill" data-bs-target="#login" type="button" role="tab">Login</button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="register-tab" data-bs-toggle="pill" data-bs-target="#register" type="button" role="tab">Register</button>
                                </li>
                            </ul>

                            <div class="tab-content" id="authTabContent">
                                <!-- Login Form -->
                                <div class="tab-pane fade show active" id="login" role="tabpanel">
                                    <form id="loginForm" onsubmit="handleLogin(event)">
                                        <div class="mb-3">
                                            <label class="form-label">Email</label>
                                            <input type="email" class="form-control" name="email" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Password</label>
                                            <input type="password" class="form-control" name="password" required>
                                        </div>
                                        <button type="submit" class="btn btn-primary w-100">
                                            Login
                                        </button>
                                    </form>
                                </div>

                                <!-- Register Form -->
                                <div class="tab-pane fade" id="register" role="tabpanel">
                                    <form id="registerForm" onsubmit="handleRegister(event)">
                                        <div class="mb-3">
                                            <label class="form-label">Full Name</label>
                                            <input type="text" class="form-control" name="full_name" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Email</label>
                                            <input type="email" class="form-control" name="email" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Password</label>
                                            <input type="password" class="form-control" name="password" minlength="8" required>
                                            <div class="form-text">Minimum 8 characters</div>
                                        </div>
                                        <button type="submit" class="btn btn-primary w-100">
                                            Register
                                        </button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="text-center mt-4 text-muted">
                        <p>AI-powered interview preparation and skill gap analysis platform</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const data = {
        email: form.email.value,
        password: form.password.value
    };

    submitBtn.disabled = true;
    submitBtn.classList.add('btn-loading');

    try {
        const response = await authAPI.login(data);
        api.setToken(response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        showToast('Login successful!', 'success');
        initApp();
    } catch (error) {
        showToast(error.message || 'Login failed', 'error');
        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-loading');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const data = {
        full_name: form.full_name.value,
        email: form.email.value,
        password: form.password.value
    };

    submitBtn.disabled = true;
    submitBtn.classList.add('btn-loading');

    try {
        const response = await authAPI.register(data);
        api.setToken(response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        showToast('Registration successful!', 'success');
        initApp();
    } catch (error) {
        showToast(error.message || 'Registration failed', 'error');
        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-loading');
    }
}

async function logout() {
    try {
        await authAPI.logout();
    } catch (error) {
        console.error('Logout error:', error);
    }

    api.clearToken();
    localStorage.removeItem('user');
    showToast('Logged out successfully', 'info');
    showLoginPage();
}
