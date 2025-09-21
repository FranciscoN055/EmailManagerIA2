import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Badge,
  Divider,
} from '@mui/material';
import EmailCard from './EmailCard';

const EmailColumn = ({ 
  column, 
  emails, 
  onMarkAsRead, 
  onArchive, 
  onToggleStar,
  onReply,
  onEmailDrop
}) => {
  const getColumnColor = (urgency) => {
    switch (urgency) {
      case 'urgent': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#198754';
      case 'low': return '#0078d4';
      case 'processed': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const getColumnIcon = (urgency) => {
    switch (urgency) {
      case 'urgent': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟢';
      case 'low': return '🔵';
      case 'processed': return '⚪';
      default: return '📧';
    }
  };

  const getColumnTitle = (urgency) => {
    switch (urgency) {
      case 'urgent': return 'Urgente';
      case 'high': return 'Alta Prioridad';
      case 'medium': return 'Prioridad Media';
      case 'low': return 'Baja Prioridad';
      case 'processed': return 'Procesados';
      default: return 'Otros';
    }
  };

  const getColumnSubtitle = (urgency) => {
    switch (urgency) {
      case 'urgent': return 'Próxima hora';
      case 'high': return 'Próximas 3 horas';
      case 'medium': return 'Hoy';
      case 'low': return 'Mañana';
      case 'processed': return 'Completados';
      default: return '';
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const emailId = e.dataTransfer.getData('emailId'); 
    onEmailDrop(emailId, column.id);
  };

  return (
    <Paper
      elevation={2}
      sx={{
        width: 280,
        minWidth: 280,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.paper',
        borderRadius: 2,
        overflow: 'hidden',
        flexShrink: 0,
      }}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* Header de la columna */}
      <Box
        sx={{
          p: 1.5,
          backgroundColor: getColumnColor(column.urgency),
          color: 'white',
          position: 'sticky',
          top: 0,
          zIndex: 1,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5, pr: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flex: 1 }}>
            <Typography variant="body1" sx={{ fontSize: '1rem' }}>
              {getColumnIcon(column.urgency)}
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
              {getColumnTitle(column.urgency)}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minWidth: 32 }}>
            <Badge
              badgeContent={emails.length}
              color="secondary"
              sx={{
                '& .MuiBadge-badge': {
                  backgroundColor: 'rgba(255,255,255,0.9)',
                  color: getColumnColor(column.urgency),
                  fontWeight: 600,
                  fontSize: '0.65rem',
                  minWidth: 18,
                  height: 18,
                  position: 'relative',
                  transform: 'none',
                  right: 'auto',
                  top: 'auto',
                }
              }}
            />
          </Box>
        </Box>
        <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.7rem' }}>
          {getColumnSubtitle(column.urgency)}
        </Typography>
      </Box>

      <Divider />

      {/* Lista de emails */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 1,
          '&::-webkit-scrollbar': {
            width: '4px',
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'rgba(0,0,0,0.2)',
            borderRadius: '2px',
            '&:hover': {
              backgroundColor: 'rgba(0,0,0,0.3)',
            },
          },
        }}
      >
        {emails.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 3,
              textAlign: 'center',
            }}
          >
            <Typography variant="body1" color="text.secondary" gutterBottom sx={{ fontSize: '1.5rem' }}>
              📭
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
              No hay correos en esta categoría
            </Typography>
          </Box>
        ) : (
          emails.map((email) => (
            <EmailCard
              key={email.id}
              email={email}
              onMarkAsRead={onMarkAsRead}
              onArchive={onArchive}
              onToggleStar={onToggleStar}
              onReply={onReply}
              draggable={true}
              onDragStart={e => {
                e.dataTransfer.setData('emailId', email.id);
              }}
              onDragEnd={e => {
                e.dataTransfer.clearData();
              }}
            />
          ))
        )}
      </Box>

      {/* Footer con estadísticas */}
      {emails.length > 0 && (
        <>
          <Divider />
          <Box sx={{ p: 1, backgroundColor: 'background.default' }}>
            <Typography variant="caption" color="text.secondary" align="center" sx={{ fontSize: '0.7rem' }}>
              {emails.filter(email => !email.isRead).length} sin leer de {emails.length}
            </Typography>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default EmailColumn;