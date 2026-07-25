import type { LucideIcon } from 'lucide-react';

export default function StatsCard({ label, value, icon: Icon, color = 'bg-blue-600', hint }: { label: string; value: string | number; icon: LucideIcon; color?: string; hint?: string }) {
  return <div className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-100"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-500">{label}</p><p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>{hint && <p className="mt-1 text-xs text-gray-400">{hint}</p>}</div><span className={`${color} rounded-lg p-3 text-white`}><Icon className="h-5 w-5" /></span></div></div>;
}
