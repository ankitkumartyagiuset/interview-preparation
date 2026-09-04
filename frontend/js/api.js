// API Configuration
const configuredApiUrl = window.APP_CONFIG?.API_BASE_URL || window.location.origin;
const API_BASE_URL = `${configuredApiUrl.replace(/\/$/, '')}/api`;

// API Client
class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/';
                throw new Error('Unauthorized');
            }

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                throw new Error(data?.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    async uploadFile(endpoint, file) {
        const formData = new FormData();
        formData.append('file', file);

        const headers = {};
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers,
            body: formData
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data?.detail || 'Upload failed');
        }

        return response.json();
    }
}

const api = new APIClient();

// Auth API
const authAPI = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    logout: () => api.post('/auth/logout'),
    getCurrentUser: () => api.get('/auth/me')
};

// Resume API
const resumeAPI = {
    upload: (file) => api.uploadFile('/resumes', file),
    list: () => api.get('/resumes'),
    get: (id) => api.get(`/resumes/${id}`),
    getProfile: (id) => api.get(`/resumes/${id}/profile`),
    updateProfile: (id, data) => api.patch(`/resumes/${id}/profile`, data),
    delete: (id) => api.delete(`/resumes/${id}`)
};

// Job API
const jobAPI = {
    getRoles: () => api.get('/jobs/roles'),
    getRole: (id) => api.get(`/jobs/roles/${id}`),
    createJobDescription: (data) => api.post('/jobs/descriptions', data),
    listJobDescriptions: () => api.get('/jobs/descriptions'),
    getJobDescription: (id) => api.get(`/jobs/descriptions/${id}`)
};

// Interview API
const interviewAPI = {
    create: (data) => api.post('/interviews', data),
    list: () => api.get('/interviews'),
    get: (id) => api.get(`/interviews/${id}`),
    start: (id) => api.post(`/interviews/${id}/start`, {}),
    submitAnswer: (id, data) => api.post(`/interviews/${id}/answer`, data),
    finish: (id) => api.post(`/interviews/${id}/finish`, {}),
    getReport: (id) => api.get(`/interviews/${id}/report`),
    getSkillGaps: (id) => api.get(`/interviews/${id}/skill-gaps`),
    getRoadmap: (id) => api.get(`/interviews/${id}/roadmap`)
};

// Dashboard API
const dashboardAPI = {
    get: () => api.get('/dashboard'),
    getProgress: () => api.get('/progress'),
    getHistory: () => api.get('/history')
};
