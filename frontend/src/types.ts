import { AxiosError } from 'axios'

export interface Document {
  id: string
  filename: string
  status: ProcessingStatus
  created_at: string
  updated_at: string
  content?: string
  progress?: number
  error_message?: string
  options?: DocumentOptions
}

interface DocumentOptions {
  perform_ocr?: boolean
  detect_tables?: boolean
  extract_images?: boolean
  language?: string
}

export interface DocumentContent extends Document {
  text: string
  pages: number
  tables: any[]
  images: string[]
  progress: number
  options: ProcessingOptions
  error_message?: string
}

export interface CustomAxiosError extends AxiosError {
  userMessage?: string
  response?: {
    status: number
    statusText: string
    headers: Record<string, string>
    config: any
    data: {
      detail?: string
      message?: string
      error?: string
    }
  }
}

export interface ProcessingOptions {
  perform_ocr?: boolean
  detect_tables?: boolean
  extract_images?: boolean
  language?: string
  dpi?: number
  use_llm_refiner?: boolean
  llm_provider?: string
  llm_model?: string
}

export interface UploadResponse {
  id: string
  message: string
  data: Document
}

// DocumentStatus ya no es necesario ya que Document incluye progress y error_message

export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'error'

export interface UserPreferences {
  default_language: string
  default_dpi: number
  auto_detect_tables: boolean
  extract_images: boolean
  dark_mode: boolean
  notifications_enabled: boolean
}

export interface ApiResponse<T> {
  data: T
  message?: string
  error?: string
}