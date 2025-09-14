import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useEffect } from 'react';

// Importar páginas
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Callback from './pages/Callback';

// Importar nuestro tema personalizado
import { ThemeProvider, useTheme } from './hooks/useTheme.jsx';

// Importar keep alive
import { keepAlive } from './services/api.js';

// Crear cliente de React Query
const queryClient = new QueryClient();

// Componente envoltorio para usar el tema
const AppContent = () => {
  const { theme } = useTheme();
  
  // Activar keep alive para mantener el servidor despierto
  useEffect(() => {
    keepAlive();
  }, []);
  
  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/auth/callback" element={<Callback />} />
          </Routes>
        </div>
      </Router>
    </MuiThemeProvider>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;