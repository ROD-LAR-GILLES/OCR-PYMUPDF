import { useNavigate } from 'react-router-dom'
import {
  Paper,
  Typography,
  Box,
  Button,
  Grid,
  useTheme,
  useMediaQuery
} from '@mui/material'
import {
  UploadFile,
  Description,
  Settings,
  HelpOutline
} from '@mui/icons-material'

interface ActionButton {
  title: string;
  description: string;
  icon: JSX.Element;
  action: () => void;
  color: string;
}

const QuickActions = (): JSX.Element => {
  const navigate = useNavigate()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  
  const actionButtons: ActionButton[] = [
    {
      title: 'Subir PDF',
      description: 'Sube un nuevo documento PDF para procesarlo',
      icon: <UploadFile fontSize="large" />,
      action: () => navigate('/upload'),
      color: theme.palette.primary.main
    },
    {
      title: 'Mis Documentos',
      description: 'Ver todos tus documentos procesados',
      icon: <Description fontSize="large" />,
      action: () => navigate('/documents'),
      color: theme.palette.secondary.main
    },
    {
      title: 'Configuración',
      description: 'Ajusta las opciones de procesamiento',
      icon: <Settings fontSize="large" />,
      action: () => navigate('/settings'),
      color: theme.palette.info.main
    },
    {
      title: 'Ayuda',
      description: 'Consulta la documentación del proyecto',
      icon: <HelpOutline fontSize="large" />,
      action: () => window.open('https://github.com/robaguilera/OCR-PYMUPDF', '_blank'),
      color: theme.palette.warning.main
    }
  ]

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
        Acciones Rápidas
      </Typography>
      
      <Grid container spacing={2} sx={{ mt: 1, flexGrow: 1 }}>
        {actionButtons.map((button, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Button
              variant="outlined"
              fullWidth
              onClick={button.action}
              sx={{
                p: 2,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                borderWidth: 2,
                borderColor: button.color,
                '&:hover': {
                  borderWidth: 2,
                  borderColor: button.color,
                  backgroundColor: `${button.color}10`
                }
              }}
            >
              <Box 
                sx={{ 
                  color: button.color,
                  mb: 1,
                  display: 'flex',
                  justifyContent: 'center'
                }}
              >
                {button.icon}
              </Box>
              <Typography 
                variant={isMobile ? 'body1' : 'h6'} 
                component="div" 
                sx={{ color: 'text.primary', fontWeight: 'bold' }}
              >
                {button.title}
              </Typography>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ mt: 0.5, display: { xs: 'none', sm: 'block' } }}
              >
                {button.description}
              </Typography>
            </Button>
          </Grid>
        ))}
      </Grid>
    </Paper>
  )
}

export default QuickActions