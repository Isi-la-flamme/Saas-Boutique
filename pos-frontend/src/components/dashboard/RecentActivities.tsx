import { Clock3 } from 'lucide-react';

export default function RecentActivities({ sales }: { sales: any[] }) {
  return <section className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-100"><h2 className="font-semibold text-gray-900">Activités récentes</h2><div className="mt-4 space-y-4">{sales.length ? sales.map((sale) => <div key={sale.id} className="flex items-center gap-3"><span className="rounded-full bg-blue-50 p-2 text-blue-600"><Clock3 className="h-4 w-4" /></span><div className="min-w-0 flex-1"><p className="text-sm font-medium text-gray-800">Vente #{sale.id}</p><p className="text-xs text-gray-500">{new Date(sale.created_at).toLocaleString('fr-FR')}</p></div><p className="text-sm font-semibold text-gray-900">{Number(sale.total).toLocaleString('fr-FR')} F CFA</p></div>) : <p className="py-8 text-center text-sm text-gray-500">Aucune activité récente.</p>}</div></section>;
}
