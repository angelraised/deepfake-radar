import { Menu, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import type { Page } from '../types'
import { Logo } from './Logo'

const links: { id: Page; label: string }[] = [
  { id: 'home', label: 'Overview' },
  { id: 'analyzer', label: 'Analyzer' },
  { id: 'research', label: 'Research' },
  { id: 'about', label: 'Methodology' },
]

export function Shell({ page, setPage, children }: { page: Page; setPage: (page: Page) => void; children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const navigate = (next: Page) => { setPage(next); setOpen(false); window.scrollTo({ top: 0, behavior: 'smooth' }) }
  return (
    <div className="min-h-screen bg-ink text-slate-200">
      <header className="fixed inset-x-0 top-0 z-50 border-b border-border bg-panel/90 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
          <button onClick={() => navigate('home')} aria-label="Home"><Logo /></button>
          <nav className="hidden items-center gap-1 md:flex">
            {links.map((link) => (
              <button key={link.id} onClick={() => navigate(link.id)} className={`rounded-lg px-4 py-2 text-sm transition ${page === link.id ? 'bg-secondary text-white' : 'text-slate-400 hover:bg-secondary/60 hover:text-white'}`}>
                {link.label}
              </button>
            ))}
          </nav>
          <button className="md:hidden" onClick={() => setOpen(!open)} aria-label="Toggle navigation">{open ? <X /> : <Menu />}</button>
        </div>
        {open && <nav className="border-t border-border px-5 py-3 md:hidden">{links.map((link) => <button key={link.id} onClick={() => navigate(link.id)} className="block w-full px-2 py-3 text-left text-sm">{link.label}</button>)}</nav>}
      </header>
      <main className="pt-16">{children}</main>
      <footer className="border-t border-border bg-panel py-10">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-5 px-5 text-sm text-slate-500 sm:flex-row lg:px-8">
          <Logo /><p>Research prototype · Predictions are probabilistic, not forensic proof.</p>
        </div>
      </footer>
    </div>
  )
}

