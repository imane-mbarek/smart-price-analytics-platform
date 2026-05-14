// src/components/AnalysePanel.jsx
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  ComposedChart, Cell, ScatterChart, Scatter, LineChart, Line,
} from "recharts";

const PLATFORM_COLORS = { Jumia: "#F97316", Avito: "#EF4444", eBay: "#8B5CF6" };
const RANGE_COLORS = { bas: "#10b981", milieu: "#6366f1", haut: "#f59e0b" };
const ALERT_COLORS = { vert: "#10b981", orange: "#f59e0b", rouge: "#ef4444" };

const money = (v) => v != null && !Number.isNaN(Number(v)) ? `${Math.round(Number(v))} MAD` : "-";
const num = (v, digits = 2) => v != null && !Number.isNaN(Number(v)) ? Number(v).toFixed(digits) : "-";

function normalizeStats(analyse, produits) {
  const stats = analyse?.stats || {};
  const prices = produits.map((p) => Number(p.prix)).filter((p) => Number.isFinite(p)).sort((a, b) => a - b);
  const n = prices.length;
  const mean = n ? prices.reduce((a, b) => a + b, 0) / n : null;
  const median = n ? prices[Math.floor(n / 2)] : null;

  return {
    count: stats.count ?? stats.total ?? n,
    min: stats.min ?? prices[0],
    max: stats.max ?? prices[n - 1],
    mean: stats.mean ?? stats.moyenne ?? mean,
    median: stats.median ?? stats.mediane ?? median,
    std: stats.std ?? stats.ecart_type,
    variance: stats.variance,
    q1: stats.q1,
    q3: stats.q3,
    iqr: stats.iqr,
  };
}

