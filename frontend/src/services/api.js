// src/services/api.js
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Scraping
export const lancerRecherche = (query, plateformes) =>
  api.get("/produits/search_async/", { params: { q: query, plateformes: plateformes.join(",") } });

export const getProgression = (taskId) =>
  api.get("/produits/progression/", { params: { task_id: taskId } });

// Export
export const exportCSV = (query) =>
  api.get("/produits/export_csv/", { params: { q: query }, responseType: "blob" });

export const exportPDF = (query) =>
  api.get("/produits/export_pdf/", { params: { q: query }, responseType: "blob" });

// Historique
export const getHistorique = () => api.get("/recherches/");

// Auth
export const login    = (data) => axios.post("/api/token/",    data);
export const register = (data) => axios.post("/api/register/", data);
export const logout   = ()     => { localStorage.removeItem("access"); localStorage.removeItem("refresh"); };
