import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default api;
