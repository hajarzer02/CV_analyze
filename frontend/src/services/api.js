import axios from 'axios';

// Use relative URLs by default for both local and ngrok access
// Only use absolute URL if explicitly set via environment variable
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Upload CV
export const uploadCV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/upload-cv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Get candidate by ID
export const getCandidate = async (id) => {
  const response = await api.get(`/api/candidate/${id}`);
  return response.data;
};

// Get all candidates
export const getCandidates = async () => {
  const response = await api.get('/api/candidates');
  return response.data;
};

// Generate recommendations for candidate
export const generateRecommendations = async (id) => {
  const response = await api.post(`/api/recommend/${id}`);
  return response.data;
};

// Delete candidate
export const deleteCandidate = async (id) => {
  const response = await api.delete(`/api/candidates/${id}`);
  return response.data;
};

// Update candidate status
export const updateCandidateStatus = async (id, status) => {
  const response = await api.patch(`/api/candidate/${id}/status`, { status });
  return response.data;
};

// Match job against candidates
export const matchJob = async (jobDescription) => {
  const response = await api.post('/api/match-job', { job_description: jobDescription });
  return response.data;
};

// Authentication functions
export const login = async (email, password, rememberMe = false) => {
  const response = await api.post('/auth/login', {
    email,
    password,
    remember_me: rememberMe
  });
  return response.data;
};

export const register = async (name, email, password) => {
  const response = await api.post('/auth/register', {
    name,
    email,
    password
  });
  return response.data;
};

export const logout = async () => {
  try {
    await api.post('/auth/logout');
  } catch (error) {
    // Even if logout fails on server, clear local storage
    console.warn('Logout request failed:', error);
  } finally {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Profile APIs
export const getProfile = async () => {
  const response = await api.get('/api/profile');
  return response.data;
};

export const updateProfile = async (data) => {
  const response = await api.put('/api/profile', data);
  return response.data;
};

export const changeMyPassword = async (currentPassword, newPassword) => {
  const response = await api.post('/api/profile/password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return response.data;
};

// Admin API functions
export const adminApi = {
  // Get all users
  getUsers: async () => {
    const response = await api.get('/api/admin/users');
    return response;
  },

  // Get user by ID
  getUser: async (id) => {
    const response = await api.get(`/api/admin/users/${id}`);
    return response;
  },

  // Update user
  updateUser: async (id, userData) => {
    const response = await api.put(`/api/admin/users/${id}`, userData);
    return response;
  },

  // Delete user
  deleteUser: async (id) => {
    const response = await api.delete(`/api/admin/users/${id}`);
    return response;
  },

  // Change any user's password (admin only)
  changeUserPassword: async (id, newPassword) => {
    const response = await api.post(`/api/admin/users/${id}/password`, {
      new_password: newPassword,
    });
    return response;
  }
};

export default api;
