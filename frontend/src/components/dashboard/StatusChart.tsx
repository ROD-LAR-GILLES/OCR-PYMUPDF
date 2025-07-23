import { useState, useEffect } from 'react'
import { 
  Paper, 
  Typography, 
  Box, 
  CircularProgress,
  useTheme,
  Button
} from '@mui/material'
import { getDocuments } from '../../services/apiService'
import { Document } from '../../types'

interface ChartData {
  completed: number;
  processing: number;
  error: number;
  loading: boolean;
}

const StatusChart = (): JSX.Element => {
  const theme = useTheme()
  const [chartData, setChartData] = useState<ChartData>({
    completed: 0,
    processing: 0,
    error: 0,
    loading: true
  })

  const [fetchError, setFetchError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setChartData(prev => ({ ...prev, loading: true }))
      setFetchError(null)
      
      try {
        const documents = await getDocuments()
        
        // Calcular datos para el gráfico
        const completed = documents.filter(doc => doc.status === 'completed').length
        const processing = documents.filter(doc => doc.status === 'processing').length
        const error = documents.filter(doc => doc.status === 'error').length
        
        setChartData({
          completed,
          processing,
          error,
          loading: false
        })
      } catch (error) {
        console.error('Error al obtener datos para el gráfico:', error)
        setChartData(prev => ({ ...prev, loading: false }))
        setFetchError('No se pudieron cargar los datos del gráfico')
      }
    }
    
    fetchData()
    
    // Actualizar datos cada minuto
    const intervalId = window.setInterval(() => {
      fetchData()
    }, 60000)
    
    return () => {
      window.clearInterval(intervalId)
    }
  }, [])

  // Calcular el total para los porcentajes
  const total = chartData.completed + chartData.processing + chartData.error
  
  // Definir colores para cada estado
  const colors = {
    completed: theme.palette.success.main,
    processing: theme.palette.warning.main,
    error: theme.palette.error.main
  }

  // Calcular porcentajes para el gráfico
  const getPercentage = (value: number): number => {
    if (total === 0) return 0
    return Math.round((value / total) * 100)
  }

  const completedPercentage = getPercentage(chartData.completed)
  const processingPercentage = getPercentage(chartData.processing)
  const errorPercentage = getPercentage(chartData.error)

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
      <Typography variant="h6" component="h2" gutterBottom>
        Distribución de Documentos
      </Typography>
      
      {chartData.loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
          <CircularProgress />
        </Box>
      ) : fetchError ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
          <Typography variant="body1" color="error" gutterBottom>
            {fetchError}
          </Typography>
          <Button 
            variant="outlined" 
            color="primary" 
            size="small"
            onClick={() => {
              setChartData(prev => ({ ...prev, loading: true }))
              setFetchError(null)
              getDocuments()
                .then(documents => {
                  const completed = documents.filter(doc => doc.status === 'completed').length
                  const processing = documents.filter(doc => doc.status === 'processing').length
                  const error = documents.filter(doc => doc.status === 'error').length
                  
                  setChartData({
                    completed,
                    processing,
                    error,
                    loading: false
                  })
                })
                .catch(err => {
                  console.error('Error al reintentar:', err)
                  setChartData(prev => ({ ...prev, loading: false }))
                  setFetchError('No se pudieron cargar los datos del gráfico')
                })
            }}
            sx={{ mt: 2 }}
          >
            Reintentar
          </Button>
        </Box>
      ) : total === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
          <Typography variant="body1" color="text.secondary">
            No hay documentos para mostrar
          </Typography>
        </Box>
      ) : (
        <Box sx={{ mt: 2, flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          {/* Gráfico de barras simple */}
          <Box sx={{ display: 'flex', height: 30, mb: 2, borderRadius: 1, overflow: 'hidden' }}>
            {chartData.completed > 0 && (
              <Box 
                sx={{ 
                  width: `${completedPercentage}%`, 
                  bgcolor: colors.completed,
                  transition: 'width 1s ease-in-out'
                }} 
              />
            )}
            {chartData.processing > 0 && (
              <Box 
                sx={{ 
                  width: `${processingPercentage}%`, 
                  bgcolor: colors.processing,
                  transition: 'width 1s ease-in-out'
                }} 
              />
            )}
            {chartData.error > 0 && (
              <Box 
                sx={{ 
                  width: `${errorPercentage}%`, 
                  bgcolor: colors.error,
                  transition: 'width 1s ease-in-out'
                }} 
              />
            )}
          </Box>
          
          {/* Leyenda */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ width: 16, height: 16, bgcolor: colors.completed, mr: 1, borderRadius: 0.5 }} />
              <Typography variant="body2">
                Completados: {chartData.completed} ({completedPercentage}%)
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ width: 16, height: 16, bgcolor: colors.processing, mr: 1, borderRadius: 0.5 }} />
              <Typography variant="body2">
                En Procesamiento: {chartData.processing} ({processingPercentage}%)
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box sx={{ width: 16, height: 16, bgcolor: colors.error, mr: 1, borderRadius: 0.5 }} />
              <Typography variant="body2">
                Con Errores: {chartData.error} ({errorPercentage}%)
              </Typography>
            </Box>
          </Box>
        </Box>
      )}
    </Paper>
  )
}

export default StatusChart