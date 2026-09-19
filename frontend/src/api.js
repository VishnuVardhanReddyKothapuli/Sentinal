import axios from 'axios';
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api/v1', timeout: 180000 });
api.interceptors.request.use(config => {const token = localStorage.getItem('sentinel_token'); if (token) config.headers.Authorization = `Bearer ${token}`; return config;});
api.interceptors.response.use(response => response, error => {if(error.response?.status === 401 && !error.config.url.includes('/auth/login')) {localStorage.removeItem('sentinel_token'); window.dispatchEvent(new Event('sentinel:logout'));} return Promise.reject(error);});
export function errorMessage(error) {const detail = error.response?.data?.detail; return typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(item => item.msg).join('. ') : error.code === 'ERR_NETWORK' ? 'Unable to reach Sentinel. Check that the API is running and try again.' : error.message || 'Something went wrong. Please try again.';}
