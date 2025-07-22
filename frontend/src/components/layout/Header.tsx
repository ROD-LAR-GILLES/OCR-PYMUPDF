import { useState, MouseEvent } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  AppBar,
  Box,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import AccountCircleIcon from '@mui/icons-material/AccountCircle'
import SettingsIcon from '@mui/icons-material/Settings'
import HelpIcon from '@mui/icons-material/Help'

interface HeaderProps {
  toggleDrawer: () => void;
}

const Header = ({ toggleDrawer }: HeaderProps): JSX.Element => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)
  
  const handleMenu = (event: MouseEvent<HTMLElement>): void => {
    setAnchorEl(event.currentTarget)
  }

  const handleClose = (): void => {
    setAnchorEl(null)
  }

  return (
    <AppBar position="sticky" color="primary" elevation={1}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={toggleDrawer}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: 'inherit',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          OCR-PYMUPDF
        </Typography>

        {!isMobile && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              color="inherit"
              component={RouterLink}
              to="/upload"
            >
              Subir PDF
            </Button>
            <Button
              color="inherit"
              component={RouterLink}
              to="/documents"
            >
              Mis Documentos
            </Button>
          </Box>
        )}

        <Box>
          <IconButton
            aria-label="cuenta de usuario"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
          >
            <AccountCircleIcon />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem
              component={RouterLink}
              to="/settings"
              onClick={handleClose}
            >
              <SettingsIcon fontSize="small" sx={{ mr: 1 }} />
              Configuración
            </MenuItem>
            <MenuItem
              component="a"
              href="https://github.com/tu-usuario/OCR-PYMUPDF"
              target="_blank"
              rel="noopener noreferrer"
              onClick={handleClose}
            >
              <HelpIcon fontSize="small" sx={{ mr: 1 }} />
              Ayuda
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Header