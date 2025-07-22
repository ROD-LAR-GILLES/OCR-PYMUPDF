import { useLocation, useNavigate } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
} from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DescriptionIcon from '@mui/icons-material/Description'
import SettingsIcon from '@mui/icons-material/Settings'
import InfoIcon from '@mui/icons-material/Info'
import { ReactElement } from 'react'

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface MenuItem {
  text: string;
  icon: ReactElement;
  path: string;
}

const Sidebar = ({ open, onClose }: SidebarProps): JSX.Element => {
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems: MenuItem[] = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Subir PDF', icon: <UploadFileIcon />, path: '/upload' },
    { text: 'Mis Documentos', icon: <DescriptionIcon />, path: '/documents' },
    { text: 'Configuración', icon: <SettingsIcon />, path: '/settings' },
  ]

  const handleNavigation = (path: string): void => {
    navigate(path)
    onClose()
  }

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: { xs: '80%', sm: 280 },
          boxSizing: 'border-box',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
          OCR-PYMUPDF
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Procesamiento de documentos PDF
        </Typography>
      </Box>

      <Divider />

      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

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
    </Drawer>
  )
}

export default Sidebar