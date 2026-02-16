import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
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
      // Unauthorized - redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const auth = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  register: async (email: string, password: string, name: string) => {
    const response = await api.post('/auth/register', { email, password, name });
    return response.data;
  },
};

// Companies endpoints
export const companies = {
  list: async (skip = 0, limit = 50) => {
    const response = await api.get('/companies', { params: { skip, limit } });
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/companies', data);
    return response.data;
  },
  
  get: async (id: string) => {
    const response = await api.get(`/companies/${id}`);
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/companies/${id}`);
    return response.data;
  },
  
  scan: async (id: string) => {
    const response = await api.post(`/companies/${id}/scan`);
    return response.data;
  },
};

// Changes endpoints
export const changes = {
  list: async (params?: any) => {
    const response = await api.get('/changes', { params });
    return response.data;
  },
  
  get: async (id: string) => {
    const response = await api.get(`/changes/${id}`);
    return response.data;
  },
};

// Users endpoints
export const users = {
  stats: async () => {
    const response = await api.get('/users/stats');
    return response.data;
  },
};

export default api;