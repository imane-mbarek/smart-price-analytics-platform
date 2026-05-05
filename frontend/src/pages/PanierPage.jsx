// src/pages/PanierPage.jsx
import usePanier from "../hooks/usePanier";
import useAuth   from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

const fmt = (v) =>
  v?.toLocaleString("fr-MA", { style: "currency", currency: "MAD", maximumFractionDigits: 0 }) ?? "—";

function VariationBadge({ variation }) {
  if (!variation || variation === 0) return <span className="badge-neutral">Inchangé</span>;
  if (variation < 0) return <span className="badge-down">▼ {Math.abs(variation).toFixed(1)}%</span>;
  return <span className="badge-up">▲ {variation.toFixed(1)}%</span>;
}

export default function PanierPage() {
  const { items, retirer } = usePanier();
  const { user }  = useAuth();
  const navigate  = useNavigate();

  if (!user) {
    return (
      <div className="page">
        <div className="empty">
          Connectez-vous pour accéder à votre panier.
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
        <h1 className="title">Mon panier</h1>
        <span className="muted">{items.length} produit(s) surveillé(s)</span>
      </div>

      {items.length === 0 ? (
        <div className="empty">
          Votre panier est vide.<br />
          <span style={{ fontSize: 13 }}>Ajoutez des produits depuis la page de recherche.</span>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: ".75rem" }}>
          {items.map((item) => {
            const p = item.produit_detail;
            return (
              <div key={item.id} className="card panier-card">
                <div className="panier-info">
                  <p className="panier-nom">{p.nom}</p>
                  <span className="badge platform-color" style={{ fontSize: 11 }}>{p.plateforme}</span>
                </div>

                <div className="panier-prix">
                  <div>
                    <p className="muted" style={{ fontSize: 12 }}>Prix actuel</p>
                    <p className="prix-actuel">{fmt(p.prix)}</p>
                  </div>
                  <div>
                    <p className="muted" style={{ fontSize: 12 }}>Ajouté à</p>
                    <p style={{ fontSize: 14, fontWeight: 500 }}>{fmt(item.prix_au_moment)}</p>
                  </div>
                  <div>
                    <p className="muted" style={{ fontSize: 12 }}>Variation</p>
                    <VariationBadge variation={item.variation_prix} />
                  </div>
                </div>

                <div className="panier-actions">
                  {p.url && (
                    <a href={p.url} target="_blank" rel="noopener noreferrer" className="btn-sm">
                      Voir l'offre →
                    </a>
                  )}
                  <button className="btn-danger" onClick={() => retirer(p.id)}>
                    Retirer
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
