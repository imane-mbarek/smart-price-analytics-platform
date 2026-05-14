// src/pages/LoginPage.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export default function LoginPage() {
  const [mode,    setMode]    = useState("login");
  const [form,    setForm]    = useState({ username: "", password: "", email: "" });
  const [error,   setError]   = useState("");
  const [loading, setLoading] = useState(false);
  const { login, register }   = useAuth();
  const navigate = useNavigate();

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      mode === "login"
        ? await login({ username: form.username, password: form.password })
        : await register(form);
      navigate("/");
    } catch (err) {
      const d = err.response?.data;
      setError(d?.detail || d?.username?.[0] || d?.password?.[0] || "Identifiants incorrects.");
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">📊</div>
        <h2 className="auth-title">
          {mode === "login" ? "Bon retour !" : "Créer un compte"}
        </h2>
        <p className="auth-sub">
          {mode === "login"
            ? "Connectez-vous pour analyser les prix"
            : "Rejoignez PriceHunt gratuitement"}
        </p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={onSubmit} className="auth-form">
          <div className="auth-field">
            <label>Nom d'utilisateur</label>
            <input name="username" type="text" value={form.username} onChange={onChange} required autoComplete="username" />
          </div>
          {mode === "register" && (
            <div className="auth-field">
              <label>Email</label>
              <input name="email" type="email" value={form.email} onChange={onChange} autoComplete="email" />
            </div>
          )}
          <div className="auth-field">
            <label>Mot de passe</label>
            <input name="password" type="password" value={form.password} onChange={onChange} required autoComplete={mode === "login" ? "current-password" : "new-password"} />
          </div>
          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? "Chargement..." : mode === "login" ? "Se connecter" : "S'inscrire"}
          </button>
        </form>

        <p className="auth-switch">
          {mode === "login" ? "Pas de compte ? " : "Déjà inscrit ? "}
          <button className="auth-link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "S'inscrire" : "Se connecter"}
          </button>
        </p>
      </div>
    </div>
  );
}
