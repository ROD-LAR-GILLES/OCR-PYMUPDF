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
      }
    };

    loadThemePreference();
  }, []);

  // Cambiar entre temas claro y oscuro
  const toggleTheme = async () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    
    // Guardar preferencia en la API
    try {
      await updateUserPreferences({
        dark_mode: newMode === 'dark'
      });
    } catch (error) {
      console.error('Error al guardar preferencia de tema:', error);
    }
  };

  // Crear tema de Material UI según el modo
  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: '#3f51b5',
      },
      secondary: {
        main: '#f50057',
      },
      background: {
        default: mode === 'light' ? '#f5f5f5' : '#121212',
        paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
      },
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
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 8,
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