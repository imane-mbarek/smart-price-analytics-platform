// src/components/ProductCard.jsx
import usePanier from "../hooks/usePanier";
import useAuth   from "../hooks/useAuth";

// Fallback uniquement si aucune image réelle disponible
const FALLBACK = {
  telephones: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80",
  laptops:    "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80",
  default:    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80",
};

const PLATFORM_STYLE = {
  Jumia: { bg: "#FFF7ED", color: "#EA580C", dot: "#F97316" },
  Avito: { bg: "#FEF2F2", color: "#DC2626", dot: "#EF4444" },
  eBay:  { bg: "#F5F3FF", color: "#7C3AED", dot: "#8B5CF6" },
};

const fmt = (v) =>
  v?.toLocaleString("fr-MA", { style: "currency", currency: "MAD", maximumFractionDigits: 0 }) ?? "—";

export default function ProductCard({ produit }) {
  const { user } = useAuth();
  const panier   = usePanier();
  const { ajouter, retirer, estDansPanier } = panier || {};
  const dedans = estDansPanier?.(produit.id) ?? false;
  const style  = PLATFORM_STYLE[produit.plateforme] || PLATFORM_STYLE.Jumia;

  // Utiliser la vraie image scraped, sinon fallback par catégorie
  const imgSrc = produit.image || FALLBACK[produit.categorie] || FALLBACK.default;

  const togglePanier = async (e) => {
    e.preventDefault();
    if (!ajouter || !retirer) return;
    try {
      dedans ? await retirer(produit.id) : await ajouter(produit.id);
    } catch {
      // La session peut expirer entre l'affichage du bouton et le clic.
    }
  };

  const handleImgError = (e) => {
    // Si l'image réelle est cassée → fallback catégorie
    e.target.src = FALLBACK[produit.categorie] || FALLBACK.default;
    e.target.onerror = null; // éviter boucle infinie
  };

  return (
    <div className="pcard">
      {/* Image */}
      <div className="pcard-img">
        <img
          src={imgSrc}
          alt={produit.nom}
          onError={handleImgError}
          loading="lazy"
        />

        {/* Badge plateforme */}
        <span className="pcard-platform" style={{ background: style.bg, color: style.color }}>
          <span className="pcard-dot" style={{ background: style.dot }} />
          {produit.plateforme}
        </span>

        {/* Badge catégorie */}
        {produit.categorie && produit.categorie !== "non_specifie" && (
          <span className="pcard-cat">
            {produit.categorie === "telephones" ? "📱" : "💻"}
          </span>
        )}
      </div>

      {/* Body */}
      <div className="pcard-body">
        <p className="pcard-nom">{produit.nom}</p>
        {produit.description && (
          <p className="pcard-desc">
            {produit.description.replace(/Catégorie : \w+\s?\|?\s?/g, "").slice(0, 80)}
          </p>
        )}

        <div className="pcard-footer">
          <span className="pcard-prix">{fmt(produit.prix)}</span>

          <div className="pcard-actions">
            {produit.url && (
              <a
                href={produit.url}
                target="_blank"
                rel="noopener noreferrer"
                className="pcard-btn-link"
              >
                Voir →
              </a>
            )}
            {user && (
              <button
                className={`pcard-btn-cart ${dedans ? "pcard-btn-cart--active" : ""}`}
                onClick={togglePanier}
                title={dedans ? "Retirer du panier" : "Ajouter au panier"}
              >
                {dedans ? "🛒 ✓" : "🛒"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
