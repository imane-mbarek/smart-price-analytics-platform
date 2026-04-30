// src/pages/HistoryPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getHistorique } from "../services/api";

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getHistorique().then(({ data }) => setHistory(data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <h1 className="title">Historique des recherches</h1>
      {loading && <p className="muted">Chargement…</p>}
      {!loading && !history.length && <div className="empty">Aucune recherche enregistrée.</div>}
      {history.map((item) => (
        <div key={item.id} className="card row space-between">
          <div>
            <strong>« {item.produit} »</strong>
            <p className="muted" style={{ marginTop: 4 }}>
              {new Date(item.date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>
          <button className="btn-sm" onClick={() => navigate("/", { state: { query: item.produit } })}>
            🔁 Relancer
          </button>
        </div>
      ))}
    </div>
  );
}
