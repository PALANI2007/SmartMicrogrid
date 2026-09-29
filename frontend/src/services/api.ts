/** API service layer: all backend communication goes through this module. Base URL auto-adapts based on environment. */
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

/** dashboardApi: fetches the aggregated dashboard summary (generation, load, SOC, etc.) */
export const dashboardApi = { getDashboard: () => api.get('/api/dashboard').then(r => r.data) };

/** forecastApi: manages solar generation forecasts — fetching predictions, triggering model training, and retrieving accuracy metrics. */
export const forecastApi = { 
  getForecast: (date?: string) => api.get('/api/forecast', { params: { date } }).then(r => r.data),
  trainModel: () => api.post('/api/forecast/train').then(r => r.data),
  getMetrics: () => api.get('/api/forecast/metrics').then(r => r.data),
  getActualVsPredicted: () => api.get('/api/forecast/actual-vs-predicted').then(r => r.data),
  getErrorAnalysis: () => api.get('/api/forecast/error-analysis').then(r => r.data),
};

/** loadsApi: CRUD operations for electrical load devices (add, update, delete, list). */
export const loadsApi = {
  getLoads: () => api.get('/api/loads').then(r => r.data),
  createLoad: (data: LoadCreate) => api.post('/api/loads', data).then(r => r.data),
  updateLoad: (id: number, data: Partial<LoadCreate>) => api.put(`/api/loads/${id}`, data).then(r => r.data),
  deleteLoad: (id: number) => api.delete(`/api/loads/${id}`).then(r => r.data),
};

/** batteryApi: retrieves battery state-of-charge, updates configuration, and fetches charge/discharge simulation results. */
export const batteryApi = {
  getBattery: () => api.get('/api/battery').then(r => r.data),
  updateBattery: (data: Partial<BatteryConfig>) => api.put('/api/battery', data).then(r => r.data),
  getSimulation: () => api.get('/api/battery/simulation').then(r => r.data),
};

/** schedulerApi: triggers the optimization scheduler for a given date and retrieves the latest schedule result. */
export const schedulerApi = {
  runSchedule: (date?: string) => api.post('/api/scheduler/run', { date }).then(r => r.data),
  getLatest: () => api.get('/api/scheduler/latest').then(r => r.data),
};

/** baselineApi: runs the naive/rule-based baseline scheduler and retrieves its latest result for comparison. */
export const baselineApi = {
  runBaseline: (date?: string) => api.post('/api/baseline/run', { date }).then(r => r.data),
  getLatest: () => api.get('/api/baseline').then(r => r.data),
};

/** experimentsApi: executes named experiments (e.g. "no_battery", "peak_shaving") and retrieves historical results. */
export const experimentsApi = {
  runExperiment: (data: { name: string, date: string }) => api.post('/api/experiments/run', data).then(r => r.data),
  getResults: () => api.get('/api/experiments/results').then(r => r.data),
  getLatestResult: () => api.get('/api/experiments/results/latest').then(r => r.data),
};

/** validationApi: submits human validation responses and retrieves all previously recorded validations. */
export const validationApi = {
  submit: (data: ValidationResponse) => api.post('/api/validation', data).then(r => r.data),
  getAll: () => api.get('/api/validation').then(r => r.data),
};

/** edgeCasesApi: runs and retrieves results for edge-case/stress-test scenarios (e.g. zero generation, battery full). */
export const edgeCasesApi = {
  getResults: () => api.get('/api/edge-cases').then(r => r.data),
  runAll: (scenario_id = 'all') => api.post('/api/edge-cases/run', { scenario_id }).then(r => r.data),
};

/** forecastErrorsApi: fetches the empirical forecast error distribution from the test period (/api/forecast/errors). */
export const forecastErrorsApi = {
  getErrorDistribution: () => api.get('/api/forecast/errors').then(r => r.data),
};

