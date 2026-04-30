// src/pages/LoginPage.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export default function LoginPage() {
  const [mode, setMode]     = useState("login");
  const [form, setForm]     = useState({ username: "", password: "", email: "" });
  const [error, setError]   = useState("");
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
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
      <div className="card" style={{ maxWidth: 380, width: "100%" }}>
        <h2 className="title">{mode === "login" ? "Connexion" : "Créer un compte"}</h2>
        {error && <div className="alert">{error}</div>}

        <form onSubmit={onSubmit} className="auth-form">
          <label className="field">Nom d'utilisateur
            <input name="username" type="text" value={form.username} onChange={onChange} required />
          </label>
          {mode === "register" && (
            <label className="field">Email
              <input name="email" type="email" value={form.email} onChange={onChange} />
            </label>
          )}
          <label className="field">Mot de passe
            <input name="password" type="password" value={form.password} onChange={onChange} required />
          </label>
          <button className="btn-primary" disabled={loading} style={{ marginTop: 4 }}>
            {loading ? "…" : mode === "login" ? "Se connecter" : "S'inscrire"}
          </button>
        </form>

        <p className="muted" style={{ textAlign: "center", marginTop: "1rem" }}>
          {mode === "login" ? "Pas de compte ? " : "Déjà inscrit ? "}
          <button className="link-btn" onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "S'inscrire" : "Se connecter"}
          </button>
        </p>
      </div>
    </div>
  );
}
