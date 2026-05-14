// src/services/api.js
import axios from "axios";

const api = axios.create({ baseURL: "/api" });
const publicApi = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("user");
      window.dispatchEvent(new Event("auth:logout"));
    }
    return Promise.reject(error);
  }
);

// ── Produits ──────────────────────────────────────────────────────────
export const getAllProduits     = ()               => publicApi.get("/produits/");
export const getAccueilProduits = (limit = 12)     => publicApi.get("/produits/accueil/", { params: { limit } });
export const lancerRecherche    = (q, plateformes) => publicApi.get("/produits/search_async/", { params: { q, plateformes: plateformes.join(",") } });
export const getProgression     = (taskId)         => publicApi.get("/produits/progression/",   { params: { task_id: taskId } });
export const getAnalyse         = (q)              => publicApi.get("/produits/analyser/",      { params: { q } });
export const exportCSV          = (q)              => publicApi.get("/produits/export_csv/",    { params: { q }, responseType: "blob" });
export const exportPDF          = (q)              => publicApi.get("/produits/export_pdf/",    { params: { q }, responseType: "blob" });

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
