import { Link as RouterLink } from 'react-router-dom'
import { Box, Typography, Button, Paper } from '@mui/material'
import {
  Error as ErrorIcon,
  Home as HomeIcon,
} from '@mui/icons-material'

const NotFoundPage = (): JSX.Element => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
        p: 3,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          maxWidth: 500,
          width: '100%',
        }}
      >
        <ErrorIcon color="error" sx={{ fontSize: 80, mb: 2 }} />
        <Typography variant="h4" component="h1" gutterBottom>
          Página no encontrada
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Lo sentimos, la página que estás buscando no existe o ha sido movida.
        </Typography>
        <Button
          variant="contained"
          component={RouterLink}
          to="/"
          startIcon={<HomeIcon />}
          sx={{ mt: 2 }}
        >
          Volver al inicio
        </Button>
      </Paper>
    </Box>
  )
}

export default NotFoundPage