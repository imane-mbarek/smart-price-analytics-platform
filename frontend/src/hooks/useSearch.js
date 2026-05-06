import { useState, useRef, useEffect } from "react";
import { lancerRecherche, getProgression, getAnalyse } from "../services/api";

export default function useSearch() {
  const [status,   setStatus]   = useState("idle");
  const [progress, setProgress] = useState(0);
  const [message,  setMessage]  = useState("");
  const [produits, setProduits] = useState([]);
  const [analyse,  setAnalyse]  = useState(null);
  const [error,    setError]    = useState("");
  const [query,    setQuery]    = useState("");
  const poll = useRef(null);

  const stop = () => { clearInterval(poll.current); poll.current = null; };
  useEffect(() => () => stop(), []);

  const search = async (q, plateformes) => {
    stop();
    setStatus("loading"); setProgress(0); setMessage("");
    setProduits([]); setAnalyse(null); setError(""); setQuery(q);

    try {
      const { data } = await lancerRecherche(q, plateformes);
      const taskId = data.task_id;

      poll.current = setInterval(async () => {
        try {
          const { data: p } = await getProgression(taskId);
          setProgress(p.progression ?? 0);
          setMessage(p.message ?? "");

          if (p.statut === "termine") {
            stop();
            setProduits(p.resultats || []);
            setStatus("done");
            // Lancer l'analyse Data Mining
            try {
              const { data: dm } = await getAnalyse(q);
              setAnalyse(dm);
            } catch { setAnalyse(null); }
          } else if (p.statut === "erreur") {
            stop(); setError(p.message || "Erreur scraping."); setStatus("error");
          }
        } catch { stop(); setError("Serveur inaccessible."); setStatus("error"); }
      }, 2000);

    } catch (e) {
      setError(e.response?.data?.error || "Erreur de lancement.");
      setStatus("error");
    }
  };

  return { status, progress, message, produits, analyse, error, query, search };
}
