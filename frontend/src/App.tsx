import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, Container, CircularProgress } from '@mui/material'

// Componentes
import Header from './components/layout/Header'
import Footer from './components/layout/Footer'
import Sidebar from './components/layout/Sidebar'

// Páginas
import Dashboard from './pages/Dashboard'
import UploadPage from './pages/UploadPage'
import DocumentsPage from './pages/DocumentsPage'
import DocumentDetailPage from './pages/DocumentDetailPage'
import SettingsPage from './pages/SettingsPage'
import NotFoundPage from './pages/NotFoundPage'

// Servicios
import { checkApiHealth } from './services/apiService'

function App(): JSX.Element {
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false)
  const [apiConnected, setApiConnected] = useState<boolean | null>(null)
  
  // Verificar conexión con la API al cargar
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await checkApiHealth()
        setApiConnected(true)
      } catch (error) {
        console.error('Error al conectar con la API:', error)
        setApiConnected(false)
      }
    }
    
    checkConnection()
  }, [])
  
  // Manejar apertura/cierre del menú lateral
  const toggleDrawer = (): void => {
    setDrawerOpen(!drawerOpen)
  }

  // Mostrar pantalla de carga mientras se verifica la conexión
  if (apiConnected === null) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <CircularProgress />
        <Box>Conectando con el servidor...</Box>
      </Box>
    )
  }

  // Mostrar mensaje de error si no hay conexión
  if (apiConnected === false) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column',
          gap: 2,
          p: 3,
          textAlign: 'center'
        }}
      >
        <Box sx={{ color: 'error.main', fontSize: 'h4.fontSize', fontWeight: 'bold' }}>
          Error de conexión
        </Box>
        <Box>
          No se pudo conectar con el servidor API. Por favor, verifica que el servidor esté en ejecución
          e intenta nuevamente.
        </Box>
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header toggleDrawer={toggleDrawer} />
      <Sidebar open={drawerOpen} onClose={toggleDrawer} />
      
      <Box component="main" sx={{ flexGrow: 1, py: 3 }}>
        <Container maxWidth="lg">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/documents/:id" element={<DocumentDetailPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Container>
      </Box>
      
      <Footer />
    </Box>
  )
}

export default App