import axios from 'axios';

const API_BASE = '/api/v1';

export const analyzeField = async (polygonGeoJSON) => {
  const response = await axios.post(`${API_BASE}/field/info`, {
    type: 'Feature',
    geometry: polygonGeoJSON.geometry || polygonGeoJSON
  });
  return response.data;
};

export const predictNitrogen = async (payload) => {
  const response = await axios.post(`${API_BASE}/predict`, payload);
  return response.data;
};

export const checkHealth = async () => {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
};
