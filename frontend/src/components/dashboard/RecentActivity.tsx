import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton,
  Divider,
  Skeleton,
  Chip,
  Button
} from '@mui/material'
import {
  Description as DescriptionIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material'
import { getDocuments } from '../../services/apiService'
import { Document } from '../../types'

const RecentActivity = (): JSX.Element => {
  const navigate = useNavigate()
  const [recentDocs, setRecentDocs] = useState<Document[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecentDocuments = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const documents = await getDocuments()
        // Ordenar por fecha de creación (más recientes primero) y tomar los primeros 5
        const recentDocuments = documents
          .sort((a: Document, b: Document) => {
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          })
          .slice(0, 5)
        
        setRecentDocs(recentDocuments)
        setLoading(false)
      } catch (error) {
        console.error('Error al obtener documentos recientes:', error)
        setLoading(false)
        setError('No se pudieron cargar los documentos recientes')
      }
    }
    
    fetchRecentDocuments()
    
    // Actualizar datos cada 2 minutos
    const intervalId = window.setInterval(() => {
      fetchRecentDocuments()
    }, 120000)
    
    return () => {
      window.clearInterval(intervalId)
    }
  }, [])

  // Función para formatear la fecha
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Función para obtener el color del chip según el estado
  const getStatusColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'processing':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'default'
    }
  }

  // Función para obtener el texto del estado en español
  const getStatusText = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'Completado'
      case 'processing':
        return 'Procesando'
      case 'error':
        return 'Error'
      default:
        return 'Desconocido'
    }
  }

  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        height: '100%',
        borderRadius: 2,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="h2">
          Actividad Reciente
        </Typography>
        <Button 
          size="small" 
          endIcon={<ArrowForwardIcon />}
          onClick={() => navigate('/documents')}
        >
          Ver todos
        </Button>
      </Box>
      
      {loading ? (
        <List>
          {[...Array(3)].map((_, index) => (
            <Box key={index}>
              <ListItem disablePadding>
                <ListItemButton disabled>
                  <ListItemIcon>
                    <Skeleton variant="circular" width={24} height={24} />
                  </ListItemIcon>
                  <ListItemText
                    primary={<Skeleton variant="text" width="60%" />}
                    secondary={<Skeleton variant="text" width="40%" />}
                  />
                  <Skeleton variant="rectangular" width={80} height={24} />
                </ListItemButton>
              </ListItem>
              {index < 2 && <Divider component="li" />}
            </Box>
          ))}
        </List>
      ) : error ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexGrow: 1, p: 3 }}>
          <Typography variant="body1" color="error" gutterBottom>
            {error}
          </Typography>
          <Button 
            variant="outlined" 
            color="primary" 
            size="small"
            onClick={() => {
              setLoading(true)
              setError(null)
              getDocuments()
                .then(documents => {
                  const recentDocuments = documents
                    .sort((a: Document, b: Document) => {
                      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                    })
                    .slice(0, 5)
                  
                  setRecentDocs(recentDocuments)
                  setLoading(false)
                })
                .catch(err => {
                  console.error('Error al reintentar:', err)
                  setLoading(false)
                  setError('No se pudieron cargar los documentos recientes')
                })
            }}
            sx={{ mt: 2 }}
          >
            Reintentar
          </Button>
        </Box>
      ) : recentDocs.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
          <Typography variant="body1" color="text.secondary">
            No hay documentos recientes
          </Typography>
        </Box>
      ) : (
        <List sx={{ flexGrow: 1 }}>
          {recentDocs.map((doc, index) => (
            <Box key={doc.id}>
              <ListItem disablePadding>
                <ListItemButton onClick={() => navigate(`/documents/${doc.id}`)}>
                  <ListItemIcon>
                    <DescriptionIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={doc.filename}
                    secondary={formatDate(doc.created_at)}
                    primaryTypographyProps={{
                      noWrap: true,
                      style: { maxWidth: '200px' }
                    }}
                  />
                  <Chip 
                    label={getStatusText(doc.status)} 
                    color={getStatusColor(doc.status)}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </ListItemButton>
              </ListItem>
              {index < recentDocs.length - 1 && <Divider component="li" />}
            </Box>
          ))}
        </List>
      )}
    </Paper>
  )
}

export default RecentActivity