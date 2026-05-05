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
  const { count }          = usePanier();
  const { nonLues }        = useNotifications();
  const navigate = useNavigate();
  return (
    <nav className="navbar">
      <Link to="/" className="nav-logo">📊 Smart Price Analytics</Link>

      <div className="nav-links">
        <Link to="/"        className="nav-link">Accueil</Link>
        <Link to="/history" className="nav-link">Historique</Link>

        {user && (
          <>
            {/* Panier avec badge */}
            <Link to="/panier" className="nav-icon-btn">
              🛒
              {count > 0 && <span className="nav-badge">{count}</span>}
            </Link>

            {/* Notifications avec badge */}
            <Link to="/notifications" className="nav-icon-btn">
              🔔
              {nonLues > 0 && <span className="nav-badge nav-badge-red">{nonLues}</span>}
            </Link>

            <span className="muted">👤 {user.username}</span>
            <button className="btn-sm" onClick={() => { logout(); navigate("/login"); }}>
              Déconnexion
            </button>
          </>
        )}

        {!user && <Link to="/login" className="btn-sm">Connexion</Link>}
      </div>
    </nav>
  );
}

// Les providers doivent être à l'intérieur de BrowserRouter pour useNavigate
function AppInner() {
  return (
    <>
      <Navbar />
      <main className="main">
        <Routes>
          <Route path="/"              element={<HomePage />}          />
          <Route path="/history"       element={<HistoryPage />}       />
          <Route path="/login"         element={<LoginPage />}         />
          <Route path="/panier"        element={<PanierPage />}        />
          <Route path="/notifications" element={<NotificationsPage />} />
        </Routes>
      </main>
    </>
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
