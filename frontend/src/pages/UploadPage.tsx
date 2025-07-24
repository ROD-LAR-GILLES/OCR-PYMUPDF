import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Button,
  FormControl,
  FormControlLabel,
  FormGroup,
  Checkbox,
  TextField,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Divider,
  Tooltip,
  IconButton,
  Chip,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material'
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  Settings as SettingsIcon,
  Check as CheckIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'

import { uploadPdf, uploadDocument } from '../services/apiService'
import { ProcessingOptions } from '../types'

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/tiff': ['.tif', '.tiff'],
}

const LANGUAGE_OPTIONS = [
  { value: 'auto', label: 'Detección automática' },
  { value: 'spa', label: 'Español' },
  { value: 'eng', label: 'Inglés' },
  { value: 'fra', label: 'Francés' },
  { value: 'deu', label: 'Alemán' },
  { value: 'por', label: 'Portugués' },
]

const DPI_OPTIONS = [
  { value: 0, label: 'Automático' },
  { value: 72, label: '72 DPI (Baja)' },
  { value: 150, label: '150 DPI (Media)' },
  { value: 300, label: '300 DPI (Alta)' },
  { value: 600, label: '600 DPI (Muy alta)' },
]

const LLM_PROVIDER_OPTIONS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'google', label: 'Google' },
  { value: 'deepseek', label: 'DeepSeek' },
]

const LLM_MODEL_OPTIONS = {
  openai: [
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  ],
  google: [
    { value: 'gemini-pro', label: 'Gemini Pro' },
  ],
  deepseek: [
    { value: 'deepseek-chat', label: 'DeepSeek Chat' },
    { value: 'deepseek-coder', label: 'DeepSeek Coder' },
  ],
}

