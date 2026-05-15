// src/components/AnalysePanel.jsx
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  Cell, ScatterChart, Scatter, LineChart, Line,
} from "recharts";

const PLATFORM_COLORS = { Jumia: "#F97316", Avito: "#EF4444" };
const RANGE_COLORS = { bas: "#10b981", milieu: "#6366f1", haut: "#f59e0b" };
const ALERT_COLORS = { vert: "#10b981", orange: "#f59e0b", rouge: "#ef4444" };

const money = (v) => v != null && !Number.isNaN(Number(v)) ? `${Math.round(Number(v))} MAD` : "-";
const num = (v, digits = 2) => v != null && !Number.isNaN(Number(v)) ? Number(v).toFixed(digits) : "-";

function countBy(list, getKey) {
  return list.reduce((acc, item) => {
    const key = getKey(item) || "Inconnu";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
}

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

function CategoryChart({ produits, analyse }) {
  const distribution = analyse?.stats?.distribution_categorie;
  const data = distribution
    ? Object.entries(distribution).map(([name, count]) => ({ name, count }))
    : Object.entries(countBy(produits, (p) => p.categorie)).map(([name, count]) => ({ name, count }));

  if (!data.length || (data.length === 1 && data[0].name === "Inconnu")) return null;

  return (
    <div className="analyse-card">
      <h4 className="analyse-title">Distribution par categorie</h4>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${v} offre(s)`, ""]} />
          <Bar dataKey="count" fill="#14b8a6" radius={[4, 4, 0, 0]} />
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

function ClientSummary({ analyse, produits }) {
  const s = normalizeStats(analyse, produits);
  const anomalies = analyse?.anomalies || [];
  const clusters = analyse?.clusters || [];
  const red = anomalies.filter((item) => item.niveau === "rouge").length;
  const orange = anomalies.filter((item) => item.niveau === "orange").length;
  const bestRange = clusters.filter((item) => item.gamme === "bas").length;
  const normalOffers = anomalies.filter((item) => item.niveau === "vert").length || produits.length - red - orange;

  const cards = [
    {
      label: "Prix conseille",
      value: money(s.median ?? s.mean),
      detail: "Reference robuste pour comparer les offres.",
      tone: "blue",
    },
    {
      label: "Offres abordables",
      value: bestRange,
      detail: "Produits classes dans la gamme basse par K-Means.",
      tone: "green",
    },
    {
      label: "Prix a verifier",
      value: orange + red,
      detail: `${red} alerte rouge, ${orange} alerte orange.`,
      tone: red ? "red" : "orange",
    },
    {
      label: "Offres normales",
      value: Math.max(normalOffers, 0),
      detail: "Non signalees par les detecteurs d'anomalies.",
      tone: "slate",
    },
  ];

  return (
    <div className="client-summary">
      {cards.map((card) => (
        <div key={card.label} className={`summary-tile summary-${card.tone}`}>
          <span className="summary-label">{card.label}</span>
          <strong>{card.value}</strong>
          <small>{card.detail}</small>
        </div>
      ))}
    </div>
  );
}

function WorkflowPanel({ analyse, produits }) {
  const metadata = analyse?.metadata || {};
  const modules = [
    {
      step: "01",
      title: "Nettoyage",
      text: "Doublons, prix vides, noms manquants et prix invalides sont retires avant l'analyse.",
      value: metadata.clean_rows != null ? `${metadata.clean_rows} lignes propres` : `${produits.length} offres`,
    },
    {
      step: "02",
      title: "Normalisation",
      text: "Les devises sont ramenees en MAD, puis les prix et variables utiles sont standardises.",
      value: `${metadata.features?.length || 0} features`,
    },
    {
      step: "03",
      title: "Statistiques",
      text: "Min, max, moyenne, mediane, quartiles, variance et repartition par plateforme.",
      value: analyse?.stats ? "calculees" : "fallback local",
    },
    {
      step: "04",
      title: "Clustering",
      text: "K-Means separe les offres en bas, milieu et haut de gamme; DBSCAN isole les groupes denses.",
      value: `${analyse?.clusters?.length || 0} labels`,
    },
    {
      step: "05",
      title: "Anomalies",
      text: "Isolation Forest et LOF donnent un niveau vert, orange ou rouge pour chaque offre.",
      value: `${analyse?.anomalies?.length || 0} scores`,
    },
    {
      step: "06",
      title: "Associations",
      text: "Les regles expliquent les liens entre plateforme, marque, etat, categorie et tranche de prix.",
      value: `${analyse?.rules?.length || 0} regles`,
    },
  ];

  return (
    <div className="workflow-grid">
      {modules.map((module) => (
        <div key={module.step} className="workflow-card">
          <span className="workflow-step">{module.step}</span>
          <div>
            <h4>{module.title}</h4>
            <p>{module.text}</p>
            <strong>{module.value}</strong>
          </div>
        </div>
      ))}
    </div>
  );
}

function RecommendedOffers({ produits, analyse }) {
  const clustersById = Object.fromEntries((analyse?.clusters || []).map((item) => [item.offre_id, item]));
  const anomaliesById = Object.fromEntries((analyse?.anomalies || []).map((item) => [item.offre_id, item]));
  const median = analyse?.stats?.median;

  const rows = produits
    .map((produit) => {
      const cluster = clustersById[produit.id] || {};
      const anomaly = anomaliesById[produit.id] || {};
      const price = Number(produit.prix);
      const score = (cluster.gamme === "bas" ? 2 : cluster.gamme === "milieu" ? 1 : 0)
        + (anomaly.niveau === "vert" ? 2 : anomaly.niveau === "orange" ? 1 : 0)
        - (median && price > median ? 1 : 0);

      return {
        ...produit,
        gamme: cluster.gamme || "-",
        niveau: anomaly.niveau || "vert",
        ecart: median && Number.isFinite(price) ? Math.round(((price - median) / median) * 100) : null,
        score,
      };
    })
    .sort((a, b) => b.score - a.score || Number(a.prix) - Number(b.prix))
    .slice(0, 5);

  if (!rows.length) return null;

  return (
    <div className="analyse-card analyse-card-wide recommendation-card">
      <h4 className="analyse-title">Meilleures options pour le client</h4>
      <div className="recommendation-list">
        {rows.map((row, index) => (
          <div key={row.id || row.nom} className="recommendation-row">
            <span className="recommendation-rank">#{index + 1}</span>
            <div className="recommendation-main">
              <strong>{row.nom}</strong>
              <small>{row.plateforme} - {row.gamme} - {row.ecart == null ? "prix compare" : `${row.ecart <= 0 ? "" : "+"}${row.ecart}% vs marche`}</small>
            </div>
            <span className={`alert-badge alert-${row.niveau}`}>{row.niveau}</span>
            <b>{money(row.prix)}</b>
          </div>
        ))}
      </div>
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
        <span>Devise cible <strong>MAD</strong></span>
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
  const apiCentroids = analyse?.kmeans?.centroids || [];
  const centroids = analyse?.clusters?.reduce((acc, item) => {
    const key = item.cluster;
    if (!acc[key]) acc[key] = { cluster: key, gamme: item.gamme, count: 0, sum: 0 };
    acc[key].count += 1;
    acc[key].sum += Number(item.prix || 0);
    return acc;
  }, {});

  const data = apiCentroids.length
    ? apiCentroids.map((item) => ({
        ...item,
        count: analyse?.clusters?.filter((cluster) => cluster.cluster === item.cluster).length || 0,
      }))
    : Object.values(centroids || {}).map((item) => ({
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
  const clusterMeta = Object.fromEntries((analyse?.clusters || []).map((item) => [item.offre_id, item]));

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
            {data.map((point, index) => {
              const gamme = point.gamme || clusterMeta[point.offre_id]?.gamme;
              return <Cell key={`${point.offre_id}-${index}`} fill={RANGE_COLORS[gamme] || "#818cf8"} />;
            })}
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

function DecisionGuide({ analyse }) {
  if (!analyse) return null;

  return (
    <div className="analyse-card analyse-card-wide decision-guide">
      <h4 className="analyse-title">Lecture rapide pour le client</h4>
      <div className="decision-grid">
        <div>
          <span className="decision-dot decision-green" />
          <strong>Vert</strong>
          <p>Prix coherent avec le marche observe.</p>
        </div>
        <div>
          <span className="decision-dot decision-orange" />
          <strong>Orange</strong>
          <p>Un algorithme trouve le prix atypique: comparer vendeur, etat et fiche produit.</p>
        </div>
        <div>
          <span className="decision-dot decision-red" />
          <strong>Rouge</strong>
          <p>Isolation Forest et LOF signalent le prix: risque eleve d'offre douteuse.</p>
        </div>
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
          Tableau d'aide a la decision - <em>{query}</em>
        </h2>
        <span className="analyse-count">{produits.length} offres collectees</span>
      </div>

      <ClientSummary produits={produits} analyse={analyse} />
      {analyse && <RecommendedOffers produits={produits} analyse={analyse} />}
      <WorkflowPanel produits={produits} analyse={analyse} />
      <Stats produits={produits} analyse={analyse} />
      {analyse && <Metadata analyse={analyse} />}

      <div className="analyse-charts">
        <Histogram produits={produits} />
        <PlatformChart produits={produits} analyse={analyse} />
        <CategoryChart produits={produits} analyse={analyse} />
        {analyse && <KmeansPanel analyse={analyse} />}
        {analyse && <DbscanPanel analyse={analyse} />}
        {analyse && <PcaPanel analyse={analyse} />}
        {analyse && <ElbowPanel analyse={analyse} />}
        {analyse && <AnomaliesPanel analyse={analyse} />}
        {analyse && <RulesPanel analyse={analyse} />}
        {analyse && <EnrichedProducts analyse={analyse} />}
        {analyse && <DecisionGuide analyse={analyse} />}
      </div>
    </section>
  );
}
