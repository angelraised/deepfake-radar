import { Activity, Database, Timer, TrendingUp } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { EmptyState } from '../components/EmptyState'
import { getResults, getStats } from '../services/api'
import type { ExperimentResult, Metrics } from '../types'

function MetricCard({ label, value, icon: Icon }: { label: string; value: string; icon: typeof Activity }) {
  return <div className="rounded-2xl border border-border bg-panel p-5"><Icon size={17} className="text-slate-300" /><p className="mt-5 text-xs uppercase tracking-[.15em] text-slate-500">{label}</p><p className="mt-2 text-2xl font-semibold text-white">{value}</p></div>
}

function Matrix({ values, label }: { values: number[][]; label: string }) {
  const max = Math.max(...values.flat(), 1)
  return <div><p className="mb-4 text-sm font-medium text-white">{label}</p><div className="grid grid-cols-2 gap-2">{values.flat().map((value, index) => <div key={index} className="grid aspect-[2/1] place-items-center rounded-lg border border-border text-lg font-semibold text-white" style={{ backgroundColor: `rgba(233,233,233,${0.04 + value / max * 0.24})` }}>{value}</div>)}</div><div className="mt-2 flex justify-between text-[10px] uppercase tracking-wider text-slate-600"><span>Pred. real</span><span>Pred. AI</span></div></div>
}

