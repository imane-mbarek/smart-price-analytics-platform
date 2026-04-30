// src/components/ProductsTable.jsx
import { useState, useMemo } from "react";

const COLORS = { jumia: "#F97316", Jumia: "#F97316", avito: "#EF4444", Avito: "#EF4444", ebay: "#8B5CF6", eBay: "#8B5CF6" };

export default function ProductsTable({ produits }) {
  const [platform, setPlatform] = useState("all");
  const [maxPrice, setMaxPrice] = useState("");
  const [sortDir,  setSortDir]  = useState("asc");

  const platforms = useMemo(() => ["all", ...new Set(produits.map((p) => p.plateforme))], [produits]);

  const list = useMemo(() => {
    let r = produits;
    if (platform !== "all") r = r.filter((p) => p.plateforme === platform);
    if (maxPrice)           r = r.filter((p) => p.prix <= parseFloat(maxPrice));
    return [...r].sort((a, b) => sortDir === "asc" ? a.prix - b.prix : b.prix - a.prix);
  }, [produits, platform, maxPrice, sortDir]);

  const fmt = (v) => v?.toLocaleString("fr-MA", { style: "currency", currency: "MAD", maximumFractionDigits: 0 }) ?? "—";

  return (
    <div className="chart-card">
      <h3 className="chart-title">Offres collectées</h3>

      <div className="filters">
        <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="select">
          {platforms.map((p) => <option key={p} value={p}>{p === "all" ? "Toutes les plateformes" : p}</option>)}
        </select>
        <input type="number" placeholder="Prix max (MAD)" value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)} className="input" style={{ maxWidth: 160 }} />
        <button className="btn-sm" onClick={() => setSortDir((d) => d === "asc" ? "desc" : "asc")}>
          Prix {sortDir === "asc" ? "↑" : "↓"}
        </button>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr><th>Produit</th><th>Plateforme</th><th>Prix</th><th>Lien</th></tr>
          </thead>
          <tbody>
            {!list.length
              ? <tr><td colSpan={4} style={{ textAlign: "center", color: "#94a3b8", padding: "1.5rem" }}>Aucun résultat</td></tr>
              : list.map((p) => (
                <tr key={p.id}>
                  <td className="td-nom">{p.nom}</td>
                  <td>
                    <span className="badge" style={{ background: (COLORS[p.plateforme] || "#6B7280") + "22", color: COLORS[p.plateforme] || "#374151" }}>
                      {p.plateforme}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600 }}>{fmt(p.prix)}</td>
                  <td>{p.url ? <a href={p.url} target="_blank" rel="noopener noreferrer" className="link">Voir →</a> : "—"}</td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
      <p className="note">{list.length} / {produits.length} offre(s)</p>
    </div>
  );
}
