export type Page = 'home' | 'analyzer' | 'research' | 'about'

export interface Prediction {
  prediction: 'REAL' | 'AI_GENERATED'
  confidence: number
  probabilities: { real: number; ai_generated: number }
  model: string
  version: string
  inference_time_ms: number
  warning: string
}

export interface ExperimentResult {
  status: 'evaluated' | 'not_evaluated'
  metrics: Metrics | null
  ood_metrics: Metrics | null
}

export interface Metrics {
  accuracy: number
  precision: number
  recall: number
  f1: number
  roc_auc: number | null
  confusion_matrix: number[][]
  inference_time_ms?: number
  training_time_seconds?: number
  roc_curve?: { fpr: number[]; tpr: number[] }
}