export function Research() {
  const [results, setResults] = useState<Record<string, ExperimentResult>>({})
  const [stats, setStats] = useState<Record<string, Record<string, unknown> | null>>({})
  const [offline, setOffline] = useState(false)
  useEffect(() => { Promise.all([getResults(), getStats()]).then(([r, s]) => { setResults(r); setStats(s) }).catch(() => setOffline(true)) }, [])
  const evaluated = Object.entries(results).filter(([, value]) => value.status === 'evaluated' && value.metrics)
  const chart = useMemo(() => evaluated.map(([name, value]) => ({ name: name === 'baseline' ? 'Original' : name[0].toUpperCase() + name.slice(1), Accuracy: Number(((value.metrics?.accuracy ?? 0) * 100).toFixed(2)), 'F1-score': Number(((value.metrics?.f1 ?? 0) * 100).toFixed(2)), 'OOD F1': value.ood_metrics ? Number((value.ood_metrics.f1 * 100).toFixed(2)) : 0 })), [results])
  const improved = results.improved?.metrics as Metrics | null | undefined
  const roc = useMemo(() => {
    const curve = improved?.roc_curve
    if (!curve) return []
    return curve.fpr.map((fpr, index) => ({ fpr: Number((fpr * 100).toFixed(2)), tpr: Number(((curve.tpr[index] ?? 0) * 100).toFixed(2)) }))
  }, [improved])
  const composition = useMemo(() => ['baseline', 'expanded', 'improved'].map((stage) => {
    const distribution = stats[stage]?.class_distribution as Record<string, number> | undefined
    return { name: stage === 'baseline' ? 'Original' : stage[0].toUpperCase() + stage.slice(1), Real: distribution?.real ?? 0, 'AI-generated': distribution?.ai_generated ?? 0 }
  }).filter((item) => item.Real || item['AI-generated']), [stats])
  return <section className="section min-h-[calc(100vh-64px)]">
    <div className="max-w-3xl"><p className="eyebrow">Research dashboard</p><h1 className="section-title">Evidence, not decoration.</h1><p className="section-copy">Every value on this page is loaded from saved experiment artifacts. Missing data remains visibly missing.</p></div>
    {offline && <div className="mt-8"><EmptyState title="Backend unavailable" detail="Start FastAPI on port 8000 to load research artifacts." /></div>}
    {!offline && evaluated.length === 0 && <div className="mt-10"><EmptyState /></div>}
    {evaluated.length > 0 && <>
      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><MetricCard icon={Activity} label="Improved accuracy" value={improved ? `${(improved.accuracy * 100).toFixed(1)}%` : 'Not evaluated'} /><MetricCard icon={TrendingUp} label="Improved F1" value={improved ? improved.f1.toFixed(3) : 'Not evaluated'} /><MetricCard icon={Timer} label="Training time" value={improved?.training_time_seconds ? `${Math.round(improved.training_time_seconds)}s` : 'Not recorded'} /><MetricCard icon={Database} label="Experiments" value={`${evaluated.length} / 3`} /></div>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1.45fr_.55fr]"><div className="rounded-2xl border border-border bg-panel p-5 sm:p-7"><h2 className="text-lg font-medium text-white">Held-out performance</h2><p className="mt-1 text-xs text-slate-500">Same independent test set for every stage</p><div className="mt-8 h-80"><ResponsiveContainer width="100%" height="100%"><BarChart data={chart} barGap={4}><CartesianGrid stroke="#292929" vertical={false} /><XAxis dataKey="name" stroke="#7a7a7a" tickLine={false} axisLine={false} fontSize={12} /><YAxis domain={[0, 100]} stroke="#7a7a7a" tickLine={false} axisLine={false} fontSize={12} /><Tooltip contentStyle={{ background: '#0d0d0d', border: '1px solid #292929', borderRadius: 12 }} /><Legend /><Bar dataKey="Accuracy" fill="#e9e9e9" radius={[5,5,0,0]} /><Bar dataKey="F1-score" fill="#7a7a7a" radius={[5,5,0,0]} /><Bar dataKey="OOD F1" fill="#ff6268" radius={[5,5,0,0]} /></BarChart></ResponsiveContainer></div></div><div className="rounded-2xl border border-border bg-panel p-7">{improved?.confusion_matrix ? <Matrix values={improved.confusion_matrix} label="Improved confusion matrix" /> : <EmptyState />}</div></div>
      {roc.length > 0 && <div className="mt-6 rounded-2xl border border-border bg-panel p-5 sm:p-7"><h2 className="text-lg font-medium text-white">Improved model ROC curve</h2><p className="mt-1 text-xs text-slate-500">True-positive rate versus false-positive rate</p><div className="mt-6 h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={roc}><CartesianGrid stroke="#292929" /><XAxis dataKey="fpr" type="number" domain={[0,100]} stroke="#7a7a7a" fontSize={11} /><YAxis domain={[0,100]} stroke="#7a7a7a" fontSize={11} /><Tooltip contentStyle={{ background: '#0d0d0d', border: '1px solid #292929', borderRadius: 12 }} /><Line type="monotone" dataKey="tpr" stroke="#e9e9e9" strokeWidth={2} dot={false} /></LineChart></ResponsiveContainer></div></div>}
    </>}
    <div className="mt-14 grid gap-6 lg:grid-cols-2"><div><p className="eyebrow">Dataset stages</p><h2 className="text-2xl font-semibold text-white">From volume to quality.</h2><p className="mt-4 text-sm leading-7 text-slate-400">Original establishes the baseline. Expanded adds sources. Improved adds diversity controls, provenance, duplicate filtering, balanced classes, and train-only condition variants.</p></div><div className="space-y-3">{['baseline', 'expanded', 'improved'].map((stage, index) => { const data = stats[stage]; const count = typeof data?.total_images === 'number' ? String(data.total_images) : 'Not reported'; return <div key={stage} className="flex items-center justify-between rounded-xl border border-border bg-panel p-4"><div className="flex items-center gap-4"><span className="font-mono text-xs text-slate-600">0{index + 1}</span><span className="capitalize text-white">{stage === 'baseline' ? 'Original' : stage}</span></div><span className="text-sm text-slate-500">{count} images</span></div> })}</div></div>
    {composition.length > 0 && <div className="mt-6 rounded-2xl border border-border bg-panel p-5 sm:p-7"><h2 className="text-lg font-medium text-white">Class balance and composition</h2><div className="mt-6 h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={composition}><CartesianGrid stroke="#292929" vertical={false} /><XAxis dataKey="name" stroke="#7a7a7a" fontSize={11} /><YAxis stroke="#7a7a7a" fontSize={11} /><Tooltip contentStyle={{ background: '#0d0d0d', border: '1px solid #292929', borderRadius: 12 }} /><Legend /><Bar dataKey="Real" stackId="a" fill="#e9e9e9" /><Bar dataKey="AI-generated" stackId="a" fill="#ff6268" /></BarChart></ResponsiveContainer></div></div>}
    <div className="mt-14 rounded-2xl border border-border bg-panel p-7"><h2 className="text-lg font-medium text-white">Why did the improved dataset perform differently?</h2>{evaluated.length === 3 ? <p className="mt-3 text-sm leading-7 text-slate-400">Interpretation must be written after inspecting source-wise errors, confidence calibration, and OOD results. The dashboard does not infer causality from the headline score alone.</p> : <p className="mt-3 text-sm leading-7 text-slate-400">Not evaluated yet. This explanation will be based on actual source-wise and OOD findings after all three experiments finish.</p>}</div>
  </section>
}

