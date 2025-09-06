import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Avatar,
  IconButton,
  Badge,
  Chip,
  Paper,
  InputAdornment,
  Menu,
  MenuList,
  MenuItem as MenuItemComponent,
} from '@mui/material';
import {
  Search,
  FilterList,
  Notifications,
  AccountCircle,
  Refresh,
} from '@mui/icons-material';
import EmailColumn from '../components/email/EmailColumn';
import ThemeToggle from '../components/common/ThemeToggle';
import PriorityProgressBar from '../components/common/PriorityProgressBar';
import { generateMockEmails, getEmailsByUrgency, getEmailStats } from '../utils/mockData';

const Dashboard = () => {
  const [emails, setEmails] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterBy, setFilterBy] = useState('all');
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [profileAnchor, setProfileAnchor] = useState(null);
  const [stats, setStats] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const columns = [
    { id: 'urgent', urgency: 'urgent', title: 'Urgente', subtitle: 'Próxima hora' },
    { id: 'high', urgency: 'high', title: 'Alta Prioridad', subtitle: 'Próximas 3 horas' },
    { id: 'medium', urgency: 'medium', title: 'Prioridad Media', subtitle: 'Hoy' },
    { id: 'low', urgency: 'low', title: 'Baja Prioridad', subtitle: 'Mañana' },
    { id: 'processed', urgency: 'processed', title: 'Procesados', subtitle: 'Completados' },
  ];

  useEffect(() => {
    loadEmails();
  }, []);

  useEffect(() => {
    setStats(getEmailStats(emails));
  }, [emails]);

  const loadEmails = () => {
    setIsLoading(true);
    setTimeout(() => {
      const mockEmails = generateMockEmails();
      setEmails(mockEmails);
      setIsLoading(false);
    }, 500);
  };

  const handleMarkAsRead = (emailId) => {
    setEmails(prevEmails =>
      prevEmails.map(email =>
        email.id === emailId ? { ...email, isRead: true } : email
      )
    );
  };

  const handleArchive = (emailId) => {
    setEmails(prevEmails =>
      prevEmails.map(email =>
        email.id === emailId ? { ...email, urgency: 'processed', isRead: true } : email
      )
    );
  };

  const handleToggleStar = (emailId) => {
    setEmails(prevEmails =>
      prevEmails.map(email =>
        email.id === emailId ? { ...email, isStarred: !email.isStarred } : email
      )
    );
  };

  const filteredEmails = emails.filter(email => {
    const matchesSearch = email.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         email.sender.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (filterBy === 'all') return matchesSearch;
    if (filterBy === 'unread') return matchesSearch && !email.isRead;
    if (filterBy === 'starred') return matchesSearch && email.isStarred;
    return matchesSearch;
  });

  return (
    <Box sx={{ flexGrow: 1, height: '100vh', backgroundColor: 'background.default' }}>
      {/* Header/AppBar */}
      <AppBar 
        position="fixed" 
        elevation={2} 
        sx={{ 
          backgroundColor: 'primary.main',
          zIndex: 1200,
          height: 60
        }}
      >
        <Toolbar sx={{ minHeight: '60px !important', px: 2 }}>
          <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 3, fontWeight: 600, fontSize: '1.1rem' }}>
            📧 Email Manager IA
          </Typography>
          
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
            {/* Barra de búsqueda */}
            <TextField
              variant="outlined"
              placeholder="Buscar correos..."
              size="small"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{
                minWidth: 250,
                backgroundColor: 'rgba(255,255,255,0.1)',
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': {
                    borderColor: 'rgba(255,255,255,0.3)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(255,255,255,0.5)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'white',
                  },
                },
                '& .MuiInputBase-input::placeholder': {
                  color: 'rgba(255,255,255,0.7)',
                  opacity: 1,
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: 'rgba(255,255,255,0.7)' }} />
                  </InputAdornment>
                ),
              }}
            />
            
            {/* Filtros */}
            <FormControl size="small" sx={{ minWidth: 100 }}>
              <InputLabel sx={{ color: 'rgba(255,255,255,0.7)' }}>Filtrar</InputLabel>
              <Select
                value={filterBy}
                label="Filtrar"
                onChange={(e) => setFilterBy(e.target.value)}
                sx={{
                  color: 'white',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(255,255,255,0.3)',
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(255,255,255,0.5)',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'white',
                  },
                  '& .MuiSvgIcon-root': {
                    color: 'rgba(255,255,255,0.7)',
                  },
                }}
              >
                <MenuItem value="all">Todos</MenuItem>
                <MenuItem value="unread">Sin leer</MenuItem>
                <MenuItem value="starred">Destacados</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Acciones del header */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit" onClick={loadEmails} disabled={isLoading}>
              <Refresh sx={{ animation: isLoading ? 'spin 1s linear infinite' : 'none' }} />
            </IconButton>
            
            <ThemeToggle />
            
            <IconButton
              color="inherit"
              onClick={(e) => setNotificationAnchor(e.currentTarget)}
            >
              <Badge badgeContent={stats.unread || 0} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            
            <IconButton
              color="inherit"
              onClick={(e) => setProfileAnchor(e.currentTarget)}
            >
              <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem', bgcolor: 'secondary.main' }}>
                MS
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Fixed Statistics Bar */}
      <Paper 
        elevation={1} 
        sx={{ 
          position: 'fixed',
          top: '60px',
          left: 0,
          right: 0,
          zIndex: 95,
          px: 3,
          py: 1.5, 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: 'background.paper',
          borderBottom: '1px solid #e0e0e0',
          borderRadius: 0,
        }}
      >
        {/* Left side - Key metrics */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: { xs: 1, sm: 2 },
          flexWrap: { xs: 'wrap', sm: 'nowrap' },
          '& .MuiChip-root': {
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-1px)',
              boxShadow: 2,
            }
          },
          '& .MuiChip-root:not(:last-child)': {
            position: 'relative',
            '&::after': {
              content: '""',
              position: 'absolute',
              right: '-1px',
              top: '50%',
              transform: 'translateY(-50%)',
              width: '1px',
              height: '20px',
              backgroundColor: '#e0e0e0',
              display: { xs: 'none', sm: 'block' }
            }
          }
        }}>
          <Chip 
            label={`📧 ${stats.total || 0} Total`} 
            variant="outlined" 
            color="primary"
            size="small"
            sx={{ fontWeight: 600 }}
          />
          <Chip 
            label={`⭐ ${stats.starred || 0} Destacados`} 
            variant="outlined" 
            color="warning"
            size="small"
            sx={{ 
              fontWeight: 600, 
              display: { xs: 'none', sm: 'inline-flex' },
              ml: { sm: 1 }
            }}
          />
          <Chip 
            label={`📬 ${stats.unread || 0} Sin leer`} 
            variant="outlined" 
            color="error"
            size="small"
            sx={{ 
              fontWeight: 600,
              ml: { sm: 1 }
            }}
          />
        </Box>

        {/* Right side - Priority progress bar */}
        <Box sx={{ display: { xs: 'none', lg: 'flex' } }}>
          <PriorityProgressBar stats={stats} />
        </Box>

        {/* Mobile priority summary */}
        <Box sx={{ display: { xs: 'flex', lg: 'none' }, alignItems: 'center', gap: 1 }}>
          {stats.byUrgency?.urgent > 0 && (
            <Chip 
              label={`${stats.byUrgency.urgent} 🔴`}
              size="small"
              sx={{ 
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                color: '#dc3545',
                fontSize: '0.7rem'
              }}
            />
          )}
          {stats.byUrgency?.high > 0 && (
            <Chip 
              label={`${stats.byUrgency.high} 🟠`}
              size="small"
              sx={{ 
                backgroundColor: 'rgba(253, 126, 20, 0.1)',
                color: '#fd7e14',
                fontSize: '0.7rem',
                display: { xs: 'none', sm: 'inline-flex' }
              }}
            />
          )}
          {stats.byUrgency?.medium > 0 && (
            <Chip 
              label={`${stats.byUrgency.medium} 🟢`}
              size="small"
              sx={{ 
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                color: '#198754',
                fontSize: '0.7rem',
                display: { xs: 'none', md: 'inline-flex' }
              }}
            />
          )}
        </Box>
      </Paper>

      {/* Main Content Container */}
      <Box sx={{ mt: 'calc(60px + 60px)', height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>

        {/* Kanban Board */}
        <Box
          sx={{
            display: 'flex',
            overflowX: 'auto',
            overflowY: 'hidden',
            flex: 1,
            px: 1.5,
            pb: 1.5,
            gap: 1,
            '&::-webkit-scrollbar': {
              height: '6px',
            },
            '&::-webkit-scrollbar-track': {
              backgroundColor: 'rgba(0,0,0,0.1)',
              borderRadius: '3px',
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: 'rgba(0,0,0,0.3)',
              borderRadius: '3px',
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.4)',
              },
            },
          }}
        >
          {columns.map(column => {
            const columnEmails = getEmailsByUrgency(filteredEmails, column.urgency);
            return (
              <EmailColumn
                key={column.id}
                column={column}
                emails={columnEmails}
                onMarkAsRead={handleMarkAsRead}
                onArchive={handleArchive}
                onToggleStar={handleToggleStar}
              />
            );
          })}
        </Box>
      </Box>

      {/* Menús desplegables */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={() => setNotificationAnchor(null)}
      >
        <MenuList sx={{ minWidth: 250 }}>
          <MenuItemComponent>
            <Typography variant="body2">
              📧 {stats.unread || 0} correos sin leer
            </Typography>
          </MenuItemComponent>
          <MenuItemComponent>
            <Typography variant="body2">
              🔴 {stats.byUrgency?.urgent || 0} correos urgentes
            </Typography>
          </MenuItemComponent>
          <MenuItemComponent>
            <Typography variant="body2">
              ⭐ {stats.starred || 0} correos destacados
            </Typography>
          </MenuItemComponent>
        </MenuList>
      </Menu>

      <Menu
        anchorEl={profileAnchor}
        open={Boolean(profileAnchor)}
        onClose={() => setProfileAnchor(null)}
      >
        <MenuList>
          <MenuItemComponent onClick={() => setProfileAnchor(null)}>
            👤 Perfil
          </MenuItemComponent>
          <MenuItemComponent onClick={() => setProfileAnchor(null)}>
            ⚙️ Configuración
          </MenuItemComponent>
          <MenuItemComponent onClick={() => setProfileAnchor(null)}>
            🚪 Cerrar sesión
          </MenuItemComponent>
        </MenuList>
      </Menu>
      
      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Box>
  );
};

export default Dashboard;