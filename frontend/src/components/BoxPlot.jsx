// src/components/BoxPlot.jsx
import { ComposedChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Cell } from "recharts";

const COLORS = { jumia: "#F97316", Jumia: "#F97316", avito: "#EF4444", Avito: "#EF4444", ebay: "#8B5CF6", eBay: "#8B5CF6" };

function stats(produits) {
  const g = {};
  produits.forEach((p) => { if (!g[p.plateforme]) g[p.plateforme] = []; if (p.prix) g[p.plateforme].push(p.prix); });
  return Object.entries(g).map(([pl, prices]) => {
    prices.sort((a, b) => a - b);
    const n = prices.length;
    return {
      pl,
      min: Math.round(prices[0]),
      max: Math.round(prices[n - 1]),
      med: Math.round(prices[Math.floor(n / 2)]),
      base: Math.round(prices[0]),
      range: Math.round(prices[n - 1] - prices[0]),
      n,
    };
  });
}

const Tip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div className="tooltip">
      <strong>{d.pl}</strong>
      <p>Min : {d.min} MAD</p><p>Médiane : {d.med} MAD</p><p>Max : {d.max} MAD</p><p>{d.n} offres</p>
    </div>
  );
};

export default function BoxPlot({ produits }) {
  const data = stats(produits);
  if (!data.length) return null;
  return (
    <div className="chart-card">
      <h3 className="chart-title">Comparaison par plateforme</h3>
      <ResponsiveContainer width="100%" height={240}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="pl" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 11 }} unit=" MAD" width={75} />
          <Tooltip content={<Tip />} />
          <Bar dataKey="base"  stackId="b" fill="transparent" />
          <Bar dataKey="range" stackId="b" radius={[4, 4, 0, 0]}>
            {data.map((d) => <Cell key={d.pl} fill={COLORS[d.pl] || "#6B7280"} fillOpacity={0.8} />)}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
      <p className="note">Barre = plage de prix min → max par plateforme</p>
    </div>
  );
}
