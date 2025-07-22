import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Card,
  CardContent,
  CardActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
} from '@mui/material'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DescriptionIcon from '@mui/icons-material/Description'
import HistoryIcon from '@mui/icons-material/History'
import ErrorIcon from '@mui/icons-material/Error'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'

import { getDocuments } from '../services/apiService'
import { Document } from '../types'

const Dashboard = (): JSX.Element => {
  const navigate = useNavigate()
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDocuments = async (): Promise<void> => {
      try {
        setLoading(true)
        const data = await getDocuments()
        setDocuments(data)
        setError(null)
      } catch (err) {
        console.error('Error al cargar documentos:', err)
        setError('No se pudieron cargar los documentos. Por favor, intenta nuevamente.')
      } finally {
        setLoading(false)
      }
    }

    fetchDocuments()
  }, [])

  // Estadísticas de documentos
  const totalDocuments = documents.length
  const completedDocuments = documents.filter(doc => doc.status === 'completed').length
  const processingDocuments = documents.filter(doc => doc.status === 'processing').length
  const errorDocuments = documents.filter(doc => doc.status === 'error').length

  // Documentos recientes (últimos 5)
  const recentDocuments = [...documents]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5)

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Tarjetas de estadísticas */}
        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'primary.light',
              color: 'primary.contrastText',
            }}
          >
            <DescriptionIcon sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="h4" component="div">
              {loading ? <CircularProgress size={24} color="inherit" /> : totalDocuments}
            </Typography>
            <Typography variant="body1">Total de documentos</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'success.light',
              color: 'success.contrastText',
            }}
          >
            <CheckCircleIcon sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="h4" component="div">
              {loading ? <CircularProgress size={24} color="inherit" /> : completedDocuments}
            </Typography>
            <Typography variant="body1">Completados</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'warning.light',
              color: 'warning.contrastText',
            }}
          >
            <HourglassEmptyIcon sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="h4" component="div">
              {loading ? <CircularProgress size={24} color="inherit" /> : processingDocuments}
            </Typography>
            <Typography variant="body1">En proceso</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'error.light',
              color: 'error.contrastText',
            }}
          >
            <ErrorIcon sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="h4" component="div">
              {loading ? <CircularProgress size={24} color="inherit" /> : errorDocuments}
            </Typography>
            <Typography variant="body1">Con errores</Typography>
          </Paper>
        </Grid>

        {/* Acciones rápidas */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="div" gutterBottom>
                Acciones rápidas
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<UploadFileIcon />}
                  onClick={() => navigate('/upload')}
                  fullWidth
                >
                  Subir nuevo documento
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DescriptionIcon />}
                  onClick={() => navigate('/documents')}
                  fullWidth
                >
                  Ver todos los documentos
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Documentos recientes */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" component="div" gutterBottom>
                Documentos recientes
              </Typography>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : error ? (
                <Typography color="error">{error}</Typography>
              ) : recentDocuments.length > 0 ? (
                <List>
                  {recentDocuments.map((doc) => (
                    <Box key={doc.id}>
                      <ListItem button onClick={() => navigate(`/documents/${doc.id}`)}>
                        <ListItemIcon>
                          {doc.status === 'completed' ? (
                            <CheckCircleIcon color="success" />
                          ) : doc.status === 'processing' ? (
                            <HourglassEmptyIcon color="warning" />
                          ) : (
                            <ErrorIcon color="error" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={doc.filename}
                          secondary={
                            <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <HistoryIcon fontSize="small" />
                              {new Date(doc.created_at).toLocaleString()}
                            </Box>
                          }
                        />
                      </ListItem>
                      <Divider />
                    </Box>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                  No hay documentos recientes. ¡Sube tu primer documento!
                </Typography>
              )}
            </CardContent>
            {recentDocuments.length > 0 && (
              <CardActions>
                <Button size="small" onClick={() => navigate('/documents')}>
                  Ver todos
                </Button>
              </CardActions>
            )}
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard