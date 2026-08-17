import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Menu, Package, ShoppingCart, Users, LogOut, ShieldCheck, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useConnection } from '../../hooks/useConnection'; // Import du hook réseau

const links = [
  { to: '/', label: 'Tableau de bord', icon: LayoutDashboard },
  { to: '/products', label: 'Produits', icon: Package },
  { to: '/sales', label: 'Ventes', icon: ShoppingCart },
  { to: '/customers', label: 'Clients', icon: Users },
  { to: '/tenants', label: 'Boutiques', icon: Users },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const isOnline = useConnection(); // État de la connexion en temps réel
  const navigate = useNavigate();
  const location = useLocation();
  
  const close = () => setOpen(false);
  const logoutUser = () => { logout(); navigate('/login'); };
  
  const linkClass = (to) => `flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 ${location.pathname === to ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100 hover:text-blue-700'}`;
  const navigationLinks = user?.is_superuser ? [...links, { to: '/admin', label: 'Administration', icon: ShieldCheck }] : links;

  return (
    <nav className="bg-white shadow-sm" aria-label="Navigation principale">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          
          {/* Logo + Badge d'état réseau */}
          <div className="flex items-center gap-4">
            <Link to="/" onClick={close} className="text-lg font-bold text-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600">
              POS
            </Link>
            
            {/* Badge Online/Offline moderne */}
            <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold transition-colors duration-300 ${
              isOnline ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"
            }`}>
              <span className={`h-2 w-2 rounded-full ${isOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`}></span>
              <span>{isOnline ? "En ligne" : "Hors-ligne"}</span>
            </div>
          </div>

          {/* Navigation Desktop */}
          <div className="hidden items-center gap-1 lg:flex">
            {navigationLinks.map(({ to, label, icon: Icon }) => (
              <Link key={to} to={to} className={linkClass(to)}>
                <Icon className="h-4 w-4" />{label}
              </Link>
            ))}
          </div>

          {/* Profil et Déconnexion Desktop */}
          <div className="hidden items-center gap-3 lg:flex">
            <span className="max-w-48 truncate text-sm text-gray-600">{user?.full_name || user?.email}</span>
            <button onClick={logoutUser} className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-red-50 hover:text-red-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-600">
              <LogOut className="h-4 w-4" />Déconnexion
            </button>
          </div>

          {/* Bouton Menu Mobile */}
          <button type="button" onClick={() => setOpen(!open)} aria-expanded={open} aria-controls="mobile-navigation" className="rounded-md p-2 text-gray-700 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 lg:hidden">
            <span className="sr-only">{open ? 'Fermer le menu' : 'Ouvrir le menu'}</span>
            {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Menu Mobile étendu */}
        {open && (
          <div id="mobile-navigation" className="border-t py-3 lg:hidden">
            
            {/* Badge réseau visible en mobile */}
            <div className="flex sm:hidden items-center justify-between px-3 py-2 mb-2 bg-gray-50 rounded-md">
              <span className="text-xs text-gray-500 font-medium">Statut du réseau :</span>
              <div className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                isOnline ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
              }`}>
                <span className={`h-2 w-2 rounded-full ${isOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`}></span>
                <span>{isOnline ? "En ligne" : "Hors-ligne"}</span>
              </div>
            </div>

            <div className="space-y-1">
              {navigationLinks.map(({ to, label, icon: Icon }) => (
                <Link key={to} to={to} onClick={close} className={linkClass(to)}>
                  <Icon className="h-4 w-4" />{label}
                </Link>
              ))}
            </div>
            
            <div className="mt-3 border-t pt-3">
              <p className="mb-2 truncate px-3 text-sm text-gray-600">{user?.full_name || user?.email}</p>
              <button onClick={logoutUser} className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-600">
                <LogOut className="h-4 w-4" />Déconnexion
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}