import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const c2Api = {
  // Nodes
  getNodes: async () => {
    const response = await axios.get(`${API_BASE}/nodes/`);
    return response.data;
  },

  getNode: async (nodeId) => {
    const response = await axios.get(`${API_BASE}/nodes/${nodeId}`);
    return response.data;
  },

  // Tasks
  getTasks: async (status = null) => {
    const url = status ? `${API_BASE}/tasks/?status=${status}` : `${API_BASE}/tasks/`;
    const response = await axios.get(url);
    return response.data;
  },

  createTask: async (taskData) => {
    const response = await axios.post(`${API_BASE}/tasks/`, taskData);
    return response.data;
  },

  // Statistics
  getStats: async () => {
    const response = await axios.get(`${API_BASE}/stats/overview`);
    return response.data;
  },

  // Health
  getHealth: async () => {
    const response = await axios.get('http://localhost:8000/health');
    return response.data;
  }
};
