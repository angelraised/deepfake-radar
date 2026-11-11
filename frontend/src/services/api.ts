import type { ExperimentResult, Prediction } from '../types'

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(detail.detail ?? 'Request failed')
  }
  return response.json() as Promise<T>
}

export async function analyze(file: File, model: string): Promise<Prediction> {
  const body = new FormData()
  body.append('file', file)
  return parse(await fetch(`/api/predict?model=${model}`, { method: 'POST', body }))
}

export async function compare(file: File): Promise<{ baseline: Prediction; improved: Prediction }> {
  const body = new FormData()
  body.append('file', file)
  return parse(await fetch('/api/compare', { method: 'POST', body }))
}

export async function getResults(): Promise<Record<string, ExperimentResult>> {
  return parse(await fetch('/api/research/results'))
}

export async function getStats(): Promise<Record<string, Record<string, unknown> | null>> {
  return parse(await fetch('/api/research/dataset-stats'))
}

