import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1',
});

// Request interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('business_nexus_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('business_nexus_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
