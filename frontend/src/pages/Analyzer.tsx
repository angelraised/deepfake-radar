import { AlertTriangle, CheckCircle2, ImagePlus, LoaderCircle, Scale, UploadCloud, X } from 'lucide-react'
import { useRef, useState } from 'react'
import { analyze, compare } from '../services/api'
import type { Prediction } from '../types'

function Result({ result, title }: { result: Prediction; title?: string }) {
  const ai = result.prediction === 'AI_GENERATED'
  return <div className="result-card">
    {title && <p className="eyebrow">{title}</p>}
    <div className="flex items-center justify-between gap-4"><div><p className="text-xs uppercase tracking-[.18em] text-slate-500">Prediction</p><h3 className={`mt-2 text-2xl font-semibold ${ai ? 'text-destructive' : 'text-slate-200'}`}>{result.prediction.replace('_', '-')}</h3></div><span className="text-4xl font-semibold text-white">{Math.round(result.confidence * 100)}%</span></div>
    <div className="mt-7 space-y-4">{([['Real', result.probabilities.real], ['AI-generated', result.probabilities.ai_generated]] as const).map(([label, value]) => <div key={label}><div className="mb-2 flex justify-between text-xs text-slate-400"><span>{label}</span><span>{(value * 100).toFixed(1)}%</span></div><div className="h-2 overflow-hidden rounded-full bg-muted"><div className={`h-full rounded-full ${label === 'AI-generated' ? 'bg-destructive' : 'bg-electric'}`} style={{ width: `${value * 100}%` }} /></div></div>)}</div>
    <div className="mt-7 grid grid-cols-2 gap-3 text-xs text-slate-500"><span>Model<br /><b className="text-slate-300">{result.model}</b></span><span>Inference<br /><b className="text-slate-300">{result.inference_time_ms.toFixed(1)} ms</b></span></div>
  </div>
}

export function Analyzer() {
  const input = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState<string | null>(null)
  const [mode, setMode] = useState<'improved' | 'compare'>('improved')
  const [result, setResult] = useState<Prediction | null>(null)
  const [comparison, setComparison] = useState<{ baseline: Prediction; improved: Prediction } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const accept = (candidate?: File) => {
    if (!candidate) return
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(candidate.type)) { setError('Choose a PNG, JPG, JPEG, or WEBP image.'); return }
    if (candidate.size > 10 * 1024 * 1024) { setError('Image must be 10 MB or smaller.'); return }
    if (url) URL.revokeObjectURL(url)
    setFile(candidate); setUrl(URL.createObjectURL(candidate)); setResult(null); setComparison(null); setError(null)
  }
  const run = async () => {
    if (!file) return
    setLoading(true); setError(null)
    try { if (mode === 'compare') setComparison(await compare(file)); else setResult(await analyze(file, 'improved')) }
    catch (e) { setError(e instanceof Error ? e.message : 'Analysis failed.') }
    finally { setLoading(false) }
  }
  const clear = () => { if (url) URL.revokeObjectURL(url); setFile(null); setUrl(null); setResult(null); setComparison(null); setError(null) }
  return <section className="section min-h-[calc(100vh-64px)]">
    <div className="mx-auto max-w-3xl text-center"><p className="eyebrow">Image analyzer</p><h1 className="section-title">Inspect an image signal.</h1><p className="section-copy mx-auto">Upload one image for a probabilistic classification. Files are processed in memory and are not stored by default.</p></div>
    <div className="mx-auto mt-12 max-w-4xl">
      <div className="mb-4 flex justify-center"><div className="inline-flex rounded-xl border border-border bg-panel p-1"><button onClick={() => setMode('improved')} className={`mode-tab ${mode === 'improved' ? 'active' : ''}`}><ImagePlus size={15} /> Improved model</button><button onClick={() => setMode('compare')} className={`mode-tab ${mode === 'compare' ? 'active' : ''}`}><Scale size={15} /> Compare models</button></div></div>
      {!file ? <button onClick={() => input.current?.click()} onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); accept(e.dataTransfer.files[0]) }} className="upload-zone"><UploadCloud size={34} className="text-electric" /><span className="mt-5 text-lg font-medium text-white">Drop an image here</span><span className="mt-2 text-sm text-slate-500">or click to browse · PNG, JPG, WEBP · max 10 MB</span></button> : <div className="grid overflow-hidden rounded-2xl border border-border bg-panel md:grid-cols-2"><div className="relative min-h-72 bg-black/30"><img src={url!} alt="Uploaded preview" className="h-full max-h-[460px] w-full object-contain" /><button onClick={clear} className="absolute right-3 top-3 rounded-full bg-black/70 p-2 text-white"><X size={16} /></button></div><div className="flex flex-col justify-center p-8"><p className="break-all text-sm font-medium text-white">{file.name}</p><p className="mt-1 text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p><button onClick={run} disabled={loading} className="primary-button mt-8 justify-center disabled:opacity-50">{loading ? <><LoaderCircle className="animate-spin" size={17} /> Analyzing</> : 'Run analysis'}</button><p className="mt-4 text-xs leading-5 text-slate-500">A trained checkpoint is required. If unavailable, the system will return a setup message instead of a fake result.</p></div></div>}
      <input ref={input} type="file" accept=".png,.jpg,.jpeg,.webp" className="hidden" onChange={(e) => accept(e.target.files?.[0])} />
      {error && <div className="mt-5 flex items-start gap-3 rounded-xl border border-destructive/35 bg-destructive/10 p-4 text-sm text-red-100"><AlertTriangle className="shrink-0 text-destructive" size={18} />{error}</div>}
      {result && <div className="mt-6"><Result result={result} /><p className="mt-4 flex gap-2 text-xs leading-5 text-slate-500"><CheckCircle2 size={15} className="shrink-0" />{result.warning}</p></div>}
      {comparison && <div className="mt-6 grid gap-4 md:grid-cols-2"><Result result={comparison.baseline} title="Baseline" /><Result result={comparison.improved} title="Improved dataset" /></div>}
    </div>
  </section>
}

