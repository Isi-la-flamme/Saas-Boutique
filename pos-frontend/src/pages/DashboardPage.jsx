import { DollarSign, Package, ShoppingCart, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useDashboard } from '../hooks/useDashboard';
import StatsCard from '../components/Dashboard/StatsCard';
import RevenueChart from '../components/Dashboard/RevenueChart';
import RecentActivities from '../components/Dashboard/RecentActivities';
import SalesOverview from '../components/Dashboard/SalesOverview';
import TopProducts from '../components/Dashboard/TopProducts';
import CustomerInsights from '../components/Dashboard/CustomerInsights';
import QuickActions from '../components/Dashboard/QuickActions';
import MonthlyComparison from '../components/Dashboard/MonthlyComparison';
import POSWidget from '../components/Dashboard/POSWidget';

const DashboardPage = () => {
  const { user } = useAuth();
  const { isLoading, metrics, dailyRevenue, topProducts, recentSales } = useDashboard();
  if (isLoading) return <div className="py-12 text-center text-gray-500">Chargement du tableau de bord…</div>;
  const currency = (value) => `${Number(value).toLocaleString('fr-FR')} F CFA`;
  return <div className="space-y-6"><div><h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1><p className="text-gray-600">Bienvenue, {user?.full_name || user?.email} ! Voici l’activité de votre boutique.</p></div><div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"><StatsCard label="Chiffre d’affaires" value={currency(metrics.revenue)} icon={DollarSign} color="bg-violet-600" hint={`Aujourd’hui : ${currency(metrics.todayRevenue)}`} /><StatsCard label="Ventes" value={metrics.salesCount} icon={ShoppingCart} color="bg-emerald-600" /><StatsCard label="Produits" value={metrics.productCount} icon={Package} color="bg-blue-600" hint={`${metrics.lowStockCount} à faible stock`} /><StatsCard label="Articles vendus" value={metrics.itemsSold} icon={Users} color="bg-orange-500" /></div><div className="grid grid-cols-1 gap-6 xl:grid-cols-3"><div className="xl:col-span-2"><RevenueChart data={dailyRevenue} /></div><SalesOverview revenue={metrics.revenue} salesCount={metrics.salesCount} itemsSold={metrics.itemsSold} /></div><div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4"><TopProducts products={topProducts} /><CustomerInsights salesCount={metrics.salesCount} unpaidCount={metrics.unpaidCount} /><MonthlyComparison current={metrics.monthRevenue} previous={metrics.previousMonthRevenue} /><POSWidget lowStockCount={metrics.lowStockCount} /></div><div className="grid grid-cols-1 gap-6 xl:grid-cols-3"><div className="xl:col-span-2"><RecentActivities sales={recentSales} /></div><QuickActions /></div></div>;
};

export default DashboardPage;
