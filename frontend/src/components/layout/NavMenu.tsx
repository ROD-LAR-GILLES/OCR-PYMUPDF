import { useLocation, useNavigate } from 'react-router-dom'
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Tooltip,
  Badge
} from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DescriptionIcon from '@mui/icons-material/Description'
import SettingsIcon from '@mui/icons-material/Settings'
import InfoIcon from '@mui/icons-material/Info'
import { ReactElement } from 'react'

interface MenuItem {
  text: string;
  icon: ReactElement;
  path: string;
  badge?: number;
  tooltip?: string;
}

interface NavMenuProps {
  onNavigate?: () => void;
  variant?: 'sidebar' | 'header';
}

const NavMenu = ({ onNavigate, variant = 'sidebar' }: NavMenuProps): JSX.Element => {
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems: MenuItem[] = [
    { 
      text: 'Dashboard', 
      icon: <DashboardIcon />, 
      path: '/dashboard',
      tooltip: 'Panel principal con resumen de actividad'
    },
    { 
      text: 'Subir PDF', 
      icon: <UploadFileIcon />, 
      path: '/upload',
      tooltip: 'Subir y procesar nuevos documentos PDF'
    },
    { 
      text: 'Mis Documentos', 
      icon: <DescriptionIcon />, 
      path: '/documents',
      badge: 0, // Este valor podría ser dinámico basado en documentos pendientes
      tooltip: 'Ver y gestionar documentos procesados'
    },
    { 
      text: 'Configuración', 
      icon: <SettingsIcon />, 
      path: '/settings',
      tooltip: 'Ajustar preferencias del sistema'
    },
  ]

  const handleNavigation = (path: string): void => {
    navigate(path)
    if (onNavigate) {
      onNavigate()
    }
  }

  const isCompact = variant === 'header'

  return (
    <Box sx={{ width: '100%' }}>
      {!isCompact && (
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            OCR-PYMUPDF
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Procesamiento de documentos PDF
          </Typography>
        </Box>
      )}

      {!isCompact && <Divider />}

      <List sx={isCompact ? { display: 'flex' } : {}}>
        {menuItems.map((item) => (
          <Tooltip key={item.text} title={item.tooltip || ''} placement={isCompact ? 'bottom' : 'right'}>
            <ListItem 
              disablePadding 
              sx={isCompact ? { width: 'auto' } : {}}
            >
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => handleNavigation(item.path)}
                sx={isCompact ? { px: 2 } : {}}
              >
                <ListItemIcon>
                  {item.badge ? (
                    <Badge badgeContent={item.badge} color="primary">
                      {item.icon}
                    </Badge>
                  ) : (
                    item.icon
                  )}
                </ListItemIcon>
                {!isCompact && <ListItemText primary={item.text} />}
              </ListItemButton>
            </ListItem>
          </Tooltip>
        ))}
      </List>

      {!isCompact && <Divider />}

      {!isCompact && (
        <List>
          <ListItem disablePadding>
            <ListItemButton
              component="a"
              href="https://github.com/tu-usuario/OCR-PYMUPDF"
              target="_blank"
              rel="noopener noreferrer"
            >
              <ListItemIcon>
                <InfoIcon />
              </ListItemIcon>
              <ListItemText primary="Acerca de" />
            </ListItemButton>
          </ListItem>
        </List>
      )}
    </Box>
  )
}

export default NavMenu