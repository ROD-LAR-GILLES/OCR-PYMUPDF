import { useState, useCallback, ChangeEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Button,
  Stepper,
  Step,
  StepLabel,
  FormControlLabel,
  Checkbox,
  TextField,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
} from '@mui/material'
import { useDropzone } from 'react-dropzone'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import SettingsIcon from '@mui/icons-material/Settings'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'

import { uploadPdf } from '../services/apiService'
import { ProcessingOptions, Document } from '../types'

interface UploadOptions extends ProcessingOptions {
  language: string;
  dpi: number;
  perform_ocr?: boolean;
  detect_tables?: boolean;
  extract_images?: boolean;
}

const UploadPage = (): JSX.Element => {
  const navigate = useNavigate()
  const [activeStep, setActiveStep] = useState<number>(0)
  const [file, setFile] = useState<File | null>(null)
  const [options, setOptions] = useState<UploadOptions>({
    perform_ocr: true,
    detect_tables: true,
    extract_images: false,
    language: 'spa',
    dpi: 300,
  })
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedDocId, setUploadedDocId] = useState<string | null>(null)

  // Configuración de react-dropzone
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0]
      // Verificar que sea un PDF
      if (selectedFile.type !== 'application/pdf') {
        setError('Solo se permiten archivos PDF')
        return
      }
      
      setFile(selectedFile)
      setError(null)
      setActiveStep(1) // Avanzar al siguiente paso
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  })

  // Manejar cambios en las opciones
  const handleOptionChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, checked, value, type } = event.target
    setOptions({
      ...options,
      [name]: type === 'checkbox' ? checked : value,
    })
  }

  // Manejar el envío del formulario
  const handleSubmit = async (): Promise<void> => {
    if (!file) return
    
    try {
      setLoading(true)
      setError(null)
      
      const response = await uploadPdf(file, options)
      setUploadedDocId((response.data as Document).id)
      setActiveStep(2) // Avanzar al paso final
    } catch (err) {
      console.error('Error al subir el documento:', err)
      setError('Error al subir el documento. Por favor, intenta nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  // Reiniciar el proceso
  const handleReset = (): void => {
    setFile(null)
    setActiveStep(0)
    setError(null)
    setUploadedDocId(null)
  }

  // Pasos del proceso
  const steps = ['Seleccionar archivo', 'Configurar opciones', 'Completado']

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Subir documento PDF
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {activeStep === 0 && (
        <Paper
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Box
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'active' : ''}`}
            sx={{
              width: '100%',
              maxWidth: 600,
              mb: 3,
            }}
          >
            <input {...getInputProps()} />
            <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" align="center" gutterBottom>
              {isDragActive
                ? 'Suelta el archivo aquí'
                : 'Arrastra y suelta un archivo PDF aquí, o haz clic para seleccionarlo'}
            </Typography>
            <Typography variant="body2" align="center" color="text.secondary">
              Tamaño máximo: 50MB
            </Typography>
          </Box>

          <Card sx={{ width: '100%', maxWidth: 600, mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ¿Qué puedes hacer con OCR-PYMUPDF?
              </Typography>
              <Typography variant="body2" paragraph>
                Sube un documento PDF y conviértelo a texto con reconocimiento óptico de caracteres (OCR).
                Ideal para documentos escaneados o imágenes de texto.
              </Typography>
              <Typography variant="body2">
                Características:
              </Typography>
              <ul>
                <li>Extracción de texto con OCR</li>
                <li>Detección de tablas</li>
                <li>Extracción de imágenes</li>
                <li>Soporte para múltiples idiomas</li>
              </ul>
            </CardContent>
          </Card>
        </Paper>
      )}

      {activeStep === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom>
            Archivo seleccionado: <strong>{file?.name}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Tamaño: {(file && file.size ? (file.size / 1024 / 1024).toFixed(2) : '0')} MB
          </Typography>

          <Divider sx={{ my: 3 }} />

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <SettingsIcon sx={{ mr: 1 }} /> Opciones de procesamiento
            </Typography>

            <Box sx={{ ml: 2 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={options.perform_ocr}
                    onChange={handleOptionChange}
                    name="perform_ocr"
                  />
                }
                label="Realizar OCR (reconocimiento de texto)"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={options.detect_tables}
                    onChange={handleOptionChange}
                    name="detect_tables"
                  />
                }
                label="Detectar tablas"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={options.extract_images}
                    onChange={handleOptionChange}
                    name="extract_images"
                  />
                }
                label="Extraer imágenes"
              />

              <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <TextField
                  select
                  label="Idioma"
                  name="language"
                  value={options.language}
                  onChange={handleOptionChange}
                  SelectProps={{
                    native: true,
                  }}
                  sx={{ width: 200 }}
                >
                  <option value="spa">Español</option>
                  <option value="eng">Inglés</option>
                  <option value="fra">Francés</option>
                  <option value="deu">Alemán</option>
                  <option value="por">Portugués</option>
                </TextField>

                <TextField
                  type="number"
                  label="DPI (calidad)"
                  name="dpi"
                  value={options.dpi}
                  onChange={handleOptionChange}
                  InputProps={{ inputProps: { min: 72, max: 600 } }}
                  sx={{ width: 200 }}
                />
              </Box>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button onClick={handleReset} variant="outlined">
              Volver
            </Button>
            <Button
              onClick={handleSubmit}
              variant="contained"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Procesando...' : 'Procesar documento'}
            </Button>
          </Box>
        </Paper>
      )}

      {activeStep === 2 && (
        <Paper
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <CheckCircleIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom align="center">
            ¡Documento subido correctamente!
          </Typography>
          <Typography variant="body1" paragraph align="center">
            Tu documento está siendo procesado. Puedes ver su estado en la página de detalles.
          </Typography>

          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, gap: 2 }}>
            <Button
              variant="outlined"
              onClick={handleReset}
            >
              Subir otro documento
            </Button>
            <Button
              variant="contained"
              onClick={() => navigate(`/documents/${uploadedDocId}`)}
            >
              Ver detalles del documento
            </Button>
          </Box>
        </Paper>
      )}
    </Box>
  )
}

export default UploadPage