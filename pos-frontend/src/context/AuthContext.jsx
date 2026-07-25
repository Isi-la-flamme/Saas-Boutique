import { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';
import { tenantApi } from '../api/tenants';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [tenantId, setTenantId] = useState(localStorage.getItem('tenantId'));

  useEffect(() => {
    const initAuth = async () => {
      // Si token présent, charger l'utilisateur
      if (token) {
        await loadUser();
      }
      
      // ❌ SUPPRIMER ensureTenant - La création se fait uniquement via RegisterPage
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const loadUser = async () => {
    try {
      const response = await authApi.me();
      setUser(response.data);
      // Si l'utilisateur a un tenant, on le sauvegarde
      if (response.data.tenant_id) {
        localStorage.setItem('tenantId', response.data.tenant_id);
        setTenantId(response.data.tenant_id);
      }
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('tenantId');
      setToken(null);
      setTenantId(null);
      setUser(null);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authApi.login({ email, password });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      await loadUser();
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const register = async (data) => {
    // L'inscription nécessite un tenant, on le crée d'abord
    try {
      // 1. Créer le tenant avec le nom saisi par l'utilisateur
      const tenantResponse = await tenantApi.create({ 
        name: data.tenantName || 'Mon Entreprise',
        description: `Entreprise ${data.tenantName || 'Mon Entreprise'}`
      });
      const tenant = tenantResponse.data;
      
      // 2. Sauvegarder le tenant
      localStorage.setItem('tenantId', tenant.tenant_id);
      setTenantId(tenant.tenant_id);
      
      // 3. Créer l'utilisateur
      const userResponse = await authApi.register({
        email: data.email,
        username: data.username,
        password: data.password,
        full_name: data.full_name,
      });
      
      return userResponse.data;
    } catch (error) {
      console.error('❌ Erreur inscription:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('tenantId');
    setToken(null);
    setTenantId(null);
    setUser(null);
    toast.success('Déconnecté');
  };

  const setTenant = (id) => {
    localStorage.setItem('tenantId', id);
    setTenantId(id);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        token,
        tenantId,
        login,
        register,
        logout,
        setTenant,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};