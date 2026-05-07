// src/pages/HistoryPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getHistorique } from "../services/api";
import useAuth from "../hooks/useAuth";

export default function HistoryPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      setHistory([]);
      setLoading(false);
      return;
    }

    getHistorique().then(({ data }) => setHistory(data)).catch(() => {}).finally(() => setLoading(false));
  }, [user]);

  return (
    <div className="page-content">
      <div className="section-header">
        <h2 className="section-title">Historique des recherches</h2>
      </div>

      {loading && <p style={{ color: "#94a3b8", fontSize: 14 }}>Chargement...</p>}

      {!loading && !user && (
        <div className="empty-state">Connectez-vous pour voir votre historique.</div>
      )}

      {!loading && user && !history.length && (
        <div className="empty-state">Aucune recherche enregistrée.</div>
      )}

      {user && <div style={{ display: "flex", flexDirection: "column", gap: ".6rem" }}>
        {history.map((item) => (
          <div key={item.id} className="history-item">
            <div>
              <p className="history-query">« {item.produit} »</p>
              <p className="history-date">
                {new Date(item.date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
              </p>
            </div>
            <button
              className="toolbar-btn"
              onClick={() => navigate("/", { state: { query: item.produit } })}
            >
              🔁 Relancer
            </button>
          </div>
        ))}
      </div>}
    </div>
  );
}
