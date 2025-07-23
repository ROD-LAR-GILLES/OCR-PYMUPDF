import { Drawer } from '@mui/material'
import NavMenu from './NavMenu'

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const Sidebar = ({ open, onClose }: SidebarProps): JSX.Element => {

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
      <NavMenu onNavigate={onClose} variant="sidebar" />
    </Drawer>
  )
}

export default Sidebar