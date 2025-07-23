import { useState, useEffect, ChangeEvent } from 'react'
import {
  Box,
  Typography,
  Paper,
  Divider,
  FormControl,
  FormControlLabel,
  FormGroup,
  Switch,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Grid,
  MenuItem,
  Select,
  InputLabel,
  Card,
  CardContent,
  Snackbar,
  SelectChangeEvent,
} from '@mui/material'
import SaveIcon from '@mui/icons-material/Save'

import { getUserPreferences, updateUserPreferences } from '../services/apiService'
import { UserPreferences } from '../types'
import { useTheme } from '../context/ThemeContext'

const SettingsPage = (): JSX.Element => {
  const { mode, toggleTheme } = useTheme();
  const [preferences, setPreferences] = useState<UserPreferences>({
    default_language: 'spa',
    default_dpi: 300,
    auto_detect_tables: true,
    extract_images: false,
    dark_mode: mode === 'dark',
    notifications_enabled: true,
  })
  const [loading, setLoading] = useState<boolean>(true)
  const [saving, setSaving] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<boolean>(false)

  // Cargar preferencias del usuario
  useEffect(() => {
    const fetchPreferences = async (): Promise<void> => {
      try {
        setLoading(true)
        const data = await getUserPreferences()
        // Asegurarse de que el modo oscuro esté sincronizado con el contexto del tema
        setPreferences({
          ...data,
          dark_mode: mode === 'dark'
        })
        setError(null)
      } catch (err) {
        console.error('Error al cargar preferencias:', err)
        setError('No se pudieron cargar las preferencias. Se usarán los valores predeterminados.')
        // Usar valores predeterminados y sincronizar con el tema actual
        setPreferences(prev => ({
          ...prev,
          dark_mode: mode === 'dark'
        }))
      } finally {
        setLoading(false)
      }
    }

    fetchPreferences()
  }, [mode])

  // Manejar cambios en los campos
  const handleChange = (event: ChangeEvent<HTMLInputElement> | SelectChangeEvent): void => {
    const { name, value, checked, type } = event.target as HTMLInputElement
    const isCheckbox = type === 'checkbox';
    const newValue = isCheckbox ? checked : value;
    
    // Si es el switch de modo oscuro, también actualizar el contexto del tema
    if (name === 'dark_mode' && isCheckbox) {
      toggleTheme();
    }
    
    setPreferences({
      ...preferences,
      [name]: newValue,
    })
  }

  // Manejar cambio numérico
  const handleNumberChange = (event: ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = event.target
    const numValue = parseInt(value, 10)
    if (!isNaN(numValue)) {
      setPreferences({
        ...preferences,
        [name]: numValue,
      })
    }
  }

  // Guardar preferencias
  const handleSave = async (): Promise<void> => {
    try {
      setSaving(true)
      // Guardar las preferencias sin incluir el modo oscuro, ya que se maneja a través del contexto del tema
      const { dark_mode, ...preferencesToSave } = preferences;
      await updateUserPreferences({
        ...preferencesToSave,
        dark_mode: mode === 'dark' // Asegurarse de que el valor guardado coincida con el contexto actual
      })
      setSuccess(true)
      setError(null)
    } catch (err) {
      console.error('Error al guardar preferencias:', err)
      setError('No se pudieron guardar las preferencias. Por favor, intenta nuevamente.')
    } finally {
      setSaving(false)
    }
  }

  // Cerrar alerta de éxito
  const handleCloseSuccess = (): void => {
    setSuccess(false)
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Configuración
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSuccess}
        message="Preferencias guardadas correctamente"
      />

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Preferencias de procesamiento
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="default-language-label">Idioma predeterminado</InputLabel>
                <Select
                  labelId="default-language-label"
                  name="default_language"
                  value={preferences.default_language}
                  onChange={handleChange}
                  label="Idioma predeterminado"
                >
                  <MenuItem value="spa">Español</MenuItem>
                  <MenuItem value="eng">Inglés</MenuItem>
                  <MenuItem value="fra">Francés</MenuItem>
                  <MenuItem value="deu">Alemán</MenuItem>
                  <MenuItem value="por">Portugués</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="DPI predeterminado"
                name="default_dpi"
                type="number"
                value={preferences.default_dpi}
                onChange={handleNumberChange}
                InputProps={{ inputProps: { min: 72, max: 600 } }}
                sx={{ mb: 3 }}
              />

              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.auto_detect_tables}
                      onChange={handleChange}
                      name="auto_detect_tables"
                    />
                  }
                  label="Detectar tablas automáticamente"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.extract_images}
                      onChange={handleChange}
                      name="extract_images"
                    />
                  }
                  label="Extraer imágenes por defecto"
                />
              </FormGroup>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Preferencias de interfaz
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.dark_mode}
                      onChange={handleChange}
                      name="dark_mode"
                    />
                  }
                  label="Modo oscuro"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.notifications_enabled}
                      onChange={handleChange}
                      name="notifications_enabled"
                    />
                  }
                  label="Habilitar notificaciones"
                />
              </FormGroup>
            </Paper>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Acerca de OCR-PYMUPDF
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body2" paragraph>
                  OCR-PYMUPDF es una herramienta para procesar documentos PDF utilizando reconocimiento óptico de caracteres (OCR).
                </Typography>
                <Typography variant="body2" paragraph>
                  Versión: 1.0.0
                </Typography>
                <Typography variant="body2">
                  Desarrollado con PyMuPDF, Tesseract OCR y React.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Guardando...' : 'Guardar preferencias'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      )}
    </Box>
  )
}

export default SettingsPage