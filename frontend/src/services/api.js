/**
 * API Service for Playto Community Feed
 * 
 * Handles all HTTP requests to the Django backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true, // Important for session authentication
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add CSRF token to requests
api.interceptors.request.use((config) => {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
});

// Helper function to get cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Auth API
export const authAPI = {
    register: (userData) => api.post('/auth/register/', userData),
    login: (credentials) => api.post('/auth/login/', credentials),
    logout: () => api.post('/auth/logout/'),
    getCurrentUser: () => api.get('/auth/me/'),
};

// Posts API
export const postsAPI = {
    getAll: (page = 1) => api.get(`/posts/?page=${page}`),
    getById: (id) => api.get(`/posts/${id}/`),
    create: (postData) => api.post('/posts/', postData),
    update: (id, postData) => api.put(`/posts/${id}/`, postData),
    delete: (id) => api.delete(`/posts/${id}/`),
    like: (id) => api.post(`/posts/${id}/like/`),
};

// Comments API
export const commentsAPI = {
    create: (commentData) => api.post('/comments/', commentData),
    update: (id, commentData) => api.put(`/comments/${id}/`, commentData),
    delete: (id) => api.delete(`/comments/${id}/`),
    like: (id) => api.post(`/comments/${id}/like/`),
};

// Leaderboard API
export const leaderboardAPI = {
    get: () => api.get('/leaderboard/'),
};

export default api;
