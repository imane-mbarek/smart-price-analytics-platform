// src/App.jsx
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import { AuthProvider }          from "./hooks/useAuth";
import { PanierProvider }        from "./hooks/usePanier";
import { NotificationsProvider } from "./hooks/useNotifications";
import useAuth          from "./hooks/useAuth";
import usePanier        from "./hooks/usePanier";
import useNotifications from "./hooks/useNotifications";
import HomePage           from "./pages/HomePage";
import HistoryPage        from "./pages/HistoryPage";
import LoginPage          from "./pages/LoginPage";
import PanierPage         from "./pages/PanierPage";
import NotificationsPage  from "./pages/NotificationsPage";
import "./index.css";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <nav className="navbar">
      <Link to="/" className="nav-logo">📊 Smart Price Analytics</Link>
      <div className="nav-links">
        <Link to="/"        className="nav-link">Recherche</Link>
        <Link to="/history" className="nav-link">Historique</Link>
        {user
          ? <><span className="muted">👤 {user.username}</span>
              <button className="btn-sm" onClick={() => { logout(); navigate("/login"); }}>Déconnexion</button></>
          : <Link to="/login" className="btn-sm">Connexion</Link>
        }
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <main className="main">
          <Routes>
            <Route path="/"        element={<HomePage />}    />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/login"   element={<LoginPage />}   />
          </Routes>
        </main>
      </BrowserRouter>
    </AuthProvider>
  );
}
