import axios, { AxiosError } from 'axios';
import { LoadCreate, BatteryConfig, ValidationResponse } from '../types';

const API_BASE = 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE, timeout: 30000 });

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError | any) => {
    console.error('API Error:', error);
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return Promise.reject('Request timed out. The server took too long to respond.');
    }
    if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
      return Promise.reject('Unable to connect to the microgrid backend. Please make sure the FastAPI server is running.');
    }
    return Promise.reject(error.response?.data?.detail || error.message || 'An unexpected error occurred');
  }
);

export const dashboardApi = { getDashboard: () => api.get('/api/dashboard').then(r => r.data) };
export const forecastApi = { 
  getForecast: (date?: string) => api.get('/api/forecast', { params: { date } }).then(r => r.data),
  trainModel: () => api.post('/api/forecast/train').then(r => r.data),
  getMetrics: () => api.get('/api/forecast/metrics').then(r => r.data),
  getActualVsPredicted: () => api.get('/api/forecast/actual-vs-predicted').then(r => r.data),
  getErrorAnalysis: () => api.get('/api/forecast/error-analysis').then(r => r.data),
};
export const loadsApi = {
  getLoads: () => api.get('/api/loads').then(r => r.data),
  createLoad: (data: LoadCreate) => api.post('/api/loads', data).then(r => r.data),
  updateLoad: (id: number, data: Partial<LoadCreate>) => api.put(`/api/loads/${id}`, data).then(r => r.data),
  deleteLoad: (id: number) => api.delete(`/api/loads/${id}`).then(r => r.data),
};
export const batteryApi = {
  getBattery: () => api.get('/api/battery').then(r => r.data),
  updateBattery: (data: Partial<BatteryConfig>) => api.put('/api/battery', data).then(r => r.data),
  getSimulation: () => api.get('/api/battery/simulation').then(r => r.data),
};
export const schedulerApi = {
  runSchedule: (date?: string) => api.post('/api/scheduler/run', { date }).then(r => r.data),
  getLatest: () => api.get('/api/scheduler/latest').then(r => r.data),
};
export const baselineApi = {
  runBaseline: (date?: string) => api.post('/api/baseline/run', { date }).then(r => r.data),
  getLatest: () => api.get('/api/baseline').then(r => r.data),
};
export const experimentsApi = {
  runExperiment: (data: { name: string, date: string }) => api.post('/api/experiments/run', data).then(r => r.data),
  getResults: () => api.get('/api/experiments/results').then(r => r.data),
  getLatestResult: () => api.get('/api/experiments/results/latest').then(r => r.data),
};
export const validationApi = {
  submit: (data: ValidationResponse) => api.post('/api/validation', data).then(r => r.data),
  getAll: () => api.get('/api/validation').then(r => r.data),
};
