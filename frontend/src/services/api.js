import axios from 'axios';

// Configuración base de Axios
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para incluir token de autenticación
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

// Interceptor para manejar respuestas
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Funciones de la API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
};

export const emailAPI = {
  getAccounts: () => api.get('/emails/accounts'),
  connectAccount: (data) => api.post('/emails/connect', data),
  getEmails: (params) => api.get('/emails', { params }),
  getEmailsByUrgency: (urgency) => api.get(`/emails/urgency/${urgency}`),
  markAsRead: (emailId) => api.patch(`/emails/${emailId}/read`),
};

export const microsoftAPI = {
  getAuthUrl: () => api.get('/microsoft/auth-url'),
  callback: (code) => api.post('/microsoft/callback', { code }),
};

export default api;