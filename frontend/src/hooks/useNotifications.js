// src/hooks/useNotifications.js
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { getNonLues, getNotifications, marquerLue, toutMarquerLu } from "../services/api";
import useAuth from "./useAuth";

const NotifCtx = createContext(null);

export function NotificationsProvider({ children }) {
  const { user }   = useAuth();
  const [notifs,   setNotifs]   = useState([]);
  const [nonLues,  setNonLues]  = useState(0);

  const charger = useCallback(async () => {
    if (!user) { setNotifs([]); setNonLues(0); return; }
    try {
      const { data } = await getNotifications();
      setNotifs(data);
      setNonLues(data.filter((n) => !n.lue).length);
    } catch {
      setNotifs([]); setNonLues(0);
    }
  }, [user]);

  // Chargement initial + polling toutes les 30s
  useEffect(() => {
    charger();
    const interval = setInterval(charger, 30_000);
    return () => clearInterval(interval);
  }, [charger]);

  const lire = async (id) => {
    await marquerLue(id);
    setNotifs((prev) => prev.map((n) => n.id === id ? { ...n, lue: true } : n));
    setNonLues((c) => Math.max(0, c - 1));
  };

  const toutLire = async () => {
    await toutMarquerLu();
    setNotifs((prev) => prev.map((n) => ({ ...n, lue: true })));
    setNonLues(0);
  };

  return (
    <NotifCtx.Provider value={{ notifs, nonLues, lire, toutLire, charger }}>
      {children}
    </NotifCtx.Provider>
  );
}

export default function useNotifications() { return useContext(NotifCtx); }
