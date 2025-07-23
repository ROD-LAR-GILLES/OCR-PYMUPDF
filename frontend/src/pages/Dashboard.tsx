import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Container,
  Alert,
  Skeleton,
  Button
} from '@mui/material'

import StatsCards from '../components/dashboard/StatsCards'
import StatusChart from '../components/dashboard/StatusChart'
import RecentActivity from '../components/dashboard/RecentActivity'
import QuickActions from '../components/dashboard/QuickActions'
import { getApiStatus } from '../services/apiService'

const Dashboard = (): JSX.Element => {
  const [apiConnected, setApiConnected] = useState<boolean | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const checkApiStatus = async () => {
      setLoading(true)
      try {
        const isConnected = await getApiStatus()
        setApiConnected(isConnected)
        setLoading(false)
      } catch (error) {
        console.error('Error al conectar con la API:', error)
        setApiConnected(false)
        setLoading(false)
      }
    }

    checkApiStatus()

    // Configurar un intervalo para verificar la conexión periódicamente si está desconectado
    let intervalId: number | undefined
    
    if (apiConnected === false) {
      intervalId = window.setInterval(() => {
        checkApiStatus()
      }, 30000) // Verificar cada 30 segundos
    }

    return () => {
      if (intervalId) {
        window.clearInterval(intervalId)
      }
    }
  }, [apiConnected])

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Skeleton para StatsCards */}
          <Grid item xs={12}>
            <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
          </Grid>
          
          {/* Skeleton para las tarjetas principales */}
          <Grid item xs={12} md={8}>
            <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
          </Grid>
          
          <Grid item xs={12}>
            <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />
          </Grid>
        </Grid>
      </Container>
    )
  }

  if (apiConnected === false) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 3, p: 3, borderRadius: 2 }}>
          <Typography variant="h6" component="h2" gutterBottom>
            Error de conexión
          </Typography>
          <Typography variant="body1" paragraph>
            No se pudo conectar con el servidor API. Por favor, verifica que el servidor esté en ejecución e intenta nuevamente.
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => window.location.reload()}
            sx={{ mt: 1 }}
          >
            Reintentar conexión
          </Button>
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Bienvenido al panel de control de OCR-PYMUPDF. Aquí puedes ver un resumen de tus documentos y acceder rápidamente a las funciones principales.
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        {/* Tarjetas de estadísticas */}
        <Grid item xs={12}>
          <StatsCards />
        </Grid>
        
        {/* Acciones rápidas y gráfico de estado */}
        <Grid item xs={12} md={8}>
          <QuickActions />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <StatusChart />
        </Grid>
        
        {/* Actividad reciente */}
        <Grid item xs={12}>
          <RecentActivity />
        </Grid>
      </Grid>

      {/* Mensaje de conexión exitosa */}
      {apiConnected && (
        <Alert severity="success" sx={{ mt: 3, borderRadius: 2 }} onClose={() => {}}>          
          Conectado al servidor API correctamente
        </Alert>
      )}
    </Container>
  )
}

export default Dashboard