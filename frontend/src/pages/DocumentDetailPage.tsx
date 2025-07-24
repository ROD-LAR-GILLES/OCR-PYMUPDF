import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  IconButton,
  CircularProgress,
  LinearProgress,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Tooltip,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import axios from 'axios'

import { getDocumentContent, getDocumentStatus, downloadDocument, deleteDocument } from '../services/apiService'
import type { Document, DocumentContent, CustomAxiosError, ProcessingStatus } from '../types'

const DocumentDetailPage = (): JSX.Element => {
  const { id } = useParams<string>()
  const navigate = useNavigate()
  const [document, setDocument] = useState<Document | null>(null)
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false)

  useEffect(() => {
    const fetchDocument = async (): Promise<void> => {
      if (!id) return
      
      try {
        setLoading(true)
        const data = await getDocumentContent(id)
        const documentData = data as DocumentContent
        setDocument(documentData)
        
        if (documentData.status === 'completed' && documentData.content) {
          setContent(documentData.content)
        }
        
        setError(null)
      } catch (err) {
        console.error('Error al cargar el documento:', err)
        let errorMessage = 'No se pudo cargar el documento. Por favor, intenta nuevamente.'
        
        if (axios.isAxiosError(err)) {
          const axiosError = err as CustomAxiosError
          errorMessage = axiosError.response?.data?.detail || axiosError.response?.data?.message || axiosError.userMessage || 'Error desconocido'
        }
        
        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    fetchDocument()
  }, [id])

  // Actualizar estado del documento si está en proceso
  useEffect(() => {
    let intervalId: NodeJS.Timeout | undefined

    if (document?.status === 'processing' && id) {
      intervalId = setInterval(async () => {
        try {
          const statusData = await getDocumentStatus(id)
          
          if (statusData.status !== 'processing') {
            // Si el procesamiento ha terminado, obtener el documento completo
            const data = await getDocumentContent(id)
            const documentData = data as DocumentContent
            setDocument(documentData)
            
            if (documentData.status === 'completed' && documentData.content) {
              setContent(documentData.content)
            }
            
            clearInterval(intervalId)
          } else {
            // Actualizar solo el estado y progreso
            setDocument(prev => prev ? { ...prev, ...statusData } : null)
          }
        } catch (err) {
          console.error('Error al actualizar estado del documento:', err)
          if (axios.isAxiosError(err)) {
            const axiosError = err as CustomAxiosError
            setError(axiosError.userMessage || 'Error al actualizar el estado del documento')
          }
          clearInterval(intervalId)
        }
      }, 5000) // Consultar cada 5 segundos
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [document, id])

  // Manejar descarga de documento
  const handleDownload = async (): Promise<void> => {
    if (!id) return
    
    try {
      const blob = await downloadDocument(id)
      const url = window.URL.createObjectURL(blob)
      const a = window.document.createElement('a')
      a.href = url
      a.download = document?.filename?.replace('.pdf', '.md') || `document-${id}.md`
      window.document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      window.document.body.removeChild(a)
    } catch (err) {
      console.error('Error al descargar el documento:', err)
      let errorMessage = 'No se pudo descargar el documento. Por favor, intenta nuevamente.'
      
      if (axios.isAxiosError(err)) {
        const axiosError = err as CustomAxiosError
        errorMessage = axiosError.userMessage || axiosError.response?.data?.message || 'Error desconocido'
      }
      
      setError(errorMessage)
    }
  }

  // Manejar eliminación de documento
  const handleDeleteClick = (): void => {
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async (): Promise<void> => {
    if (!id) return
    
    try {
      await deleteDocument(id)
      setDeleteDialogOpen(false)
      navigate('/documents')
    } catch (err) {
      console.error('Error al eliminar el documento:', err)
      let errorMessage = 'No se pudo eliminar el documento. Por favor, intenta nuevamente.'
      
      if (axios.isAxiosError(err)) {
        const axiosError = err as CustomAxiosError
        errorMessage = axiosError.userMessage || axiosError.response?.data?.message || 'Error desconocido'
      }
      
      setError(errorMessage)
    }
  }

  const handleDeleteCancel = (): void => {
    setDeleteDialogOpen(false)
  }

  // Refrescar documento
  const handleRefresh = (): void => {
    if (!id) return
    const fetchDocument = async (): Promise<void> => {
      try {
        setLoading(true)
        const data = await getDocumentContent(id)
        const documentData = data as DocumentContent
        setDocument(documentData)
        
        if (documentData.status === 'completed' && documentData.content) {
          setContent(documentData.content)
        }
        
        setError(null)
      } catch (err) {
        console.error('Error al cargar el documento:', err)
        let errorMessage = 'No se pudo cargar el documento. Por favor, intenta nuevamente.'
        
        if (axios.isAxiosError(err)) {
          const axiosError = err as CustomAxiosError
          errorMessage = axiosError.response?.data?.message || axiosError.userMessage || 'Error desconocido'
        }
        
        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    fetchDocument()
  }

  // Obtener chip de estado
  const getStatusChip = (status: ProcessingStatus): JSX.Element => {
    switch (status) {
      case 'completed':
        return <Chip label="Completado" color="success" size="small" />
      case 'processing':
        return <Chip label="Procesando" color="warning" size="small" />
      case 'error':
        return <Chip label="Error" color="error" size="small" />
      default:
        return <Chip label="Desconocido" color="default" size="small" />
    }
  }

  // Formatear fecha
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate('/documents')} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          Detalles del documento
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Tooltip title="Refrescar">
          <IconButton onClick={handleRefresh} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="body2" fontWeight="bold" gutterBottom>
            Error:
          </Typography>
          <Typography variant="body2" data-testid="error-message">
            {error}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            Si el problema persiste, verifica tu conexión a internet o intenta más tarde.
          </Typography>
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : document ? (
        <>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Información del documento
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Nombre del archivo
                    </Typography>
                    <Typography variant="body1">
                      {document.filename}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Estado
                    </Typography>
                    <Box sx={{ mt: 0.5 }}>
                      {getStatusChip(document.status)}
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Fecha de creación
                    </Typography>
                    <Typography variant="body1">
                      {formatDate(document.created_at)}
                    </Typography>
                  </Box>
                  
                  {document.status === 'processing' && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Progreso
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                        <LinearProgress
                          variant="determinate"
                          value={document.progress || 0}
                          sx={{ flexGrow: 1, mr: 1 }}
                        />
                        <Typography variant="body2">
                          {document.progress || 0}%
                        </Typography>
                      </Box>
                    </Box>
                  )}
                  
                  {document?.options && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Opciones de procesamiento
                      </Typography>
                      <Box sx={{ mt: 0.5 }}>
                        {document.options.perform_ocr && (
                          <Chip label="OCR" size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                        )}
                        {document.options.detect_tables && (
                          <Chip label="Tablas" size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                        )}
                        {document.options.extract_images && (
                          <Chip label="Imágenes" size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                        )}
                        {document.options.language && (
                          <Chip
                            label={`Idioma: ${document.options.language}`}
                            size="small"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        )}
                      </Box>
                    </Box>
                  )}
                  
                  {document.error_message && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="error">
                        Error en el procesamiento
                      </Typography>
                      <Alert severity="error" sx={{ mt: 0.5 }}>
                        <Typography variant="body2" fontWeight="bold" gutterBottom>
                        Mensaje de error:
                      </Typography>
                      <Typography variant="body2" data-testid="document-error-message">
                        {document.error_message}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Posibles soluciones:
                      </Typography>
                      <ul>
                        <li>Intenta procesar el documento con diferentes opciones de OCR</li>
                        <li>Verifica que el archivo PDF no esté dañado o protegido</li>
                        <li>Si el documento tiene muchas imágenes, prueba con un valor de DPI más bajo</li>
                        <li>Si el problema persiste, contacta al soporte técnico</li>
                      </ul>
                      </Alert>
                    </Box>
                  )}
                  
                  <Box sx={{ display: 'flex', gap: 1, mt: 3 }}>
                    {document.status === 'completed' && (
                      <Button
                        variant="contained"
                        startIcon={<DownloadIcon />}
                        onClick={handleDownload}
                      >
                        Descargar
                      </Button>
                    )}
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={handleDeleteClick}
                    >
                      Eliminar
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Contenido del documento
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                {document.status === 'completed' ? (
                  content ? (
                    <Box className="document-preview">
                      <ReactMarkdown>{content}</ReactMarkdown>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No hay contenido disponible para mostrar.
                    </Typography>
                  )
                ) : document.status === 'processing' ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <CircularProgress sx={{ mb: 2 }} />
                    <Typography>
                      El documento está siendo procesado. Por favor, espera...
                    </Typography>
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No se puede mostrar el contenido debido a un error en el procesamiento.
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>

          {/* Diálogo de confirmación para eliminar */}
          <Dialog
            open={deleteDialogOpen}
            onClose={handleDeleteCancel}
          >
            <DialogTitle>Confirmar eliminación</DialogTitle>
            <DialogContent>
              <DialogContentText>
                ¿Estás seguro de que deseas eliminar el documento "{document.filename}"?
                Esta acción no se puede deshacer.
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleDeleteCancel}>Cancelar</Button>
              <Button onClick={handleDeleteConfirm} color="error" autoFocus>
                Eliminar
              </Button>
            </DialogActions>
          </Dialog>
        </>
      ) : (
        <Alert severity="warning">
          No se encontró el documento solicitado.
        </Alert>
      )}
    </Box>
  )
}

export default DocumentDetailPage