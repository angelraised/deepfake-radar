import { ArrowRight, Database, Gauge, Layers3, ShieldCheck, Sparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { EmptyState } from '../components/EmptyState'
import { getResults } from '../services/api'
import type { ExperimentResult, Page } from '../types'

const method = [
  { icon: Database, step: '01', title: 'Curate', text: 'Index sources, licenses, image groups, dimensions, and duplicates.' },
  { icon: Layers3, step: '02', title: 'Control', text: 'Hold architecture and training configuration constant across datasets.' },
  { icon: Gauge, step: '03', title: 'Evaluate', text: 'Measure the same fixed test set plus unseen out-of-distribution sources.' },
]

export function Home({ setPage }: { setPage: (p: Page) => void }) {
  const [results, setResults] = useState<Record<string, ExperimentResult>>({})
  useEffect(() => { getResults().then(setResults).catch(() => undefined) }, [])
  const evaluated = Object.entries(results).filter(([, item]) => item.status === 'evaluated' && item.metrics)
  return <>
    <section className="relative overflow-hidden">
      <div className="orb orb-one" /><div className="orb orb-two" />
      <div className="mx-auto grid min-h-[720px] w-full max-w-7xl items-center gap-16 px-5 py-24 lg:grid-cols-[1.08fr_.92fr] lg:px-8">
        <div className="relative z-10 min-w-0">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-slate-300"><Sparkles size={14} /> Computer vision research platform</div>
          <h1 className="max-w-3xl text-5xl font-semibold leading-[1.03] tracking-[-.045em] text-white sm:text-7xl">See beyond<br /><span className="text-gradient">what looks real.</span></h1>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-400">An experimental AI platform that analyzes visual patterns to distinguish authentic photographs from AI-generated images.</p>
          <div className="mt-9 flex flex-col gap-3 min-[430px]:flex-row min-[430px]:flex-wrap">
            <button onClick={() => setPage('analyzer')} className="primary-button">Analyze an image <ArrowRight size={17} /></button>
            <button onClick={() => setPage('research')} className="secondary-button">Explore our research</button>
          </div>
          <p className="mt-7 flex max-w-xl items-start gap-2 text-xs leading-5 text-slate-500"><ShieldCheck size={16} className="mt-0.5 shrink-0 text-slate-400" />Deepfake Radar estimates probability. It cannot prove whether an image is authentic or establish who created it.</p>
        </div>
        <div className="scan-panel relative mx-auto min-w-0 w-full max-w-lg" aria-hidden="true">
          <div className="scan-grid" /><div className="scan-line" />
          <div className="absolute left-7 top-7 text-[10px] uppercase tracking-[.25em] text-slate-500">visual signal / 001</div>
          <div className="absolute inset-0 grid place-items-center"><div className="radar-ring"><div className="radar-ring inner"><div className="h-3 w-3 rounded-full bg-electric shadow-[0_0_20px_rgba(233,233,233,.35)]" /></div></div></div>
          <div className="absolute bottom-7 left-7 right-7 grid grid-cols-2 gap-3 text-xs"><div className="metric-chip"><span>MODEL STATE</span><b>AWAITING DATA</b></div><div className="metric-chip"><span>CLAIM</span><b>PROBABILISTIC</b></div></div>
        </div>
      </div>
    </section>
    <section className="section border-y border-white/[0.06] bg-white/[0.018]">
      <p className="eyebrow">Research method</p><h2 className="section-title">One model. Better evidence.</h2>
      <p className="section-copy">The model stays fixed. The dataset changes in controlled stages, isolating whether diversity and quality improve generalization.</p>
      <div className="mt-12 grid gap-px overflow-hidden rounded-2xl border border-border bg-border md:grid-cols-3">{method.map(({ icon: Icon, ...item }) => <article key={item.step} className="bg-panel p-7"><div className="flex items-center justify-between"><Icon className="text-slate-300" /><span className="font-mono text-xs text-slate-600">{item.step}</span></div><h3 className="mt-8 text-lg font-medium text-white">{item.title}</h3><p className="mt-3 text-sm leading-6 text-slate-400">{item.text}</p></article>)}</div>
    </section>
    <section className="section"><div className="grid gap-10 lg:grid-cols-2"><div><p className="eyebrow">Hypothesis</p><h2 className="section-title">Diversity should travel further.</h2></div><div className="rounded-2xl border border-border bg-panel p-8 text-lg leading-8 text-slate-300">“An improved and more diverse training dataset will help the model generalize better to previously unseen image sources and image conditions.”</div></div></section>
    <section className="section pt-0"><div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="eyebrow">Model comparison preview</p><h2 className="mt-3 text-2xl font-semibold text-white">Results stay connected to evidence.</h2></div><button onClick={() => setPage('research')} className="text-left text-sm text-slate-300 underline-offset-4 hover:underline">Open research dashboard →</button></div>{evaluated.length === 0 ? <EmptyState /> : <div className="grid gap-4 sm:grid-cols-3">{evaluated.map(([name, item]) => <div key={name} className="rounded-2xl border border-border bg-panel p-6"><p className="capitalize text-sm text-slate-400">{name === 'baseline' ? 'Original' : name}</p><p className="mt-5 text-3xl font-semibold text-white">{((item.metrics?.accuracy ?? 0) * 100).toFixed(1)}%</p><p className="mt-1 text-xs text-slate-500">Held-out accuracy · F1 {(item.metrics?.f1 ?? 0).toFixed(3)}</p></div>)}</div>}</section>
  </>
}

