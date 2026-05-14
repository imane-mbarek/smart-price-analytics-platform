// src/components/AnalysePanel.jsx
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  ComposedChart, Cell,
} from "recharts";

const PLATFORM_COLORS = { Jumia: "#F97316", Avito: "#EF4444", eBay: "#8B5CF6" };
const fmt = (v) => v != null ? `${Math.round(v)} MAD` : "—";

// ── Histogramme distribution ─────────────────────────────────────────
function Histogram({ produits }) {
  const prices = produits.map((p) => p.prix).filter(Boolean);
  if (!prices.length) return null;
  const min = Math.min(...prices), max = Math.max(...prices);
  const step = (max - min) / 8 || 1;
  const bins = Array.from({ length: 8 }, (_, i) => ({
    range: `${Math.round(min + i * step)}–${Math.round(min + (i+1) * step)}`,
    count: 0,
  }));
  prices.forEach((p) => { const i = Math.min(Math.floor((p - min) / step), 7); bins[i].count++; });

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">Distribution des prix</h4>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={bins} margin={{ bottom: 36, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="range" tick={{ fontSize: 9 }} angle={-35} textAnchor="end" interval={0} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${v} offre(s)`, ""]} />
          <Bar dataKey="count" fill="#6366f1" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// ── Comparaison par plateforme ────────────────────────────────────────
function PlatformChart({ produits }) {
  const groups = {};
  produits.forEach((p) => {
    if (!groups[p.plateforme]) groups[p.plateforme] = [];
    if (p.prix) groups[p.plateforme].push(p.prix);
  });

  const data = Object.entries(groups).map(([pl, prices]) => {
    prices.sort((a, b) => a - b);
    const n = prices.length;
    return {
      pl, count: n,
      min: Math.round(prices[0]),
      max: Math.round(prices[n - 1]),
      base: Math.round(prices[0]),
      range: Math.round(prices[n - 1] - prices[0]),
      med: Math.round(prices[Math.floor(n / 2)]),
    };
  });

  if (!data.length) return null;

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">Prix par plateforme</h4>
      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="pl" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 11 }} unit=" MAD" width={80} />
          <Tooltip formatter={(v, n, p) => [fmt(p.payload.min) + " → " + fmt(p.payload.max), p.payload.pl]} />
          <Bar dataKey="base"  stackId="b" fill="transparent" />
          <Bar dataKey="range" stackId="b" radius={[4, 4, 0, 0]}>
            {data.map((d) => <Cell key={d.pl} fill={PLATFORM_COLORS[d.pl] || "#6B7280"} fillOpacity={0.85} />)}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

// ── Stats résumées ────────────────────────────────────────────────────
function Stats({ produits }) {
  const prices = produits.map((p) => p.prix).filter(Boolean).sort((a, b) => a - b);
  if (!prices.length) return null;
  const n      = prices.length;
  const mean   = prices.reduce((a, b) => a + b, 0) / n;
  const median = n % 2 ? prices[Math.floor(n / 2)] : (prices[n / 2 - 1] + prices[n / 2]) / 2;
  const std    = Math.sqrt(prices.reduce((a, b) => a + (b - mean) ** 2, 0) / n);

  const items = [
    { label: "Minimum",      value: fmt(prices[0]),          accent: "#10b981" },
    { label: "Médiane",      value: fmt(median),             accent: "#6366f1" },
    { label: "Maximum",      value: fmt(prices[n - 1]),      accent: "#ef4444" },
    { label: "Écart-type",   value: fmt(std),                accent: "#f59e0b" },
    { label: "Offres",       value: n,                       accent: "#0ea5e9" },
  ];

  return (
    <div className="stats-row">
      {items.map((s) => (
        <div key={s.label} className="stat-pill" style={{ borderTopColor: s.accent }}>
          <span className="stat-pill-val">{s.value}</span>
          <span className="stat-pill-lbl">{s.label}</span>
        </div>
      ))}
    </div>
  );
}

// ── Clusters (si dispo depuis /analyser/) ─────────────────────────────
function Clusters({ analyse }) {
  const clusters = analyse?.clusters || [];
  if (!clusters.length) return null;
  const labels = { 0: "Bas de gamme", 1: "Milieu de gamme", 2: "Haut de gamme" };
  const colors = { 0: "#10b981", 1: "#6366f1", 2: "#f59e0b" };

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">Segmentation par gamme</h4>
      <div className="clusters-row">
        {clusters.map((c) => (
          <div key={c.cluster_id} className="cluster-pill" style={{ borderColor: colors[c.cluster_id] || "#6B7280" }}>
            <span className="cluster-label" style={{ color: colors[c.cluster_id] }}>
              {labels[c.cluster_id] || `Cluster ${c.cluster_id}`}
            </span>
            <span className="cluster-prix">{fmt(c.avg_price)}</span>
            <span className="cluster-count">{c.count} offres</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AnalysePanel({ produits, analyse, query }) {
  if (!produits?.length) return null;

  return (
    <section className="analyse-section">
      <div className="analyse-header">
        <h2 className="analyse-main-title">
          Analyse des prix — <em>{query}</em>
        </h2>
        <span className="analyse-count">{produits.length} offres collectées</span>
      </div>

      <Stats produits={produits} />

      <div className="analyse-charts">
        <Histogram   produits={produits} />
        <PlatformChart produits={produits} />
      </div>

      {analyse && <Clusters analyse={analyse} />}
    </section>
  );
}
