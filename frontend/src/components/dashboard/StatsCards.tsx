import { useState, useEffect } from 'react'
import { 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  CircularProgress,
  Skeleton,
  Tooltip,
  Button
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import ErrorIcon from '@mui/icons-material/Error'
import { getDocuments } from '../../services/apiService'
import { Document } from '../../types'

interface StatsData {
  total: number;
  completed: number;
  processing: number;
  error: number;
  loading: boolean;
}

const StatsCards = (): JSX.Element => {
  const [stats, setStats] = useState<StatsData>({
    total: 0,
    completed: 0,
    processing: 0,
    error: 0,
    loading: true
  })

  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      setStats(prev => ({ ...prev, loading: true }))
      setError(null)
      
      try {
        const documents = await getDocuments()
        
        // Calcular estadísticas
        const completed = documents.filter(doc => doc.status === 'completed').length
        const processing = documents.filter(doc => doc.status === 'processing').length
        const error = documents.filter(doc => doc.status === 'error').length
        
        setStats({
          total: documents.length,
          completed,
          processing,
          error,
          loading: false
        })
      } catch (error) {
        console.error('Error al obtener estadísticas:', error)
        setStats(prev => ({ ...prev, loading: false }))
        setError('No se pudieron cargar las estadísticas. Intente nuevamente más tarde.')
      }
    }
    
    fetchStats()
    
    // Configurar un intervalo para actualizar las estadísticas cada 60 segundos
    const intervalId = window.setInterval(() => {
      fetchStats()
    }, 60000)
    
    return () => {
      window.clearInterval(intervalId)
    }
  }, [])

  const statCards = [
    {
      title: 'Total de Documentos',
      value: stats.total,
      icon: <DescriptionIcon fontSize="large" color="primary" />,
      color: '#3f51b5'
    },
    {
      title: 'Completados',
      value: stats.completed,
      icon: <CheckCircleIcon fontSize="large" color="success" />,
      color: '#4caf50'
    },
    {
      title: 'En Procesamiento',
      value: stats.processing,
      icon: <HourglassEmptyIcon fontSize="large" color="warning" />,
      color: '#ff9800'
    },
    {
      title: 'Con Errores',
      value: stats.error,
      icon: <ErrorIcon fontSize="large" color="error" />,
      color: '#f44336'
    }
  ]

  return (
    <Grid container spacing={3}>
      {error ? (
        <Grid item xs={12}>
          <Paper
            elevation={2}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 2,
              borderLeft: '4px solid #f44336'
            }}
          >
            <Typography color="error" variant="subtitle1">
              {error}
            </Typography>
            <Button 
              variant="outlined" 
              color="primary" 
              size="small"
              onClick={() => {
                setStats(prev => ({ ...prev, loading: true }))
                setError(null)
                getDocuments()
                  .then(documents => {
                    const completed = documents.filter(doc => doc.status === 'completed').length
                    const processing = documents.filter(doc => doc.status === 'processing').length
                    const error = documents.filter(doc => doc.status === 'error').length
                    
                    setStats({
                      total: documents.length,
                      completed,
                      processing,
                      error,
                      loading: false
                    })
                  })
                  .catch(err => {
                    console.error('Error al reintentar:', err)
                    setStats(prev => ({ ...prev, loading: false }))
                    setError('No se pudieron cargar las estadísticas. Intente nuevamente más tarde.')
                  })
              }}
              sx={{ mt: 2, alignSelf: 'flex-start' }}
            >
              Reintentar
            </Button>
          </Paper>
        </Grid>
      ) : (
        statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: 140,
                borderTop: `4px solid ${card.color}`,
                borderRadius: 2,
                transition: 'transform 0.3s, box-shadow 0.3s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 3
                }
              }}
            >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6" component="h2" color="text.secondary">
                {card.title}
              </Typography>
              {card.icon}
            </Box>
            
            {stats.loading ? (
              <Skeleton variant="rectangular" width="60%" height={40} />
            ) : (
              <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
                {card.value}
              </Typography>
            )}
          </Paper>
        </Grid>
      ))}
    </Grid>
  )
}

export default StatsCards