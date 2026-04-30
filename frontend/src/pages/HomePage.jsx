// src/pages/HomePage.jsx
import { useState, useMemo } from "react";
import useSearch from "../hooks/useSearch";
import { exportCSV, exportPDF } from "../services/api";
import PriceHistogram from "../components/PriceHistogram";
import BoxPlot        from "../components/BoxPlot";
import ProductsTable  from "../components/ProductsTable";

const PLATFORMS = [
  { id: "jumia", label: "Jumia.ma" },
  { id: "avito", label: "Avito.ma" },
  { id: "ebay",  label: "eBay" },
];

function downloadBlob(blob, name) {
  const url = URL.createObjectURL(blob);
  Object.assign(document.createElement("a"), { href: url, download: name }).click();
  URL.revokeObjectURL(url);
}

export default function HomePage() {
  const { status, progress, message, produits, error, query, search } = useSearch();
  const [input,    setInput]    = useState("");
  const [selected, setSelected] = useState(["jumia", "avito", "ebay"]);

  const toggle = (id) =>
    setSelected((p) => p.includes(id) ? p.filter((x) => x !== id) : [...p, id]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && selected.length) search(input.trim(), selected);
  };

  const handleCSV = async () => { const r = await exportCSV(query); downloadBlob(r.data, `${query}.csv`); };
  const handlePDF = async () => { const r = await exportPDF(query); downloadBlob(r.data, `${query}.pdf`); };

  return (
    <div className="page">

      {/* ── Recherche ── */}
      <section className="card">
        <h1 className="title">Smart Price Analytics</h1>
        <p className="sub">Collecte et analyse des prix sur Jumia, Avito et eBay</p>

        <form onSubmit={handleSubmit} className="search-form">
          <div className="row">
            <input
              className="input"
              placeholder='Ex : "hp pc portable", "iphone 15"'
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={status === "loading"}
            />
            <button className="btn-primary" disabled={status === "loading" || !input.trim() || !selected.length}>
              {status === "loading" ? "En cours…" : "Analyser"}
            </button>
          </div>

          <div className="chips">
            <span className="chips-label">Plateformes :</span>
            {PLATFORMS.map((p) => (
              <label key={p.id} className={`chip ${selected.includes(p.id) ? "active" : ""}`}>
                <input type="checkbox" checked={selected.includes(p.id)} onChange={() => toggle(p.id)} hidden />
                {p.label}
              </label>
            ))}
          </div>
        </form>
      </section>

      {/* ── Progression ── */}
      {status === "loading" && (
        <div className="card">
          <div className="prog-header">
            <span>{message || "Scraping en cours…"}</span>
            <strong>{progress}%</strong>
          </div>
          <div className="prog-track"><div className="prog-fill" style={{ width: `${progress}%` }} /></div>
        </div>
      )}

      {/* ── Erreur ── */}
      {status === "error" && <div className="alert">⚠ {error}</div>}

      {/* ── Résultats ── */}
      {status === "done" && (
        <>
          <div className="row space-between">
            <span className="muted">{produits.length} offre(s) pour « {query} »</span>
            <div className="row gap-sm">
              <button className="btn-sm" onClick={handleCSV}>⬇ CSV</button>
              <button className="btn-sm" onClick={handlePDF}>⬇ PDF</button>
            </div>
          </div>

          {produits.length > 0 ? (
            <>
              <div className="grid-2">
                <PriceHistogram produits={produits} />
                <BoxPlot        produits={produits} />
              </div>
              <ProductsTable produits={produits} />
            </>
          ) : (
            <div className="empty">Aucun produit trouvé pour « {query} ».</div>
          )}
        </>
      )}

      {status === "idle" && (
        <div className="empty">🔍 Saisissez un produit pour démarrer</div>
      )}
    </div>
  );
}
