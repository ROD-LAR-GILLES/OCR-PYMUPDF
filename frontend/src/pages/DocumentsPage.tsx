import { useState, useEffect, ChangeEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Button,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import VisibilityIcon from '@mui/icons-material/Visibility'
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import AddIcon from '@mui/icons-material/AddCircleOutline'

import { getDocuments, deleteDocument, downloadDocument } from '../services/apiService'
import { Document } from '../types'

const DocumentsPage = (): JSX.Element => {
  const navigate = useNavigate()
  const [documents, setDocuments] = useState<Document[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false)
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(null)

  // Cargar documentos
  useEffect(() => {
    const fetchDocuments = async (): Promise<void> => {
      try {
        setLoading(true)
        const data = await getDocuments()
        setDocuments(data)
        setFilteredDocuments(data)
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

  // Filtrar documentos cuando cambia el término de búsqueda
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredDocuments(documents)
    } else {
      const filtered = documents.filter((doc) =>
        doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredDocuments(filtered)
    }
  }, [searchTerm, documents])

  // Manejar búsqueda
  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value)
  }

  // Manejar eliminación de documento
  const handleDeleteClick = (document: Document): void => {
    setDocumentToDelete(document)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async (): Promise<void> => {
    if (!documentToDelete) return

    try {
      await deleteDocument(documentToDelete.id)
      setDocuments(documents.filter((doc) => doc.id !== documentToDelete.id))
      setDeleteDialogOpen(false)
      setDocumentToDelete(null)
    } catch (err) {
      console.error('Error al eliminar el documento:', err)
      setError('No se pudo eliminar el documento. Por favor, intenta nuevamente.')
    }
  }

  const handleDeleteCancel = (): void => {
    setDeleteDialogOpen(false)
    setDocumentToDelete(null)
  }

  // Manejar descarga de documento
  const handleDownload = async (documentId: string, filename: string): Promise<void> => {
    try {
      const blob = await downloadDocument(documentId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename.replace('.pdf', '.md')
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Error al descargar el documento:', err)
      setError('No se pudo descargar el documento. Por favor, intenta nuevamente.')
    }
  }

  // Obtener chip de estado
  const getStatusChip = (status: string): JSX.Element => {
    switch (status) {
      case 'completed':
        return <Chip label="Completado" color="success" size="small" />
      case 'processing':
        return <Chip label="Procesando" color="warning" size="small" />
      case 'error':
        return <Chip label="Error" color="error" size="small" />
      default:
        return <Chip label="Desconocido" size="small" />
    }
  }

  // Formatear fecha
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Mis Documentos
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/upload')}
        >
          Nuevo documento
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Buscar por nombre de archivo..."
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      <TableContainer component={Paper}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : filteredDocuments.length > 0 ? (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Fecha de creación</TableCell>
                <TableCell align="right">Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredDocuments.map((doc) => (
                <TableRow key={doc.id} hover className="document-list-item">
                  <TableCell>{doc.filename}</TableCell>
                  <TableCell>{getStatusChip(doc.status)}</TableCell>
                  <TableCell>{formatDate(doc.created_at)}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      color="primary"
                      onClick={() => navigate(`/documents/${doc.id}`)}
                      title="Ver detalles"
                    >
                      <VisibilityIcon />
                    </IconButton>
                    {doc.status === 'completed' && (
                      <IconButton
                        color="primary"
                        onClick={() => handleDownload(doc.id, doc.filename)}
                        title="Descargar"
                      >
                        <DownloadIcon />
                      </IconButton>
                    )}
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteClick(doc)}
                      title="Eliminar"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              {searchTerm
                ? 'No se encontraron documentos que coincidan con la búsqueda.'
                : 'No hay documentos disponibles. ¡Sube tu primer documento!'}
            </Typography>
            {!searchTerm && (
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/upload')}
                sx={{ mt: 2 }}
              >
                Subir documento
              </Button>
            )}
          </Box>
        )}
      </TableContainer>

      {/* Diálogo de confirmación para eliminar */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>Confirmar eliminación</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Estás seguro de que deseas eliminar el documento "{documentToDelete?.filename}"?
            Esta acción no se puede deshacer.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancelar</Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DocumentsPage