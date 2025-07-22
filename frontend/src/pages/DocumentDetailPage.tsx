import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Button,
  Chip,
  LinearProgress,
  CircularProgress,
  Alert,
  Divider,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import DownloadIcon from '@mui/icons-material/Download'
import DeleteIcon from '@mui/icons-material/Delete'
import RefreshIcon from '@mui/icons-material/Refresh'
import ReactMarkdown from 'react-markdown'

import { getDocumentContent, getDocumentStatus, downloadDocument, deleteDocument } from '../services/apiService'
import { Document, DocumentContent } from '../types'

interface DocumentParams {
  id: string;
}

const DocumentDetailPage = (): JSX.Element => {
  const { id } = useParams<DocumentParams>()
  const navigate = useNavigate()
  const [document, setDocument] = useState<DocumentContent | null>(null)
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false)

  // Cargar documento
  useEffect(() => {
    const fetchDocument = async (): Promise<void> => {
      if (!id) return
      
      try {
        setLoading(true)
        const data = await getDocumentContent(id)
        setDocument(data)
        
        // Si el documento está completado, cargar el contenido
        if (data.status === 'completed' && data.content) {
          setContent(data.content)
        }
        
        setError(null)
      } catch (err) {
        console.error('Error al cargar el documento:', err)
        setError('No se pudo cargar el documento. Por favor, intenta nuevamente.')
      } finally {
        setLoading(false)
      }
    }

    fetchDocument()
  }, [id])

  // Actualizar estado del documento si está en proceso
  useEffect(() => {
    let intervalId: NodeJS.Timeout | undefined

    if (document && document.status === 'processing' && id) {
      intervalId = setInterval(async () => {
        try {
          const statusData = await getDocumentStatus(id)
          setDocument(prev => prev ? ({ ...prev, ...statusData }) : statusData)
          
          // Si el documento se ha completado, cargar el contenido
          if (statusData.status === 'completed') {
            const fullData = await getDocumentContent(id)
            setDocument(fullData)
            setContent(fullData.content)
            clearInterval(intervalId)
          } else if (statusData.status === 'error') {
            clearInterval(intervalId)
          }
        } catch (err) {
          console.error('Error al actualizar el estado:', err)
          clearInterval(intervalId)
        }
      }, 3000) // Actualizar cada 3 segundos
    }

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [document, id])

  // Manejar descarga de documento
  const handleDownload = async (): Promise<void> => {
    if (!id) return
    
    try {
      const blob = await downloadDocument(id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = document?.filename.replace('.pdf', '.md') || `document-${id}.md`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Error al descargar el documento:', err)
      setError('No se pudo descargar el documento. Por favor, intenta nuevamente.')
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
      setError('No se pudo eliminar el documento. Por favor, intenta nuevamente.')
    }
  }

  const handleDeleteCancel = (): void => {
    setDeleteDialogOpen(false)
  }

  // Refrescar datos del documento
  const handleRefresh = async (): Promise<void> => {
    if (!id) return
    
    try {
      setLoading(true)
      const data = await getDocumentContent(id)
      setDocument(data)
      
      if (data.status === 'completed' && data.content) {
        setContent(data.content)
      }
      
      setError(null)
    } catch (err) {
      console.error('Error al refrescar el documento:', err)
      setError('No se pudo refrescar el documento. Por favor, intenta nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  // Obtener chip de estado
  const getStatusChip = (status: string): JSX.Element => {
    switch (status) {
      case 'completed':
        return <Chip label="Completado" color="success" />
      case 'processing':
        return <Chip label="Procesando" color="warning" />
      case 'error':
        return <Chip label="Error" color="error" />
      default:
        return <Chip label="Desconocido" />
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
          {error}
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
                  
                  {document.options && (
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
                        Error
                      </Typography>
                      <Alert severity="error" sx={{ mt: 0.5 }}>
                        {document.error_message}
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