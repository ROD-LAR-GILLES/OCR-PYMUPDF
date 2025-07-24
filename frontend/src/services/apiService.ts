import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { Document, ProcessingOptions, UserPreferences, DocumentStatus, DocumentContent, ApiResponse } from '../types'

// Crear instancia de axios con configuración base
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para manejar errores de forma global
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Registrar información detallada del error
    let errorMessage = 'Error inesperado en la comunicación con el servidor.';
    
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'La conexión con el servidor ha expirado. El procesamiento del documento puede estar tomando más tiempo del esperado. Verifica tu conexión a internet e intenta nuevamente.';
        console.error('Error: Timeout al conectar con la API. La solicitud ha excedido el tiempo máximo de espera.');
      } else if (!error.response) {
        errorMessage = 'No se pudo establecer conexión con el servidor. Verifica tu conexión a internet o si el servidor está en funcionamiento e intenta nuevamente.';
        console.error('Error: No se pudo establecer conexión con el servidor API. Verifica tu conexión a internet o si el servidor está en funcionamiento.');
      } else {
        console.error(`Error de API: ${error.response.status} - ${error.response.statusText}`);
        console.error('Detalles:', error.response.data);
        
        // Registrar información adicional según el código de estado
        switch (error.response.status) {
          case 400:
            errorMessage = 'Solicitud incorrecta. Verifica las opciones de procesamiento seleccionadas.';
            console.error('Error de solicitud: Los datos enviados son incorrectos o incompletos.');
            break;
          case 401:
            errorMessage = 'No tienes permiso para acceder a este recurso. Por favor, inicia sesión nuevamente.';
            console.error('Error de autenticación: No tienes permiso para acceder a este recurso.');
            break;
          case 404:
            errorMessage = 'El recurso solicitado no existe. Verifica la URL o el identificador del documento.';
            console.error('Recurso no encontrado: El endpoint solicitado no existe.');
            break;
          case 413:
            errorMessage = 'El archivo es demasiado grande. Por favor, intenta con un archivo más pequeño (máximo 50MB) o comprime el PDF antes de subirlo.';
            console.error('Archivo demasiado grande: El servidor rechazó el archivo por exceder el tamaño máximo permitido.');
            break;
          case 500:
            errorMessage = 'Error interno del servidor. El servidor encontró un problema al procesar tu solicitud. Por favor, intenta más tarde.';
            console.error('Error interno del servidor: Ocurrió un problema en el servidor. Por favor, intenta más tarde.');
            break;
          default:
            if (error.response.data && error.response.data.error) {
              errorMessage = `Error: ${error.response.data.error}`;
            } else {
              errorMessage = `Error del servidor (${error.response.status}): ${error.response.statusText}`;
            }
        }
      }
    } else {
      console.error('Error inesperado:', error);
    }
    
    // Añadir el mensaje de error al objeto de error para que esté disponible en los componentes
    if (error.isAxiosError) {
      error.userMessage = errorMessage;
    }
    
    return Promise.reject(error);
  }
)

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
    // El interceptor global ya maneja el registro detallado de errores
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

// Función para subir documentos con seguimiento de progreso
export const uploadDocument = async (formData: FormData, onProgress?: (progressEvent: any) => void): Promise<ApiResponse<Document>> => {
  const response: AxiosResponse<ApiResponse<Document>> = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: onProgress
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
  const response: AxiosResponse<ApiResponse<UserPreferences>> = await api.get('/users/preferences')
  return response.data.data as UserPreferences
}

export const updateUserPreferences = async (preferences: Partial<UserPreferences>): Promise<ApiResponse<UserPreferences>> => {
  const response: AxiosResponse<ApiResponse<UserPreferences>> = await api.put('/users/preferences', preferences)
  return response.data
}

export const getUserProfile = async (): Promise<ApiResponse<{ username: string; email: string }>> => {
  const response: AxiosResponse<ApiResponse<{ username: string; email: string }>> = await api.get('/api/users/profile')
  return response.data
}

export default api