const UploadPage = (): JSX.Element => {
  const navigate = useNavigate()
  const [activeStep, setActiveStep] = useState<number>(0)
  const [file, setFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const [options, setOptions] = useState<ProcessingOptions>({
    perform_ocr: true,
    detect_tables: true,
    extract_images: true,
    language: 'auto',
    dpi: 0,
    use_llm_refiner: false,
    llm_provider: 'openai',
    llm_model: 'gpt-3.5-turbo',
  })
  const [uploading, setUploading] = useState<boolean>(false)
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false)
  const [documentId, setDocumentId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Manejar el arrastre y soltar de archivos
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    
    const selectedFile = acceptedFiles[0]
    
    // Validar tamaño del archivo
    if (selectedFile.size > MAX_FILE_SIZE) {
      setFileError(`El archivo excede el tamaño máximo permitido (50MB).`)
      return
    }
    
    setFile(selectedFile)
    setFileError(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxFiles: 1,
    maxSize: MAX_FILE_SIZE,
    onDropRejected: (fileRejections) => {
      const rejection = fileRejections[0]
      if (rejection.errors[0].code === 'file-too-large') {
        setFileError(`El archivo excede el tamaño máximo permitido (50MB).`)
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        setFileError(`Tipo de archivo no soportado. Por favor, sube un archivo PDF, JPG, PNG o TIFF.`)
      } else {
        setFileError(`Error al subir el archivo: ${rejection.errors[0].message}`)
      }
    },
  })

  // Manejar cambios en las opciones
  const handleOptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked, value, type } = event.target
    
    setOptions(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  // Manejar cambios en opciones de selección
  const handleSelectChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target
    
    setOptions(prev => {
      const newOptions = { ...prev, [name]: value }
      
      // Si cambia el proveedor de LLM, actualizar el modelo por defecto
      if (name === 'llm_provider') {
        newOptions.llm_model = LLM_MODEL_OPTIONS[value as keyof typeof LLM_MODEL_OPTIONS][0].value
      }
      
      return newOptions
    })
  }

  // Eliminar el archivo seleccionado
  const handleRemoveFile = () => {
    setFile(null)
    setFileError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Manejar la subida del archivo
  const handleUpload = async () => {
    if (!file) {
      setFileError('Por favor, selecciona un archivo para subir.')
      return
    }

    setUploading(true)
    setUploadProgress(0)
    setUploadError(null)

    const formData = new FormData()
    formData.append('file', file)
    
    // Añadir opciones de procesamiento
    Object.entries(options).forEach(([key, value]) => {
      formData.append(key, value.toString())
    })

    try {
      const response = await uploadDocument(formData, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        setUploadProgress(progress)
      })

      setUploadSuccess(true)
      setDocumentId(response.data.id)
      setActiveStep(2) // Avanzar al paso de éxito
    } catch (err) {
      console.error('Error al subir el documento:', err)
      
      let errorMessage = 'Error al subir el documento. Por favor, intenta nuevamente.'
      
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 413) {
          errorMessage = 'El archivo es demasiado grande para ser procesado por el servidor.'
        } else if (err.response?.status === 415) {
          errorMessage = 'Tipo de archivo no soportado. Por favor, sube un archivo PDF, JPG, PNG o TIFF.'
        } else if (err.response?.data?.detail) {
          errorMessage = `Error: ${err.response.data.detail}`
        } else if (!err.response) {
          errorMessage = 'No se pudo establecer conexión con el servidor. Verifica tu conexión a internet.'
        }
      }
      
      setUploadError(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  // Navegar a la página de detalles del documento
  const handleViewDocument = () => {
    if (documentId) {
      navigate(`/documents/${documentId}`)
    }
  }

  // Navegar a la página de documentos
  const handleViewAllDocuments = () => {
    navigate('/documents')
  }

  // Reiniciar el formulario para subir otro documento
  const handleUploadAnother = () => {
    setFile(null)
    setFileError(null)
    setUploadSuccess(false)
    setDocumentId(null)
    setUploadProgress(0)
    setActiveStep(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Avanzar al siguiente paso
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1)
  }

  // Retroceder al paso anterior
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1)
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Subir documento
      </Typography>

      <Stepper activeStep={activeStep} orientation="vertical">
        {/* Paso 1: Selección de archivo */}
        <Step>
          <StepLabel>Seleccionar archivo</StepLabel>
          <StepContent>
            <Box sx={{ mb: 3 }}>
              <Typography variant="body1" gutterBottom>
                Selecciona un archivo PDF, JPG, PNG o TIFF para procesar.
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Tamaño máximo: 50MB
              </Typography>
            </Box>

            <Paper
              {...getRootProps()}
              sx={{
                p: 3,
                mb: 3,
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'divider',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: 'action.hover',
                },
              }}
            >
              <input {...getInputProps()} ref={fileInputRef} />
              <Box sx={{ textAlign: 'center' }}>
                <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="body1" gutterBottom>
                  {isDragActive
                    ? 'Suelta el archivo aquí...'
                    : 'Arrastra y suelta un archivo aquí, o haz clic para seleccionar'}
                </Typography>
              </Box>
            </Paper>

            {file && (
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.paper' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1, overflow: 'hidden' }}>
                    <Typography variant="body1" noWrap sx={{ mr: 1 }}>
                      {file.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </Typography>
                  </Box>
                  <IconButton onClick={handleRemoveFile} size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </Paper>
            )}

            {fileError && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {fileError}
              </Alert>
            )}

            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleNext}
                sx={{ mt: 1, mr: 1 }}
                disabled={!file}
                endIcon={<ArrowForwardIcon />}
              >
                Continuar
              </Button>
            </Box>
          </StepContent>
        </Step>

        {/* Paso 2: Opciones de procesamiento */}
        <Step>
          <StepLabel>Configurar opciones</StepLabel>
          <StepContent>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Opciones básicas
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={options.perform_ocr}
                        onChange={handleOptionChange}
                        name="perform_ocr"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body1">Realizar OCR</Typography>
                        <Tooltip title="Reconocimiento óptico de caracteres para extraer texto de imágenes y PDFs escaneados">
                          <IconButton size="small">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={options.detect_tables}
                        onChange={handleOptionChange}
                        name="detect_tables"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body1">Detectar tablas</Typography>
                        <Tooltip title="Identifica y extrae tablas del documento">
                          <IconButton size="small">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={options.extract_images}
                        onChange={handleOptionChange}
                        name="extract_images"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body1">Extraer imágenes</Typography>
                        <Tooltip title="Extrae las imágenes contenidas en el documento">
                          <IconButton size="small">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
                  />
                </FormGroup>

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" gutterBottom>
                  Opciones de OCR
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth margin="normal">
                      <TextField
                        select
                        label="Idioma"
                        name="language"
                        value={options.language}
                        onChange={handleSelectChange}
                        helperText="Selecciona el idioma principal del documento"
                        disabled={!options.perform_ocr}
                      >
                        {LANGUAGE_OPTIONS.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </TextField>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth margin="normal">
                      <TextField
                        select
                        label="Resolución (DPI)"
                        name="dpi"
                        value={options.dpi}
                        onChange={handleSelectChange}
                        helperText="Mayor resolución = mejor calidad pero más lento"
                        disabled={!options.perform_ocr}
                      >
                        {DPI_OPTIONS.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </TextField>
                    </FormControl>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  Refinamiento con IA
                  <Chip 
                    label="Experimental" 
                    color="warning" 
                    size="small" 
                    sx={{ ml: 1 }} 
                  />
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={options.use_llm_refiner}
                        onChange={handleOptionChange}
                        name="use_llm_refiner"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body1">Usar modelo de lenguaje para mejorar resultados</Typography>
                        <Tooltip title="Utiliza IA para corregir errores de OCR y mejorar el formato del texto extraído">
                          <IconButton size="small">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
                  />
                </FormGroup>

                {options.use_llm_refiner && (
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth margin="normal">
                        <TextField
                          select
                          label="Proveedor de IA"
                          name="llm_provider"
                          value={options.llm_provider}
                          onChange={handleSelectChange}
                          helperText="Selecciona el proveedor de IA"
                        >
                          {LLM_PROVIDER_OPTIONS.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </TextField>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth margin="normal">
                        <TextField
                          select
                          label="Modelo"
                          name="llm_model"
                          value={options.llm_model}
                          onChange={handleSelectChange}
                          helperText="Selecciona el modelo de IA a utilizar"
                        >
                          {LLM_MODEL_OPTIONS[options.llm_provider as keyof typeof LLM_MODEL_OPTIONS].map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </TextField>
                      </FormControl>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>

            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleUpload}
                sx={{ mt: 1, mr: 1 }}
                disabled={uploading}
                startIcon={<CloudUploadIcon />}
              >
                {uploading ? 'Subiendo...' : 'Subir documento'}
              </Button>
              <Button
                onClick={handleBack}
                sx={{ mt: 1, mr: 1 }}
                disabled={uploading}
              >
                Atrás
              </Button>
            </Box>

            {uploading && (
              <Box sx={{ mb: 3, mt: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Subiendo archivo... {uploadProgress}%
                </Typography>
                <LinearProgressWithLabel value={uploadProgress} />
              </Box>
            )}

            {uploadError && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {uploadError}
              </Alert>
            )}
          </StepContent>
        </Step>

        {/* Paso 3: Éxito */}
        <Step>
          <StepLabel>Documento subido</StepLabel>
          <StepContent>
            <Alert severity="success" sx={{ mb: 3 }}>
              <Typography variant="body1">
                ¡El documento se ha subido correctamente!
              </Typography>
              <Typography variant="body2">
                El procesamiento puede tardar unos minutos dependiendo del tamaño y complejidad del documento.
              </Typography>
            </Alert>

            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleViewDocument}
                sx={{ mt: 1, mr: 1 }}
                startIcon={<SettingsIcon />}
              >
                Ver detalles del documento
              </Button>
              <Button
                variant="outlined"
                onClick={handleViewAllDocuments}
                sx={{ mt: 1, mr: 1 }}
              >
                Ver todos los documentos
              </Button>
              <Button
                onClick={handleUploadAnother}
                sx={{ mt: 1, mr: 1 }}
                startIcon={<CloudUploadIcon />}
              >
                Subir otro documento
              </Button>
            </Box>
          </StepContent>
        </Step>
      </Stepper>
    </Box>
  )
}

// Componente para mostrar una barra de progreso con etiqueta
function LinearProgressWithLabel(props: { value: number }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box sx={{ width: '100%', mr: 1 }}>
        <CircularProgress variant="determinate" value={props.value} />
      </Box>
      <Box sx={{ minWidth: 35 }}>
        <Typography variant="body2" color="text.secondary">{`${Math.round(
          props.value,
        )}%`}</Typography>
      </Box>
    </Box>
  )
}

export default UploadPage