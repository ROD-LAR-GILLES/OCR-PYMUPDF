// Interfaces para documentos
export interface Document {
  id: string;
  filename: string;
  status: 'completed' | 'processing' | 'error';
  created_at: string;
  updated_at: string;
  file_size: number;
  page_count?: number;
  error_message?: string;
  metadata?: Record<string, any>;
}

// Interfaces para opciones de procesamiento
export interface ProcessingOptions {
  use_ocr?: boolean;
  language?: string;
  enhance_image?: boolean;
  use_llm_refiner?: boolean;
  llm_provider?: string;
  llm_model?: string;
  detect_tables?: boolean;
  extract_images?: boolean;
  dpi?: number;
  perform_ocr?: boolean;
}

// Interfaces para preferencias de usuario
export interface UserPreferences {
  default_language: string;
  default_dpi: number;
  auto_detect_tables: boolean;
  extract_images: boolean;
  dark_mode: boolean;
  notifications_enabled: boolean;
  theme?: string;
  language?: string;
  default_use_llm?: boolean;
  default_process_tables?: boolean;
  default_detect_language?: boolean;
  default_spell_check?: boolean;
}

// Interfaces para respuestas de API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Interfaces para estado de documento
export interface DocumentStatus {
  status: 'completed' | 'processing' | 'error';
  progress?: number;
  message?: string;
  error_message?: string;
}

// Interfaces para contenido de documento
export interface DocumentContent {
  id: string;
  content: string;
  format: 'markdown' | 'text' | 'html';
  metadata?: Record<string, any>;
}