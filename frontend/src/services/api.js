import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens (if needed in future)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Process PDF
  processPDF: (file, saveToDb = true) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/api/process?save_to_db=${saveToDb}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Submissions
  getSubmissions: (projectId = null, limit = null) => {
    const params = {};
    if (projectId) params.project_id = projectId;
    if (limit) params.limit = limit;
    return api.get('/api/submissions', { params });
  },

  getSubmission: (submissionId) => api.get(`/api/submissions/${submissionId}`),

  deleteSubmission: (submissionId) => api.delete(`/api/submissions/${submissionId}`),

  // Search
  search: (query) => api.get('/api/search', { params: { q: query } }),

  // Statistics
  getStatistics: () => api.get('/api/statistics'),

  // Projects
  getProjects: () => api.get('/api/projects'),

  // Samples
  getSamples: (submissionId) => api.get(`/api/samples/${submissionId}`),

  // Check duplicate
  checkDuplicate: (fileHash) => api.get('/api/check-duplicate', { params: { file_hash: fileHash } }),

  // Export
  exportDatabase: (format = 'json') => {
    return api.get('/api/export', {
      params: { format },
      responseType: 'blob',
    });
  },
};

export default apiService;
