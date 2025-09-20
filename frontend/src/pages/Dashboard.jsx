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
import ReplyModal from '../components/email/ReplyModal';
import ThemeToggle from '../components/common/ThemeToggle';
import PriorityProgressBar from '../components/common/PriorityProgressBar';
import { generateMockEmails, getEmailsByUrgency, getEmailStats } from '../utils/mockData';
import { emailAPI } from '../services/api';

function getInitials(name, email) {
  if (name) {
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  if (email) {
    const user = email.split('@')[0];
    return user.slice(0, 2).toUpperCase();
  }
  return '';
}

const Dashboard = () => {
  const [emails, setEmails] = useState([]);
  const [sentEmails, setSentEmails] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterBy, setFilterBy] = useState('all');
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [profileAnchor, setProfileAnchor] = useState(null);
  const [stats, setStats] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [replyModalOpen, setReplyModalOpen] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [isSendingReply, setIsSendingReply] = useState(false);
  const [profilePhotoUrl, setProfilePhotoUrl] = useState(null);
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');

  const columns = [
    { id: 'urgent', urgency: 'urgent', title: 'Urgente', subtitle: 'Próxima hora' },
    { id: 'high', urgency: 'high', title: 'Alta Prioridad', subtitle: 'Próximas 3 horas' },
    { id: 'medium', urgency: 'medium', title: 'Prioridad Media', subtitle: 'Hoy' },
    { id: 'low', urgency: 'low', title: 'Baja Prioridad', subtitle: 'Mañana' },
    { id: 'processed', urgency: 'processed', title: 'Procesados', subtitle: 'Completados' },
  ];

  useEffect(() => {
    loadEmails();
    
    // Set up polling for full synchronization every 2 minutes
    const syncInterval = setInterval(async () => {
      try {
        console.log('Auto-syncing emails and statuses...');
        await loadEmails();
        console.log('Auto-sync completed');
      } catch (error) {
        console.error('Auto-sync failed:', error);
      }
    }, 2 * 60 * 1000); // Every 2 minutes

    return () => clearInterval(syncInterval);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    fetch('http://localhost:5000/api/microsoft/profile', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setUserName(data.name);
          setUserEmail(data.email);

          // Si hay foto, la pedimos
          if (data.has_photo) {
            fetch('http://localhost:5000/api/microsoft/profile/photo', {
              headers: { Authorization: `Bearer ${token}` },
            })
              .then(response => {
                if (response.ok) return response.blob();
                throw new Error('No photo');
              })
              .then(blob => {
                const objectUrl = URL.createObjectURL(blob);
                setProfilePhotoUrl(objectUrl);
              })
              .catch(() => setProfilePhotoUrl(null));
          } else {
            setProfilePhotoUrl(null);
          }
        }
      });
  }, []);

  useEffect(() => {
    setStats(getEmailStats(emails));
  }, [emails]);

  const loadEmails = async () => {
    setIsLoading(true);
    try {
      // Check if we have a token first
      const token = localStorage.getItem('token');
      if (!token) {
        console.warn('No token found, using mock data');
        setEmails(generateMockEmails());
        setIsLoading(false);
        return;
      }

      // First, sync emails from Microsoft Graph
      console.log('Syncing emails from Microsoft Graph...');
      const syncResponse = await emailAPI.syncEmails({ count: 50, classify: true });
      console.log('Email sync completed:', syncResponse.data);

      // Also sync email read/unread statuses
      console.log('Syncing email statuses...');
      const statusResponse = await emailAPI.syncEmailStatuses({ limit: 100 });
      console.log('Status sync completed:', statusResponse.data);

      // Load received emails
      console.log('Fetching emails...');
      const response = await emailAPI.getEmails();

      // Load sent emails for processed column
      console.log('Fetching sent emails...');
      const sentResponse = await emailAPI.getSentEmails({ per_page: 50 });

      if (response.data && response.data.emails) {
        const apiEmails = response.data.emails.map(email => ({
          id: email.id,
          subject: email.subject,
          sender: email.sender,
          preview: email.body_preview,
          urgency: email.urgency_category,
          priority: email.priority_level,
          isRead: email.is_read,
          receivedAt: email.received_at,
          hasAttachments: email.has_attachments,
          ai_confidence: email.ai_confidence || 0,
          aiReason: email.ai_classification_reason || '',
          emailType: 'received'
        }));
        setEmails(apiEmails);
        console.log(`Successfully loaded ${apiEmails.length} real emails`);
      } else {
        console.warn('No emails returned from API, using mock data');
        setEmails(generateMockEmails());
      }

      // Process sent emails for the "Procesados" column
      if (sentResponse.data && sentResponse.data.emails) {
        const apiSentEmails = sentResponse.data.emails.map(email => ({
          id: `sent_${email.id}`,
          subject: email.subject,
          sender: email.recipient, // For sent emails, show recipient as "sender"
          preview: email.preview,
          urgency: 'processed',
          priority: 5,
          isRead: true, // Sent emails are always "read"
          receivedAt: email.sent_at,
          hasAttachments: email.has_attachments,
          ai_confidence: 1.0,
          aiReason: email.email_type === 'reply' ? 'Respuesta enviada' : 'Correo enviado',
          emailType: email.email_type, // 'sent' or 'reply'
          isReply: email.is_reply || false
        }));
        setSentEmails(apiSentEmails);
        console.log(`Successfully loaded ${apiSentEmails.length} sent emails`);
      } else {
        console.warn('No sent emails returned from API');
        setSentEmails([]);
      }
    } catch (error) {
      console.error('Failed to load emails:', error);
      if (error.response?.status === 401) {
        console.warn('Authentication error - redirecting to login');
        localStorage.removeItem('token');
        window.location.href = '/';
        return;
      }
      console.log('Using mock data as fallback');
      setEmails(generateMockEmails());
      setSentEmails([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsRead = async (emailId) => {
    try {
      // Optimistic update - update UI immediately
      setEmails(prevEmails =>
        prevEmails.map(email =>
          email.id === emailId ? { ...email, isRead: true } : email
        )
      );

      // Call backend to mark as read in both database and Microsoft
      const response = await emailAPI.markEmailAsRead(emailId);
      
      if (!response.data.success) {
        // Revert optimistic update on failure
        setEmails(prevEmails =>
          prevEmails.map(email =>
            email.id === emailId ? { ...email, isRead: false } : email
          )
        );
        console.error('Failed to mark email as read:', response.data.error);
      } else {
        console.log('Email marked as read:', {
          microsoft_updated: response.data.microsoft_updated,
          local_updated: response.data.local_updated
        });
      }
    } catch (error) {
      // Revert optimistic update on error
      setEmails(prevEmails =>
        prevEmails.map(email =>
          email.id === emailId ? { ...email, isRead: false } : email
        )
      );
      console.error('Error marking email as read:', error);
    }
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

  const handleReply = (email) => {
    setSelectedEmail(email);
    setReplyModalOpen(true);
  };

  const handleSendReply = async (emailId, replyBody) => {
    setIsSendingReply(true);
    try {
      const response = await emailAPI.replyToEmail(emailId, { body: replyBody });

      if (response.data.success) {
        // Remover el email original de la lista (no moverlo a procesados)
        // Solo la respuesta enviada aparecerá en procesados cuando se actualice
        setEmails(prevEmails =>
          prevEmails.filter(email => email.id !== emailId)
        );

        // Actualizar estadísticas - solo decrementar del original, procesados se actualizará al cargar sent emails
        setStats(prevStats => ({
          ...prevStats,
          unread: Math.max(0, (prevStats.unread || 0) - 1),
          byUrgency: {
            ...prevStats.byUrgency,
            [selectedEmail?.urgency]: Math.max(0, (prevStats.byUrgency?.[selectedEmail?.urgency] || 0) - 1)
          }
        }));
      }
    } catch (error) {
      console.error('Error sending reply:', error);
      throw new Error(error.response?.data?.error || 'Error al enviar la respuesta');
    } finally {
      setIsSendingReply(false);
    }
  };


  const handleCloseReplyModal = () => {
    setReplyModalOpen(false);
    setSelectedEmail(null);
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
            <IconButton 
              color="inherit" 
              onClick={loadEmails} 
              disabled={isLoading}
              title="Sincronizar correos y estados de lectura"
            >
              <Refresh sx={{ 
                animation: isLoading ? 'spin 1s linear infinite' : 'none',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' }
                }
              }} />
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
              <Avatar src={profilePhotoUrl || undefined}
                sx={{ width: 32, height: 32, fontSize: '0.875rem', bgcolor: 'secondary.main' }}
              >       
                  {!profilePhotoUrl && getInitials(userName, userEmail)}
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
            let columnEmails;
            if (column.urgency === 'processed') {
              // For processed column, show both processed emails and sent emails
              const processedEmails = getEmailsByUrgency(filteredEmails, 'processed');
              columnEmails = [...processedEmails, ...sentEmails];
            } else {
              columnEmails = getEmailsByUrgency(filteredEmails, column.urgency);
            }

            return (
              <EmailColumn
                key={column.id}
                column={column}
                emails={columnEmails}
                onMarkAsRead={handleMarkAsRead}
                onArchive={handleArchive}
                onToggleStar={handleToggleStar}
                onReply={handleReply}
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

      {/* Modal de respuesta */}
      <ReplyModal
        open={replyModalOpen}
        onClose={handleCloseReplyModal}
        email={selectedEmail}
        onSendReply={handleSendReply}
        isSending={isSendingReply}
      />
      
    </Box>
  );
};

export default Dashboard;