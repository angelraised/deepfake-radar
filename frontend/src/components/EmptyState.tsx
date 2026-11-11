import { FlaskConical } from 'lucide-react'

export function EmptyState({ title = 'Not evaluated yet', detail = 'Train and evaluate the model to populate this section with real experiment results.' }) {
  return (
    <div className="rounded-2xl border border-dashed border-border bg-panel p-8 text-center">
      <FlaskConical className="mx-auto mb-4 text-slate-300" />
      <h3 className="font-medium text-white">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">{detail}</p>
    </div>
  )
}

