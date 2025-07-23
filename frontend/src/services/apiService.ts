import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { Document, ProcessingOptions, UserPreferences, DocumentStatus, DocumentContent, ApiResponse } from '../types'

// Crear instancia de axios con configuración base
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Verificar estado de la API
export const checkApiHealth = async (): Promise<ApiResponse<{ status: string }>> => {
  const response: AxiosResponse<ApiResponse<{ status: string }>> = await api.get('/health')
  return response.data
}

// Verificar conexión con la API
export const getApiStatus = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health', { timeout: 5000 }) // Timeout de 5 segundos
    if (response.status === 200) {
      console.log('Conexión API establecida correctamente')
      return true
    }
    return false
  } catch (error) {
    console.error('Error al verificar estado de la API:', error)
    // Registrar información más detallada sobre el error
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        console.error('Timeout al conectar con la API')
      } else if (!error.response) {
        console.error('No se pudo establecer conexión con el servidor API')
      } else {
        console.error(`Error de API: ${error.response.status} - ${error.response.statusText}`)
      }
    }
    return false
  }
}

// Servicios para documentos PDF
export const uploadPdf = async (file: File, options: ProcessingOptions = {}): Promise<ApiResponse<Document>> => {
  const formData = new FormData()
  formData.append('file', file)
  
  // Añadir opciones de procesamiento si existen
  if (options) {
    formData.append('options', JSON.stringify(options))
  }
  
  const response: AxiosResponse<ApiResponse<Document>> = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getDocuments = async (): Promise<Document[]> => {
  const response: AxiosResponse<ApiResponse<Document[]>> = await api.get('/documents')
  return response.data.data || []
}

export const getDocumentStatus = async (documentId: string): Promise<DocumentStatus> => {
  const response: AxiosResponse<ApiResponse<DocumentStatus>> = await api.get(`/documents/${documentId}/status`)
  return response.data.data as DocumentStatus
}

export const getDocumentContent = async (documentId: string): Promise<DocumentContent> => {
  const response: AxiosResponse<ApiResponse<DocumentContent>> = await api.get(`/documents/${documentId}`)
  return response.data.data as DocumentContent
}

export const downloadDocument = async (documentId: string, format: 'markdown' | 'text' | 'html' = 'markdown'): Promise<Blob> => {
  const response: AxiosResponse<Blob> = await api.get(`/documents/${documentId}/download?format=${format}`, {
    responseType: 'blob',
  })
  return response.data
}

export const deleteDocument = async (documentId: string): Promise<ApiResponse<null>> => {
  const response: AxiosResponse<ApiResponse<null>> = await api.delete(`/documents/${documentId}`)
  return response.data
}

// Servicios para preferencias de usuario
export const getUserPreferences = async (): Promise<UserPreferences> => {
  const response: AxiosResponse<ApiResponse<UserPreferences>> = await api.get('/user/preferences')
  return response.data.data as UserPreferences
}

export const updateUserPreferences = async (preferences: Partial<UserPreferences>): Promise<ApiResponse<UserPreferences>> => {
  const response: AxiosResponse<ApiResponse<UserPreferences>> = await api.put('/user/preferences', preferences)
  return response.data
}

export const getUserProfile = async (): Promise<ApiResponse<{ username: string; email: string }>> => {
  const response: AxiosResponse<ApiResponse<{ username: string; email: string }>> = await api.get('/user/profile')
  return response.data
}

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Personalizar manejo de errores aquí
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api