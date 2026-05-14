// src/pages/HomePage.jsx
import { useState, useEffect, useMemo } from "react";
import { useLocation }   from "react-router-dom";
import useAuth           from "../hooks/useAuth";
import useSearch         from "../hooks/useSearch";
import { getAccueilProduits, exportCSV, exportPDF } from "../services/api";
import ProductCard       from "../components/ProductCard";
import AnalysePanel      from "../components/AnalysePanel";

const PLATFORMS = [
  { id: "jumia", label: "Jumia.ma" },
  { id: "avito", label: "Avito.ma" },
  { id: "ebay",  label: "eBay" },
];

const MOTS_PARASITES = [
  "coque","étui","etui","housse","protection","verre","film",
  "chargeur","câble","cable","adaptateur","écouteurs","ecouteurs",
  "airpods","casque","batterie","accessoire","kit","pack","compatible",
];

function matchStrict(nom, query) {
  if (!nom || !query) return false;
  const n = nom.toLowerCase();
  const q = query.toLowerCase();
  const first = n.split(/\s+/)[0];
  if (MOTS_PARASITES.some((p) => first === p || n.startsWith(p + " "))) return false;
  return new RegExp(`(^|\\s)${q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`, "i").test(
    n.split(/\s+/).slice(0, 4).join(" ")
  );
}

function downloadBlob(blob, name) {
  const url = URL.createObjectURL(blob);
  Object.assign(document.createElement("a"), { href: url, download: name }).click();
  URL.revokeObjectURL(url);
}

export default function HomePage() {
  const { user } = useAuth();
  const location = useLocation();

  // Catalogue
  const [catalog,     setCatalog]     = useState([]);
  const [loadingCat,  setLoadingCat]  = useState(true);

  // Recherche
  const [input,    setInput]    = useState(location.state?.query || "");
  const [selected, setSelected] = useState(["jumia", "avito", "ebay"]);
  const [searched, setSearched] = useState(false);
  const { status, progress, message, produits: scraped, analyse, error, query, search } = useSearch();

  useEffect(() => {
    getAccueilProduits(12)
      .then(({ data }) => setCatalog(data))
      .catch(() => setCatalog([]))
      .finally(() => setLoadingCat(false));
  }, []);

  // Si relance depuis historique
  useEffect(() => {
    if (location.state?.query) {
      setSearched(true);
      search(location.state.query, selected);
    }
  }, []); // eslint-disable-line

  const resultsFiltered = useMemo(
    () => searched ? scraped.filter((p) => matchStrict(p.nom, query)) : [],
    [scraped, query, searched]
  );

  const toggle = (id) =>
    setSelected((p) => p.includes(id) ? p.filter((x) => x !== id) : [...p, id]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || !selected.length || !user) return;
    setSearched(true);
    search(input.trim(), selected);
  };

  const handleReset = () => { setSearched(false); setInput(""); };

  return (
    <div>
      {/* ── Hero + barre de recherche ── */}
      <section className="hero">
        <div className="hero-inner">
          <h1 className="hero-title">
            Trouvez le <span className="hero-accent">meilleur prix</span><br />
            au Maroc et à l'international
          </h1>
          <p className="hero-sub">
            Comparaison en temps réel sur Jumia, Avito et eBay
          </p>

          {/* Barre de recherche */}
          <form onSubmit={handleSubmit} className="hero-form">
            <div className="hero-search">
              <span className="hero-search-icon">🔍</span>
              <input
                className="hero-input"
                placeholder="iPhone 15, HP laptop, Redmi Note 14..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={status === "loading"}
              />
              <button
                type="submit"
                className="hero-btn"
                disabled={status === "loading" || !input.trim() || !selected.length || !user}
              >
                {status === "loading" ? "..." : "Analyser"}
              </button>
            </div>

            <div className="hero-platforms">
              {PLATFORMS.map((p) => (
                <label key={p.id} className={`platform-chip ${selected.includes(p.id) ? "active" : ""}`}>
                  <input type="checkbox" hidden checked={selected.includes(p.id)} onChange={() => toggle(p.id)} />
                  {p.label}
                </label>
              ))}
            </div>
          </form>

          {/* Bannière si non connecté */}
          {!user && (
            <div className="guest-banner">
              <span>🔒 Créez un compte pour lancer une recherche et analyser les prix</span>
              <a href="/login" className="guest-cta">Connexion / Inscription →</a>
            </div>
          )}
        </div>
      </section>

      <div className="page-content">

        {/* ── Mode résultats ── */}
        {searched && (
          <>
            {/* Progression */}
            {status === "loading" && (
              <div className="progress-bar-wrap">
                <div className="progress-bar-header">
                  <span>{message || "Collecte en cours..."}</span>
                  <strong>{progress}%</strong>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
              </div>
            )}

            {status === "error" && (
              <div className="error-banner">⚠ {error}</div>
            )}

            {status === "done" && (
              <>
                {/* Analyse Data Mining */}
                <AnalysePanel produits={resultsFiltered} analyse={analyse} query={query} />

                {/* Actions */}
                <div className="results-toolbar">
                  <div className="results-info">
                    <strong>{resultsFiltered.length}</strong> résultat(s) pour «&nbsp;{query}&nbsp;»
                    {scraped.length > resultsFiltered.length && (
                      <span className="filtered-note"> · {scraped.length - resultsFiltered.length} accessoires exclus</span>
                    )}
                  </div>
                  <div className="results-actions">
                    <button onClick={() => exportCSV(query).then((r) => downloadBlob(r.data, `${query}.csv`))} className="toolbar-btn">⬇ CSV</button>
                    <button onClick={() => exportPDF(query).then((r) => downloadBlob(r.data, `${query}.pdf`))} className="toolbar-btn">⬇ PDF</button>
                    <button onClick={handleReset} className="toolbar-btn">✕ Effacer</button>
                  </div>
                </div>

                {resultsFiltered.length > 0 ? (
                  <div className="products-grid">
                    {resultsFiltered.map((p) => (
                      <ProductCard key={p.id} produit={p} />
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    Aucun résultat exact pour «&nbsp;{query}&nbsp;».<br />
                    <small>Essayez un terme plus court ("iphone" au lieu de "iphone 15 pro max").</small>
                  </div>
                )}
              </>
            )}
          </>
        )}

        {/* ── Mode accueil : catalogue ── */}
        {!searched && (
          <>
            <div className="section-header">
              <h2 className="section-title">Sélection aléatoire</h2>
              <span className="section-count">
                {loadingCat ? "..." : `${catalog.length} produits`}
              </span>
            </div>

            {loadingCat && (
              <div className="skeleton-grid">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="skeleton-card" />
                ))}
              </div>
            )}

            {!loadingCat && catalog.length === 0 && (
              <div className="empty-state">
                Aucun produit en base — le catalogue automatique va se remplir après les prochains scrapings.
              </div>
            )}

            {!loadingCat && catalog.length > 0 && (
              <div className="products-grid">
                {catalog.map((p) => (
                  <ProductCard key={p.id} produit={p} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
