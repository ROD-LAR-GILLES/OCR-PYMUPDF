import { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';
import { getUserPreferences, updateUserPreferences } from '../services/apiService';

type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme debe ser usado dentro de un ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider = ({ children }: ThemeProviderProps): JSX.Element => {
  const [mode, setMode] = useState<ThemeMode>('light');

  // Cargar preferencia de tema al iniciar
  useEffect(() => {
    const loadThemePreference = async () => {
      try {
        const preferences = await getUserPreferences();
        setMode(preferences.dark_mode ? 'dark' : 'light');
      } catch (error) {
        console.error('Error al cargar preferencias de tema:', error);
        // Si hay un error al cargar las preferencias, intentar usar la preferencia guardada en localStorage
        const savedMode = localStorage.getItem('themeMode');
        if (savedMode === 'dark' || savedMode === 'light') {
          setMode(savedMode);
        }
      }
    };

    loadThemePreference();
  }, []);

  // Cambiar entre temas claro y oscuro
  const toggleTheme = async () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    
    // Guardar preferencia en localStorage para persistencia local
    localStorage.setItem('themeMode', newMode);
    
    // Guardar preferencia en la API
    try {
      await updateUserPreferences({
        dark_mode: newMode === 'dark'
      });
    } catch (error) {
      console.error('Error al guardar preferencia de tema:', error);
    }
  };

  // Aplicar el atributo data-theme al elemento HTML cuando cambie el tema
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', mode);
  }, [mode]);

  // Crear tema de Material UI según el modo
  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'light' ? '#3f51b5' : '#5c6bc0',
        dark: mode === 'light' ? '#303f9f' : '#3949ab',
        light: mode === 'light' ? '#7986cb' : '#8c9eff',
      },
      secondary: {
        main: mode === 'light' ? '#f50057' : '#ff4081',
      },
      background: {
        default: mode === 'light' ? '#f5f5f5' : '#121212',
        paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
      },
      text: {
        primary: mode === 'light' ? 'rgba(0, 0, 0, 0.87)' : 'rgba(255, 255, 255, 0.87)',
        secondary: mode === 'light' ? 'rgba(0, 0, 0, 0.6)' : 'rgba(255, 255, 255, 0.6)',
      },
      divider: mode === 'light' ? 'rgba(0, 0, 0, 0.12)' : 'rgba(255, 255, 255, 0.12)',
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontSize: '2.5rem',
        fontWeight: 500,
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 500,
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            transition: 'background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            transition: 'background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            transition: 'background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease',
            boxShadow: mode === 'light' 
              ? '0px 2px 4px rgba(0, 0, 0, 0.1)' 
              : '0px 2px 4px rgba(0, 0, 0, 0.5)',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: mode === 'light' 
              ? '0px 2px 4px rgba(0, 0, 0, 0.1)' 
              : '0px 2px 4px rgba(0, 0, 0, 0.5)',
          },
        },
      },
      MuiSwitch: {
        styleOverrides: {
          switchBase: {
            color: mode === 'light' ? '#f5f5f5' : '#5c6bc0',
          },
          track: {
            backgroundColor: mode === 'light' ? '#e0e0e0' : '#424242',
          },
        },
      },
    },
  });

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};