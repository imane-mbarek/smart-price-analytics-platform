// src/services/api.js
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Produits ──────────────────────────────────────────────────────────
export const getAllProduits  = ()              => api.get("/produits/");
export const lancerRecherche = (q, plateformes) => api.get("/produits/search_async/", { params: { q, plateformes: plateformes.join(",") } });
export const getProgression  = (taskId)        => api.get("/produits/progression/",   { params: { task_id: taskId } });
export const exportCSV       = (q)             => api.get("/produits/export_csv/",    { params: { q }, responseType: "blob" });
export const exportPDF       = (q)             => api.get("/produits/export_pdf/",    { params: { q }, responseType: "blob" });

// ── Panier ────────────────────────────────────────────────────────────
export const getPanier        = ()           => api.get("/panier/");
export const getPanierCount   = ()           => api.get("/panier/count/");
export const ajouterAuPanier  = (produitId)  => api.post("/panier/",           { produit: produitId });
export const retirerDuPanier  = (produitId)  => api.delete(`/panier/${produitId}/`);

// ── Notifications ─────────────────────────────────────────────────────
export const getNotifications  = ()  => api.get("/notifications/");
export const getNonLues        = ()  => api.get("/notifications/non_lues/");
export const marquerLue        = (id) => api.post(`/notifications/${id}/lire/`);
export const toutMarquerLu     = ()  => api.post("/notifications/tout_lire/");

// ── Historique ────────────────────────────────────────────────────────
export const getHistorique = () => api.get("/recherches/");

// ── Auth ──────────────────────────────────────────────────────────────
export const login    = (data) => axios.post("/api/token/",    data);
export const register = (data) => axios.post("/api/register/", data);
export const logout   = ()     => { localStorage.removeItem("access"); localStorage.removeItem("refresh"); };
