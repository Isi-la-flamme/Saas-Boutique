import { CreditCard, Users } from 'lucide-react';

export default function CustomerInsights({ salesCount, unpaidCount }: { salesCount: number; unpaidCount: number }) {
  return <section className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-100"><h2 className="font-semibold text-gray-900">Insights clients</h2><div className="mt-4 grid grid-cols-2 gap-3"><div className="rounded-lg bg-blue-50 p-3"><Users className="h-5 w-5 text-blue-600" /><p className="mt-2 text-lg font-bold text-gray-900">{salesCount}</p><p className="text-xs text-gray-500">Passages enregistrés</p></div><div className="rounded-lg bg-amber-50 p-3"><CreditCard className="h-5 w-5 text-amber-600" /><p className="mt-2 text-lg font-bold text-gray-900">{unpaidCount}</p><p className="text-xs text-gray-500">Paiements à suivre</p></div></div></section>;
}
