import { Container, Paper, Typography, Button, Box } from '@mui/material';
import { Microsoft } from '@mui/icons-material';
import { microsoftAPI } from '../services/api';

const Login = () => {
  const handleMicrosoftLogin = async () => {
    try {
      console.log('Obteniendo URL de autenticación de Microsoft...');
      console.log('API URL:', import.meta.env.VITE_API_URL);
      console.log('Full API URL:', `${import.meta.env.VITE_API_URL}/microsoft/auth/login`);
      
      const response = await microsoftAPI.getAuthUrl();
      console.log('Response received:', response);
      const authUrl = response.data.auth_url;
      
      // Redirigir a Microsoft para autenticación
      window.location.href = authUrl;
    } catch (error) {
      console.error('Error al obtener URL de autenticación:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error status:', error.response?.status);
      alert('Error al conectar con Microsoft. Por favor, verifica que el servidor esté funcionando.');
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography component="h1" variant="h4" gutterBottom>
              Email Manager IA
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Conecta tu cuenta de Outlook para comenzar
            </Typography>
          </Box>

          <Box sx={{ mt: 3 }}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<Microsoft />}
              onClick={handleMicrosoftLogin}
              sx={{
                py: 1.5,
                backgroundColor: '#0078d4',
                '&:hover': {
                  backgroundColor: '#106ebe',
                },
              }}
            >
              Conectar con Microsoft Outlook
            </Button>
          </Box>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Al conectar tu cuenta, autorizas a Email Manager IA a acceder 
              y analizar tus correos para organizarlos por urgencia.
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;