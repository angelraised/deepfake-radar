import { useEffect, useState } from 'react'
import { Shell } from './components/Shell'
import { About } from './pages/About'
import { Analyzer } from './pages/Analyzer'
import { Home } from './pages/Home'
import { Research } from './pages/Research'
import type { Page } from './types'

const pages: Page[] = ['home', 'analyzer', 'research', 'about']

export default function App() {
  const initial = window.location.hash.slice(1) as Page
  const [page, setPageState] = useState<Page>(pages.includes(initial) ? initial : 'home')
  const setPage = (next: Page) => { window.location.hash = next; setPageState(next) }
  useEffect(() => { const onHash = () => { const next = window.location.hash.slice(1) as Page; if (pages.includes(next)) setPageState(next) }; window.addEventListener('hashchange', onHash); return () => window.removeEventListener('hashchange', onHash) }, [])
  return <Shell page={page} setPage={setPage}>{page === 'home' && <Home setPage={setPage} />}{page === 'analyzer' && <Analyzer />}{page === 'research' && <Research />}{page === 'about' && <About />}</Shell>
}

