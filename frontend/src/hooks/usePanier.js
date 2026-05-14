// src/hooks/usePanier.js
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { getPanier, getPanierCount, ajouterAuPanier, retirerDuPanier } from "../services/api";
import useAuth from "./useAuth";

const PanierCtx = createContext(null);

export function PanierProvider({ children }) {
  const { user } = useAuth();
  const [items,  setItems]  = useState([]);
  const [count,  setCount]  = useState(0);
  const [ids,    setIds]    = useState(new Set()); // Set des produit.id dans le panier

  const charger = useCallback(async () => {
    if (!user) { setItems([]); setCount(0); setIds(new Set()); return; }
    try {
      const { data } = await getPanier();
      setItems(data);
      setCount(data.length);
      setIds(new Set(data.map((i) => i.produit)));
    } catch {
      setItems([]); setCount(0); setIds(new Set());
    }
  }, [user]);

  // Recharger quand l'utilisateur change
  useEffect(() => { charger(); }, [charger]);

  const ajouter = async (produitId) => {
    await ajouterAuPanier(produitId);
    setIds((prev) => new Set([...prev, produitId]));
    setCount((c) => c + 1);
    charger(); // sync complet
  };

  const retirer = async (produitId) => {
    await retirerDuPanier(produitId);
    setIds((prev) => { const s = new Set(prev); s.delete(produitId); return s; });
    setCount((c) => Math.max(0, c - 1));
    charger();
  };

  const estDansPanier = (produitId) => ids.has(produitId);

  return (
    <PanierCtx.Provider value={{ items, count, ajouter, retirer, estDansPanier, charger }}>
      {children}
    </PanierCtx.Provider>
  );
}

export default function usePanier() { return useContext(PanierCtx); }
