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
    // No agregar token a endpoints de autenticación
    const authEndpoints = ['/microsoft/auth/login', '/microsoft/auth/callback'];
    const isAuthEndpoint = authEndpoints.some(endpoint => config.url.includes(endpoint));
    
    if (!isAuthEndpoint) {
      const token = localStorage.getItem('token');
      if (token) {
        console.log('Adding Authorization header with token:', token.substring(0, 20) + '...');
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        console.log('No token found in localStorage');
      }
    } else {
      console.log('Skipping token for auth endpoint:', config.url);
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
    if (error.response?.status === 401 && !window.location.pathname.includes('/auth/callback')) {
      // Token expirado o inválido - pero no redirigir durante el callback
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Solo redirigir si no estamos ya en login
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// Keep alive function for free tier
export const keepAlive = () => {
  setInterval(async () => {
    try {
      await api.get('/ping');
      console.log('Server pinged successfully');
    } catch (error) {
      console.log('Ping failed:', error.message);
    }
  }, 10 * 60 * 1000); // Ping every 10 minutes
};

// Funciones de la API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
};

export const emailAPI = {
  getAccounts: () => api.get('/emails/accounts'),
  connectAccount: (data) => api.post('/emails/connect', data),
  getEmails: (params) => api.get('/emails/', { params }),
  getEmailsByUrgency: (urgency) => api.get(`/emails/urgency/${urgency}`),
  markAsRead: (emailId) => api.patch(`/emails/${emailId}/read`),
  syncEmails: (data) => api.post('/emails/sync', data),
  sendEmail: (data) => api.post('/emails/send', data),
  replyToEmail: (emailId, data) => api.post(`/emails/${emailId}/reply`, data),
};

export const microsoftAPI = {
  getAuthUrl: () => api.get('/microsoft/auth/login'),
  callback: (code) => api.post('/microsoft/auth/callback', { code }),
  status: () => api.get('/microsoft/status'),
  profile: () => api.get('/microsoft/profile'),
  disconnect: () => api.post('/microsoft/auth/disconnect'),
  testPermissions: () => api.get('/microsoft/test-permissions'),
};

export default api;