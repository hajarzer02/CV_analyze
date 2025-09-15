import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
  
  const response = await api.post('/upload-cv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Get candidate by ID
export const getCandidate = async (id) => {
  const response = await api.get(`/candidate/${id}`);
  return response.data;
};

// Get all candidates
export const getCandidates = async () => {
  const response = await api.get('/candidates');
  return response.data;
};

// Generate recommendations for candidate
export const generateRecommendations = async (id) => {
  const response = await api.post(`/recommend/${id}`);
  return response.data;
};

// Delete candidate
export const deleteCandidate = async (id) => {
  const response = await api.delete(`/candidates/${id}`);
  return response.data;
};

// Update candidate status
export const updateCandidateStatus = async (id, status) => {
  const response = await api.patch(`/candidate/${id}/status`, { status });
  return response.data;
};

// Match job against candidates
export const matchJob = async (jobDescription) => {
  const response = await api.post('/match-job', { job_description: jobDescription });
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

export default api;
