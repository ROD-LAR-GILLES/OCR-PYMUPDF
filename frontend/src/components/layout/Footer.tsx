import { Box, Typography, Link, Container } from '@mui/material'

const Footer = (): JSX.Element => {
  const currentYear = new Date().getFullYear()

  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) =>
          theme.palette.mode === 'light'
            ? theme.palette.grey[100]
            : theme.palette.grey[900],
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {currentYear}
          {' '}
          <Link color="inherit" href="https://github.com/tu-usuario/OCR-PYMUPDF" target="_blank" rel="noopener">
            OCR-PYMUPDF
          </Link>
          {' - '}
          <span>Procesamiento de documentos PDF con OCR</span>
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          Desarrollado con PyMuPDF, Tesseract OCR y React
        </Typography>
      </Container>
    </Box>
  )
}

export default Footer