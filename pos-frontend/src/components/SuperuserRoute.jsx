import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function SuperuserRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="py-12 text-center text-gray-600">Vérification des accès…</p>;
  return user?.is_superuser ? children : <Navigate to="/" replace />;
}
