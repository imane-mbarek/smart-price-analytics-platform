// src/components/PriceHistogram.jsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

function histogram(prices, bins = 8) {
  const min = Math.min(...prices), max = Math.max(...prices);
  const step = (max - min) / bins || 1;
  const b = Array.from({ length: bins }, (_, i) => ({
    range: `${Math.round(min + i * step)}–${Math.round(min + (i + 1) * step)}`,
    count: 0,
  }));
  prices.forEach((p) => { const i = Math.min(Math.floor((p - min) / step), bins - 1); b[i].count++; });
  return b;
}

export default function PriceHistogram({ produits }) {
  const prices = produits.map((p) => p.prix).filter(Boolean);
  if (!prices.length) return null;

  return (
    <div className="chart-card">
      <h3 className="chart-title">Distribution des prix</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={histogram(prices)} margin={{ bottom: 40, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="range" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" interval={0} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${v} offre(s)`, ""]} />
          <Bar dataKey="count" fill="#3B82F6" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
