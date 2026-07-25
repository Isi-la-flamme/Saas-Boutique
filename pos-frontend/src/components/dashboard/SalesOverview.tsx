import { TrendingUp } from 'lucide-react';

export default function SalesOverview({ revenue, salesCount, itemsSold }: { revenue: number; salesCount: number; itemsSold: number }) {
  return <section className="rounded-xl bg-gradient-to-br from-indigo-600 to-blue-600 p-5 text-white shadow-sm"><div className="flex items-start justify-between"><div><p className="text-sm text-indigo-100">Vue d’ensemble des ventes</p><p className="mt-2 text-3xl font-bold">{revenue.toLocaleString('fr-FR')} F CFA</p><p className="mt-1 text-sm text-indigo-100">CA encaissé au total</p></div><TrendingUp className="h-7 w-7 text-indigo-200" /></div><div className="mt-6 grid grid-cols-2 gap-4 border-t border-indigo-400/50 pt-4"><div><p className="text-xl font-semibold">{salesCount}</p><p className="text-xs text-indigo-100">Ventes</p></div><div><p className="text-xl font-semibold">{itemsSold}</p><p className="text-xs text-indigo-100">Articles vendus</p></div></div></section>;
}
