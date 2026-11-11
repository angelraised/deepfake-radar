import { ScanSearch } from 'lucide-react'

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid h-9 w-9 place-items-center rounded-xl border border-border bg-secondary text-electric">
        <ScanSearch size={19} strokeWidth={2.2} />
      </span>
      {!compact && <span className="text-sm font-semibold tracking-[0.18em] text-white">DEEPFAKE RADAR</span>}
    </div>
  )
}