function Histogram({ produits }) {
  const prices = produits.map((p) => Number(p.prix)).filter((p) => Number.isFinite(p));
  if (!prices.length) return null;

  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const step = (max - min) / 8 || 1;
  const bins = Array.from({ length: 8 }, (_, i) => ({
    range: `${Math.round(min + i * step)}-${Math.round(min + (i + 1) * step)}`,
    count: 0,
  }));
  prices.forEach((p) => {
    const index = Math.min(Math.floor((p - min) / step), 7);
    bins[index].count += 1;
  });

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">Distribution des prix</h4>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={bins} margin={{ bottom: 38, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="range" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" interval={0} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${v} offre(s)`, ""]} />
          <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function PlatformChart({ produits, analyse }) {
  const distribution = analyse?.stats?.distribution_plateforme;
  const data = distribution
    ? Object.entries(distribution).map(([pl, count]) => ({ pl, count }))
    : Object.entries(produits.reduce((acc, p) => {
        const key = p.plateforme || "Inconnu";
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      }, {})).map(([pl, count]) => ({ pl, count }));

  if (!data.length) return null;

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">Distribution par plateforme</h4>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="pl" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${v} offre(s)`, ""]} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((d) => <Cell key={d.pl} fill={PLATFORM_COLORS[d.pl] || "#6B7280"} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function Stats({ analyse, produits }) {
  const s = normalizeStats(analyse, produits);
  const items = [
    { label: "Offres", value: s.count, accent: "#0ea5e9" },
    { label: "Minimum", value: money(s.min), accent: "#10b981" },
    { label: "Moyenne", value: money(s.mean), accent: "#38bdf8" },
    { label: "Mediane", value: money(s.median), accent: "#6366f1" },
    { label: "Maximum", value: money(s.max), accent: "#ef4444" },
    { label: "Ecart-type", value: money(s.std), accent: "#f59e0b" },
    { label: "Variance", value: num(s.variance, 0), accent: "#8b5cf6" },
    { label: "Q1", value: money(s.q1), accent: "#14b8a6" },
    { label: "Q3", value: money(s.q3), accent: "#fb7185" },
    { label: "IQR", value: money(s.iqr), accent: "#eab308" },
  ];

  return (
    <div className="stats-row stats-row-wide">
      {items.map((item) => (
        <div key={item.label} className="stat-pill" style={{ borderTopColor: item.accent }}>
          <span className="stat-pill-val">{item.value}</span>
          <span className="stat-pill-lbl">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

function Metadata({ analyse }) {
  const metadata = analyse?.metadata;
  if (!metadata) return null;

  return (
    <div className="analyse-card analyse-card-compact">
      <h4 className="analyse-title">Pipeline & nettoyage</h4>
      <div className="metadata-grid">
        <span>Lignes brutes <strong>{metadata.rows ?? "-"}</strong></span>
        <span>Lignes propres <strong>{metadata.clean_rows ?? "-"}</strong></span>
        <span>Features <strong>{metadata.features?.length || 0}</strong></span>
      </div>
      {!!metadata.features?.length && (
        <div className="feature-list">
          {metadata.features.map((feature) => <span key={feature}>{feature}</span>)}
        </div>
      )}
    </div>
  );
}

function KmeansPanel({ analyse }) {
  const centroids = analyse?.clusters?.reduce((acc, item) => {
    const key = item.cluster;
    if (!acc[key]) acc[key] = { cluster: key, gamme: item.gamme, count: 0, sum: 0 };
    acc[key].count += 1;
    acc[key].sum += Number(item.prix || 0);
    return acc;
  }, {});

  const data = Object.values(centroids || {}).map((item) => ({
    ...item,
    prix_moyen: item.count ? item.sum / item.count : 0,
  }));

  if (!data.length) return null;

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">K-Means : gammes de prix</h4>
      <div className="clusters-row">
        {data.map((c) => (
          <div key={c.cluster} className="cluster-pill" style={{ borderColor: RANGE_COLORS[c.gamme] || "#6B7280" }}>
            <span className="cluster-label" style={{ color: RANGE_COLORS[c.gamme] || "#94a3b8" }}>
              Cluster {c.cluster} - {c.gamme}
            </span>
            <span className="cluster-prix">{money(c.prix_moyen)}</span>
            <span className="cluster-count">{c.count} offres</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function DbscanPanel({ analyse }) {
  const dbscan = analyse?.dbscan || [];
  if (!dbscan.length) return null;

  const groups = dbscan.reduce((acc, item) => {
    const key = item.is_noise ? "Bruit" : `Cluster ${item.cluster}`;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const data = Object.entries(groups).map(([name, count]) => ({ name, count }));

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">DBSCAN : groupes et bruit</h4>
      <ResponsiveContainer width="100%" height={210}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${v} offre(s)`, ""]} />
          <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function PcaPanel({ analyse }) {
  const data = analyse?.pca || [];
  if (!data.length) return null;

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">PCA : projection 2D</h4>
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart margin={{ top: 12, right: 18, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="x" name="x" tick={{ fontSize: 11 }} />
          <YAxis type="number" dataKey="y" name="y" tick={{ fontSize: 11 }} />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            formatter={(value, name) => [name === "prix" ? money(value) : num(value), name]}
            labelFormatter={(_, payload) => payload?.[0]?.payload?.nom || ""}
          />
          <Scatter data={data}>
            {data.map((point, index) => (
              <Cell key={`${point.offre_id}-${index}`} fill={RANGE_COLORS[point.gamme] || "#818cf8"} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

function ElbowPanel({ analyse }) {
  const elbow = analyse?.clusters_meta?.elbow || analyse?.kmeans?.elbow || [];
  if (!elbow.length) return null;

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">Elbow K-Means</h4>
      <ResponsiveContainer width="100%" height={210}>
        <LineChart data={elbow}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="k" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(value) => [num(value), "Inertie"]} />
          <Line type="monotone" dataKey="inertia" stroke="#818cf8" strokeWidth={2} dot />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function AnomaliesPanel({ analyse }) {
  const anomalies = analyse?.anomalies || [];
  if (!anomalies.length) return null;

  const counts = anomalies.reduce((acc, item) => {
    acc[item.niveau] = (acc[item.niveau] || 0) + 1;
    return acc;
  }, {});
  const suspectRows = anomalies.filter((item) => item.niveau !== "vert").slice(0, 8);

  return (
    <div className="analyse-card analyse-card-wide">
      <h4 className="analyse-title">Anomalies : Isolation Forest + LOF</h4>
      <div className="anomaly-summary">
        {["vert", "orange", "rouge"].map((level) => (
          <span key={level} style={{ borderColor: ALERT_COLORS[level] }}>
            <b style={{ color: ALERT_COLORS[level] }}>{counts[level] || 0}</b> {level}
          </span>
        ))}
      </div>
      {suspectRows.length > 0 && (
        <div className="analyse-table-wrap">
          <table className="analyse-table">
            <thead>
              <tr>
                <th>Produit</th>
                <th>Prix</th>
                <th>Niveau</th>
                <th>IF</th>
                <th>LOF</th>
              </tr>
            </thead>
            <tbody>
              {suspectRows.map((item) => (
                <tr key={item.offre_id}>
                  <td>{item.nom}</td>
                  <td>{money(item.prix)}</td>
                  <td><span className={`alert-badge alert-${item.niveau}`}>{item.niveau}</span></td>
                  <td>{item.anomalie_iso ? "oui" : "non"}</td>
                  <td>{item.anomalie_lof ? "oui" : "non"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function RulesPanel({ analyse }) {
  const rules = analyse?.rules || [];
  if (!rules.length) return null;

  return (
    <div className="analyse-card analyse-card-wide">
      <h4 className="analyse-title">Regles d'association</h4>
      <div className="analyse-table-wrap">
        <table className="analyse-table">
          <thead>
            <tr>
              <th>Condition</th>
              <th>Conclusion</th>
              <th>Support</th>
              <th>Confiance</th>
            </tr>
          </thead>
          <tbody>
            {rules.slice(0, 10).map((rule, index) => (
              <tr key={index}>
                <td>{rule.antecedent || rule.antecedents || "-"}</td>
                <td>{rule.consequent || rule.consequents || "-"}</td>
                <td>{num(rule.support, 3)}</td>
                <td>{num(rule.confidence, 3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function EnrichedProducts({ analyse }) {
  const clusters = analyse?.clusters || [];
  const anomaliesById = Object.fromEntries((analyse?.anomalies || []).map((item) => [item.offre_id, item]));
  if (!clusters.length) return null;

  return (
    <div className="analyse-card analyse-card-wide">
      <h4 className="analyse-title">Produits enrichis par le pipeline</h4>
      <div className="analyse-table-wrap">
        <table className="analyse-table">
          <thead>
            <tr>
              <th>Produit</th>
              <th>Plateforme</th>
              <th>Prix</th>
              <th>Gamme</th>
              <th>Cluster</th>
              <th>Alerte</th>
            </tr>
          </thead>
          <tbody>
            {clusters.slice(0, 12).map((item) => {
              const anomaly = anomaliesById[item.offre_id];
              return (
                <tr key={item.offre_id}>
                  <td>{item.nom}</td>
                  <td>{item.plateforme}</td>
                  <td>{money(item.prix)}</td>
                  <td>{item.gamme}</td>
                  <td>{item.cluster}</td>
                  <td>{anomaly?.niveau || "-"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
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
          Analyse data mining - <em>{query}</em>
        </h2>
        <span className="analyse-count">{produits.length} offres collectees</span>
      </div>

      <Stats produits={produits} analyse={analyse} />
      {analyse && <Metadata analyse={analyse} />}

      <div className="analyse-charts">
        <Histogram produits={produits} />
        <PlatformChart produits={produits} analyse={analyse} />
        {analyse && <KmeansPanel analyse={analyse} />}
        {analyse && <DbscanPanel analyse={analyse} />}
        {analyse && <PcaPanel analyse={analyse} />}
        {analyse && <ElbowPanel analyse={analyse} />}
        {analyse && <AnomaliesPanel analyse={analyse} />}
        {analyse && <RulesPanel analyse={analyse} />}
        {analyse && <EnrichedProducts analyse={analyse} />}
      </div>
    </section>
  );
}
