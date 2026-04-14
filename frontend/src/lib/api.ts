import axios, { AxiosRequestConfig } from 'axios';

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://apicotizador.policlinicotabancura.cl';

// Extend AxiosRequestConfig to include our custom retry properties
interface CustomConfig extends AxiosRequestConfig {
  retry?: number;
  retryDelay?: number;
  retryCount?: number;
}

// Create a configured axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
});

// Simple retry interceptor
api.interceptors.response.use(null, async (error) => {
  const config = error.config as CustomConfig;
  if (!config || !config.retry) return Promise.reject(error);
  
  config.retryCount = config.retryCount || 0;
  
  if (config.retryCount >= config.retry) {
    return Promise.reject(error);
  }
  
  config.retryCount += 1;
  const backoff = new Promise((resolve) => {
    setTimeout(() => resolve(null), (config.retryDelay || 1) * 1000);
  });
  
  return backoff.then(() => api(config));
});

export interface Examen {
  codigo: string;
  nombre: string;
  valor_bono_fonasa: number;
  valor_copago: number;
  valor_particular_general: number;
  valor_particular_preferencial: number;
  busqueda: string;
}

export interface Paquete {
  nombre: string;
  examenes: {
    codigo: string | null;
    nombre: string;
    cantidad: number;
  }[];
}

// Helper for requests with retry
const withRetry: CustomConfig = { retry: 3, retryDelay: 1.5 };

export const getExamenes = () => api.get<Examen[]>('/api/examenes', withRetry);
export const getPaquetes = () => api.get<Paquete[]>('/api/paquetes', withRetry);
export const getPaciente = (docId: string) => api.get(`/api/paciente/${docId}`, withRetry);
export const postCotizar = (data: any) => api.post('/api/cotizar', data);

// --- Admin Endpoints ---
export const adminLogin = (credentials: any) => api.post('/api/admin/login', credentials);
export const getAdminStats = (token: string) => api.get('/api/admin/stats', { headers: { 'Authorization': `Bearer ${token}`, 'password': token } }); 
export const getAdminHistory = (token: string) => api.get('/api/admin/history', { headers: { 'password': token } });
export const updateArancel = (codigo: string, data: any, token: string) => api.put(`/api/admin/aranceles/${codigo}`, data, { headers: { 'password': token } });

