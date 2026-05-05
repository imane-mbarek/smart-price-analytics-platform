// src/pages/NotificationsPage.jsx
import useNotifications from "../hooks/useNotifications";
import useAuth          from "../hooks/useAuth";
import { useNavigate }  from "react-router-dom";

const TYPE_CONFIG = {
  baisse_prix : { icon: "▼", color: "#10b981", label: "Baisse de prix" },
  hausse_prix : { icon: "▲", color: "#f59e0b", label: "Hausse de prix" },
  rupture     : { icon: "✕", color: "#ef4444", label: "Rupture de stock" },
  retour_stock: { icon: "✓", color: "#3b82f6", label: "Retour en stock" },
};

const fmt = (v) => v != null
  ? v.toLocaleString("fr-MA", { style: "currency", currency: "MAD", maximumFractionDigits: 0 })
  : null;

export default function NotificationsPage() {
  const { notifs, nonLues, lire, toutLire } = useNotifications();
  const { user }   = useAuth();
  const navigate   = useNavigate();

  if (!user) {
    return (
      <div className="page">
        <div className="empty">
          Connectez-vous pour voir vos notifications.
          <br />
          <button className="btn-primary" style={{ marginTop: "1rem" }} onClick={() => navigate("/login")}>
            Se connecter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="row space-between" style={{ alignItems: "baseline" }}>
        <h1 className="title">
          Notifications
          {nonLues > 0 && <span className="notif-badge-title">{nonLues}</span>}
        </h1>
        {nonLues > 0 && (
          <button className="btn-sm" onClick={toutLire}>Tout marquer comme lu</button>
        )}
      </div>

      {notifs.length === 0 ? (
        <div className="empty">Aucune notification pour le moment.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: ".6rem" }}>
          {notifs.map((n) => {
            const cfg = TYPE_CONFIG[n.type_notif] || { icon: "•", color: "#6b7280", label: n.type_notif };
            return (
              <div
                key={n.id}
                className={`card notif-card ${!n.lue ? "notif-unread" : ""}`}
                onClick={() => !n.lue && lire(n.id)}
                style={{ cursor: n.lue ? "default" : "pointer" }}
              >
                <div className="notif-icon" style={{ background: cfg.color + "22", color: cfg.color }}>
                  {cfg.icon}
                </div>
                <div className="notif-body">
                  <div className="row" style={{ gap: ".5rem", flexWrap: "wrap" }}>
                    <span className="notif-type" style={{ color: cfg.color }}>{cfg.label}</span>
                    <span className="notif-produit">{n.produit_nom}</span>
                  </div>
                  <p className="notif-message">{n.message}</p>
                  {n.ancien_prix && n.nouveau_prix && (
                    <p className="muted" style={{ fontSize: 12, marginTop: 2 }}>
                      {fmt(n.ancien_prix)} → {fmt(n.nouveau_prix)}
                    </p>
                  )}
                  <p className="muted" style={{ fontSize: 11, marginTop: 4 }}>
                    {new Date(n.date).toLocaleDateString("fr-FR", {
                      day: "2-digit", month: "short", year: "numeric",
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </p>
                </div>
                {!n.lue && <div className="notif-dot" />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
