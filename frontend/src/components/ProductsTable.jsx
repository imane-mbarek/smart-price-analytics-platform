// src/components/ProductsTable.jsx
import { useState, useMemo } from "react";
import usePanier from "../hooks/usePanier";
import useAuth   from "../hooks/useAuth";

const COLORS = {
  jumia: "#F97316", Jumia: "#F97316",
  avito: "#EF4444", Avito: "#EF4444",
  ebay:  "#8B5CF6", eBay:  "#8B5CF6",
};

const fmt = (v) =>
  v?.toLocaleString("fr-MA", { style: "currency", currency: "MAD", maximumFractionDigits: 0 }) ?? "—";

function BoutonPanier({ produitId }) {
  const { user }          = useAuth();
  const { ajouter, retirer, estDansPanier } = usePanier();
  const [loading, setLoading] = useState(false);

  if (!user) return null; // masqué si non connecté

  const dansPanier = estDansPanier(produitId);

  const handleClick = async (e) => {
    e.stopPropagation();
    setLoading(true);
    try {
      dansPanier ? await retirer(produitId) : await ajouter(produitId);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      className={dansPanier ? "btn-panier-active" : "btn-panier"}
      onClick={handleClick}
      disabled={loading}
      title={dansPanier ? "Retirer du panier" : "Ajouter au panier"}
    >
      {loading ? "…" : dansPanier ? "🛒 ✓" : "🛒"}
    </button>
  );
}

export default function ProductsTable({ produits, showSearch = false }) {
  const [platform,   setPlatform]   = useState("all");
  const [maxPrice,   setMaxPrice]   = useState("");
  const [localQuery, setLocalQuery] = useState("");
  const [sortDir,    setSortDir]    = useState("asc");

  const platforms = useMemo(
    () => ["all", ...new Set(produits.map((p) => p.plateforme))],
    [produits]
  );

  const list = useMemo(() => {
    let r = produits;
    if (platform !== "all") r = r.filter((p) => p.plateforme === platform);
    if (maxPrice)           r = r.filter((p) => p.prix <= parseFloat(maxPrice));
    if (localQuery)         r = r.filter((p) => p.nom?.toLowerCase().includes(localQuery.toLowerCase()));
    return [...r].sort((a, b) => sortDir === "asc" ? a.prix - b.prix : b.prix - a.prix);
  }, [produits, platform, maxPrice, localQuery, sortDir]);

  return (
    <div className="chart-card">
      <h3 className="chart-title">Offres collectées</h3>

      <div className="filters">
        {showSearch && (
          <input
            className="input" placeholder="Filtrer par nom…"
            value={localQuery} onChange={(e) => setLocalQuery(e.target.value)}
            style={{ maxWidth: 200 }}
          />
        )}
        <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="select">
          {platforms.map((p) => (
            <option key={p} value={p}>{p === "all" ? "Toutes les plateformes" : p}</option>
          ))}
        </select>
        <input
          type="number" placeholder="Prix max (MAD)"
          value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)}
          className="input" style={{ maxWidth: 150 }}
        />
        <button className="btn-sm" onClick={() => setSortDir((d) => d === "asc" ? "desc" : "asc")}>
          Prix {sortDir === "asc" ? "↑" : "↓"}
        </button>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Produit</th>
              <th>Plateforme</th>
              <th>Prix</th>
              <th>Lien</th>
              <th>Panier</th>
            </tr>
          </thead>
          <tbody>
            {!list.length ? (
              <tr>
                <td colSpan={5} style={{ textAlign: "center", color: "#94a3b8", padding: "1.5rem" }}>
                  Aucun résultat
                </td>
              </tr>
            ) : (
              list.map((p) => (
                <tr key={p.id}>
                  <td className="td-nom">{p.nom}</td>
                  <td>
                    <span className="badge" style={{
                      background: (COLORS[p.plateforme] || "#6B7280") + "22",
                      color: COLORS[p.plateforme] || "#374151",
                    }}>
                      {p.plateforme}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600 }}>{fmt(p.prix)}</td>
                  <td>
                    {p.url
                      ? <a href={p.url} target="_blank" rel="noopener noreferrer" className="link">Voir →</a>
                      : "—"}
                  </td>
                  <td><BoutonPanier produitId={p.id} /></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <p className="note">{list.length} / {produits.length} offre(s)</p>
    </div>
  );
}
