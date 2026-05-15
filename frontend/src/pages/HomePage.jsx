// src/pages/HomePage.jsx
import { useState, useEffect, useMemo } from "react";
import { Link, useLocation } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import useSearch from "../hooks/useSearch";
import { getAccueilProduits, exportCSV, exportPDF } from "../services/api";
import ProductCard from "../components/ProductCard";
import AnalysePanel from "../components/AnalysePanel";

const PLATFORMS = [
  { id: "jumia", label: "Jumia.ma" },
  { id: "avito", label: "Avito.ma" },
];

const MOTS_PARASITES = [
  "coque", "etui", "housse", "protection", "verre", "film",
  "chargeur", "cable", "adaptateur", "ecouteurs", "airpods",
  "casque", "batterie", "accessoire", "kit", "pack", "compatible",
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

function buildInsights(analyse, produits) {
  const clusters = Object.fromEntries((analyse?.clusters || []).map((item) => [item.offre_id, item]));
  const anomalies = Object.fromEntries((analyse?.anomalies || []).map((item) => [item.offre_id, item]));
  const median = analyse?.stats?.median;

  return Object.fromEntries(
    produits.map((produit) => {
      const cluster = clusters[produit.id] || {};
      const anomaly = anomalies[produit.id] || {};
      const price = Number(produit.prix);
      const ecartMedian = median && Number.isFinite(price)
        ? Math.round(((price - median) / median) * 100)
        : null;

      return [produit.id, { gamme: cluster.gamme, niveau: anomaly.niveau, ecartMedian }];
    })
  );
}

export default function HomePage() {
  const { user } = useAuth();
  const location = useLocation();

  const [catalog, setCatalog] = useState([]);
  const [loadingCat, setLoadingCat] = useState(true);
  const [input, setInput] = useState(location.state?.query || "");
  const [selected, setSelected] = useState(["jumia", "avito"]);
  const [searched, setSearched] = useState(false);
  const { status, progress, message, produits: scraped, analyse, error, query, search } = useSearch();

  useEffect(() => {
    getAccueilProduits(12)
      .then(({ data }) => setCatalog(data))
      .catch(() => setCatalog([]))
      .finally(() => setLoadingCat(false));
  }, []);

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

  const productInsights = useMemo(
    () => buildInsights(analyse, resultsFiltered),
    [analyse, resultsFiltered]
  );

  const toggle = (id) =>
    setSelected((p) => p.includes(id) ? p.filter((x) => x !== id) : [...p, id]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || !selected.length || !user) return;
    setSearched(true);
    search(input.trim(), selected);
  };

  const handleReset = () => {
    setSearched(false);
    setInput("");
  };

  return (
    <div>
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-kicker">Site de vente comparee et analyse de prix</div>
          <h1 className="hero-title">
            Achetez plus malin avec une <span className="hero-accent">analyse claire</span>
          </h1>
          <p className="hero-sub">
            Comparez les offres, detectez les prix suspects et choisissez le meilleur produit au bon moment.
          </p>

          <form onSubmit={handleSubmit} className="hero-form">
            <div className="hero-search">
              <span className="hero-search-icon">Search</span>
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
                {status === "loading" ? "Analyse..." : "Analyser"}
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

          <div className="hero-proof">
            <span>Prix en MAD</span>
            <span>Alertes anti-arnaque</span>
            <span>Gammes bas / moyen / premium</span>
          </div>

          {!user && (
            <div className="guest-banner">
              <span>Connectez-vous pour lancer une recherche et ajouter des produits au panier.</span>
              <Link to="/login" className="guest-cta">Connexion / inscription</Link>
            </div>
          )}
        </div>
      </section>

      <div className="page-content">
        {searched && (
          <>
            {status === "loading" && (
              <div className="progress-bar-wrap">
                <div className="progress-bar-header">
                  <span>{message || "Collecte des offres et analyse des prix..."}</span>
                  <strong>{progress}%</strong>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
              </div>
            )}

            {status === "error" && <div className="error-banner">{error}</div>}

            {status === "done" && (
              <>
                <AnalysePanel produits={resultsFiltered} analyse={analyse} query={query} />

                <div className="results-toolbar">
                  <div className="results-info">
                    <strong>{resultsFiltered.length}</strong> offres pour "{query}"
                    {scraped.length > resultsFiltered.length && (
                      <span className="filtered-note"> - {scraped.length - resultsFiltered.length} accessoires exclus</span>
                    )}
                  </div>
                  <div className="results-actions">
                    <button onClick={() => exportCSV(query).then((r) => downloadBlob(r.data, `${query}.csv`))} className="toolbar-btn">
                      Export CSV
                    </button>
                    <button onClick={() => exportPDF(query).then((r) => downloadBlob(r.data, `${query}.pdf`))} className="toolbar-btn">
                      Export PDF
                    </button>
                    <button onClick={handleReset} className="toolbar-btn">Effacer</button>
                  </div>
                </div>

                {resultsFiltered.length > 0 ? (
                  <div className="products-grid">
                    {resultsFiltered.map((p) => (
                      <ProductCard key={p.id} produit={p} insight={productInsights[p.id]} />
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    Aucun resultat exact pour "{query}".<br />
                    <small>Essayez un terme plus court, par exemple "iphone" au lieu de "iphone 15 pro max".</small>
                  </div>
                )}
              </>
            )}
          </>
        )}

        {!searched && (
          <>
            <div className="market-strip">
              <div>
                <strong>Acheter</strong>
                <span>Des cartes produits avec prix, plateforme et lien vendeur.</span>
              </div>
              <div>
                <strong>Comparer</strong>
                <span>Des statistiques simples pour voir le prix juste.</span>
              </div>
              <div>
                <strong>Verifier</strong>
                <span>Des alertes pour reperer les prix trop beaux pour etre vrais.</span>
              </div>
            </div>

            <div className="section-header">
              <h2 className="section-title">Produits disponibles</h2>
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
                Aucun produit en base. Le catalogue se remplit apres les prochaines recherches.
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
