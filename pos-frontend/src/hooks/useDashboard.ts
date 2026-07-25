import { useQuery } from '@tanstack/react-query';
import { productApi } from '../api/products';
import { saleApi } from '../api/sales';

const startOfDay = (date: Date) => new Date(date.getFullYear(), date.getMonth(), date.getDate());
const dayKey = (date: Date) => date.toISOString().slice(0, 10);

export function useDashboard() {
  const productsQuery = useQuery({ queryKey: ['products'], queryFn: () => productApi.getAll() });
  const salesQuery = useQuery({ queryKey: ['sales'], queryFn: () => saleApi.getAll() });
  const products = productsQuery.data?.data?.items ?? [];
  const sales = salesQuery.data?.data?.items ?? [];
  const now = new Date();
  const today = startOfDay(now);
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const previousMonthStart = new Date(now.getFullYear(), now.getMonth() - 1, 1);

  const completedSales = sales.filter((sale: any) => sale.status === 'completed');
  const salesSince = (date: Date) => completedSales.filter((sale: any) => new Date(sale.created_at) >= date);
  const sum = (items: any[]) => items.reduce((total, item) => total + Number(item.total || 0), 0);
  const currentMonthSales = salesSince(monthStart);
  const previousMonthSales = completedSales.filter((sale: any) => {
    const date = new Date(sale.created_at);
    return date >= previousMonthStart && date < monthStart;
  });
  const itemsSold = completedSales.reduce((total: number, sale: any) => total + (sale.items || []).reduce((count: number, item: any) => count + Number(item.quantity || 0), 0), 0);
  const productSales = new Map<number, { id: number; name: string; quantity: number; revenue: number }>();

  completedSales.forEach((sale: any) => (sale.items || []).forEach((item: any) => {
    const current = productSales.get(item.product_id) || { id: item.product_id, name: item.product_name || `Produit #${item.product_id}`, quantity: 0, revenue: 0 };
    current.quantity += Number(item.quantity || 0);
    current.revenue += Number(item.total_price ?? item.quantity * item.unit_price ?? 0);
    productSales.set(item.product_id, current);
  }));

  const dailyRevenue = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today);
    date.setDate(today.getDate() - 6 + index);
    const key = dayKey(date);
    return { label: date.toLocaleDateString('fr-FR', { weekday: 'short' }), revenue: sum(completedSales.filter((sale: any) => dayKey(new Date(sale.created_at)) === key)) };
  });

  return {
    isLoading: productsQuery.isLoading || salesQuery.isLoading,
    isError: productsQuery.isError || salesQuery.isError,
    products,
    sales,
    metrics: {
      productCount: products.length,
      salesCount: sales.length,
      revenue: sum(completedSales),
      todayRevenue: sum(salesSince(today)),
      monthRevenue: sum(currentMonthSales),
      previousMonthRevenue: sum(previousMonthSales),
      itemsSold,
      lowStockCount: products.filter((product: any) => Number(product.stock) <= 5).length,
      unpaidCount: sales.filter((sale: any) => sale.payment_status !== 'paid').length,
    },
    dailyRevenue,
    topProducts: [...productSales.values()].sort((a, b) => b.quantity - a.quantity).slice(0, 5),
    recentSales: [...sales].sort((a: any, b: any) => +new Date(b.created_at) - +new Date(a.created_at)).slice(0, 5),
  };
}
