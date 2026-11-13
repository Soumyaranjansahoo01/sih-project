import axios from 'axios';

// Dynamically resolve API base URL for localhost, 127.0.0.1, and LAN IP addresses
const getBaseUrl = () => {
  if (typeof window !== 'undefined' && window.location) {
    const hostname = window.location.hostname;
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:8000`;
    }
  }
  return '/api';
};

const apiClient = axios.create({
  baseURL: getBaseUrl(),
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // System
  getRoot: () => apiClient.get('/'),
  getHealth: () => apiClient.get('/health'),

  // Tasks
  getTasks: (params) => apiClient.get('/tasks', { params }),
  getTaskDetails: (taskId) => apiClient.get(`/tasks/${taskId}`),
  createTask: (data) => apiClient.post('/tasks', data),
  recalculatePriorities: (weights) => apiClient.post('/tasks/recalculate', weights),

  // Optimization & Schedule
  getBaseline: (horizonDays = 7) => apiClient.get(`/baseline?horizon_days=${horizonDays}`),
  runOptimize: (data) => apiClient.post('/optimize', data),
  getSchedule: (params) => apiClient.get('/schedule', { params }),
  getWeeklySchedule: () => apiClient.get('/schedule/weekly'),
  getMonthlySchedule: () => apiClient.get('/schedule/monthly'),
  getComparison: (runId) => apiClient.get(runId ? `/comparison?run_id=${runId}` : '/comparison'),
  getConflicts: (params) => apiClient.get('/conflicts', { params }),
  getExplanation: (taskId) => apiClient.get(`/optimization/explanation/${taskId}`),

  // Network & Assets
  getNetwork: () => apiClient.get('/network'),
  getSections: (params) => apiClient.get('/sections', { params }),
  getTrains: (params) => apiClient.get('/trains', { params }),
  getAssets: (params) => apiClient.get('/assets', { params }),

  // Analytics & Simulation
  getAnalytics: () => apiClient.get('/analytics'),
  runSimulation: (data) => apiClient.post('/simulate', data),
};

export default api;
