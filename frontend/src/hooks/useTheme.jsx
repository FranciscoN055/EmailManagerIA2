import { createContext, useContext, useState, useEffect } from 'react';
import { createTheme } from '@mui/material/styles';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const createCustomTheme = (mode) => {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: '#0078d4',
        light: '#40a9ff',
        dark: '#106ebe',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#004578',
        light: '#0078d4',
        dark: '#003456',
        contrastText: '#ffffff',
      },
      error: {
        main: '#dc3545',
        light: '#e85d75',
        dark: '#c82333',
      },
      warning: {
        main: '#fd7e14',
        light: '#ff9f40',
        dark: '#e8590c',
      },
      info: {
        main: '#0078d4',
        light: '#40a9ff',
        dark: '#106ebe',
      },
      success: {
        main: '#198754',
        light: '#4caf50',
        dark: '#145a32',
      },
      background: {
        default: mode === 'light' ? '#f8f9fa' : '#1a1a1a',
        paper: mode === 'light' ? '#ffffff' : '#2d2d2d',
      },
      text: {
        primary: mode === 'light' ? '#1a1a1a' : '#ffffff',
        secondary: mode === 'light' ? '#6c757d' : '#adb5bd',
      },
      divider: mode === 'light' ? '#e9ecef' : '#495057',
    },
    typography: {
      fontFamily: '"Segoe UI", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontWeight: 600,
      },
      h2: {
        fontWeight: 600,
      },
      h3: {
        fontWeight: 600,
      },
      h4: {
        fontWeight: 600,
      },
      h5: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 600,
      },
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            boxShadow: mode === 'light' 
              ? '0 2px 8px rgba(0,0,0,0.1)' 
              : '0 2px 8px rgba(0,0,0,0.3)',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: mode === 'light'
                ? '0 4px 16px rgba(0,0,0,0.15)'
                : '0 4px 16px rgba(0,0,0,0.4)',
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: 6,
            fontWeight: 500,
          },
        },
      },
    },
  });
};

export const ThemeProvider = ({ children }) => {
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('email-manager-theme');
    return savedMode || 'light';
  });

  useEffect(() => {
    localStorage.setItem('email-manager-theme', mode);
  }, [mode]);

  const toggleMode = () => {
    setMode(prevMode => prevMode === 'light' ? 'dark' : 'light');
  };

  const theme = createCustomTheme(mode);

  return (
    <ThemeContext.Provider value={{ mode, toggleMode, theme }}>
      {children}
    </ThemeContext.Provider>
  );
};