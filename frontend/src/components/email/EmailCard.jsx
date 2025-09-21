import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  MarkEmailRead,
  Archive,
  Star,
  StarBorder,
  Circle,
  Reply,
} from '@mui/icons-material';

const EmailCard = ({ 
  email, 
  onMarkAsRead, 
  onArchive, 
  onToggleStar,
  onReply,
  isDragging = false,
  draggable = false,
  onDragStart,
  onDragEnd 
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const getSenderName = (email) => {
    // For sent emails, show recipient instead of sender
    if (email.emailType === 'sent') {
      if (email.sender) {
        if (typeof email.sender === 'string') {
          return email.sender;
        }
        if (typeof email.sender === 'object') {
          return email.sender.name || email.sender.email || 'Unknown Recipient';
        }
      }
      return 'Unknown Recipient';
    }

    // Handle different possible data structures for sender (received emails)
    if (email.sender_name && typeof email.sender_name === 'string') {
      return email.sender_name;
    }
    if (email.sender) {
      if (typeof email.sender === 'string') {
        return email.sender;
      }
      if (typeof email.sender === 'object') {
        return email.sender.name || email.sender.email || 'Unknown';
      }
    }
    return 'Unknown Sender';
  };

  const getInitials = (name) => {
    if (!name || typeof name !== 'string') {
      return '??';
    }
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getTimeAgo = (timestamp) => {
    if (!timestamp) return 'Fecha desconocida';
    
    try {
      const now = new Date();
      const emailDate = new Date(timestamp);
      
      // Verificar que la fecha es válida
      if (isNaN(emailDate.getTime())) {
        console.warn('Invalid timestamp:', timestamp);
        return 'Fecha inválida';
      }
      
      const diffInMs = now - emailDate;
      const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
      const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
      const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
      
      if (diffInMinutes < 1) return 'Ahora mismo';
      if (diffInMinutes < 60) return `Hace ${diffInMinutes}min`;
      if (diffInHours < 1) return 'Hace menos de 1h';
      if (diffInHours < 24) return `Hace ${diffInHours}h`;
      if (diffInDays === 1) return 'Ayer';
      if (diffInDays < 7) return `Hace ${diffInDays} días`;
      if (diffInDays < 30) {
        const weeks = Math.floor(diffInDays / 7);
        return weeks === 1 ? 'Hace 1 semana' : `Hace ${weeks} semanas`;
      }
      if (diffInDays < 365) {
        const months = Math.floor(diffInDays / 30);
        return months === 1 ? 'Hace 1 mes' : `Hace ${months} meses`;
      }
      const years = Math.floor(diffInDays / 365);
      return years === 1 ? 'Hace 1 año' : `Hace ${years} años`;
      
    } catch (error) {
      console.error('Error calculating time ago:', error, 'for timestamp:', timestamp);
      return 'Error de fecha';
    }
  };

  const getPriorityColor = (urgency) => {
    switch (urgency) {
      case 'urgent': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#198754';
      case 'low': return '#0078d4';
      default: return '#6c757d';
    }
  };

  const getPriorityLabel = (urgency) => {
    switch (urgency) {
      case 'urgent': return 'Urgente';
      case 'high': return 'Alta';
      case 'medium': return 'Media';
      case 'low': return 'Baja';
      default: return 'Procesado';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence === undefined || confidence === null) {
      return '#6c757d'; // Gray for undefined
    }
    if (confidence >= 0.8) return '#198754'; // Green for high confidence
    if (confidence >= 0.6) return '#fd7e14'; // Orange for medium confidence
    return '#dc3545'; // Red for low confidence
  };

  const handleCardClick = (e) => {
    // Evitar que se active si se hizo click en un botón o elemento interactivo
    if (e.target.closest('button') || e.target.closest('[role="button"]')) {
      return;
    }

    // Only open reply modal for received emails, not sent or replied emails
    if (email.emailType !== 'sent' && email.emailType !== 'reply') {
      onReply?.(email);
    }
  };

  return (
    <Card
      sx={{
        mb: 1,
        cursor: draggable ? 'grab' : 'pointer',
        opacity: isDragging ? 0.8 : 1,
        transform: isDragging 
          ? 'rotate(2deg) scale(1.02)' 
          : isHovered 
            ? 'translateY(-1px)' 
            : 'translateY(0)',
        transition: 'all 0.2s ease-in-out',
        border: email.isRead ? 'none' : '1px solid',
        borderColor: email.isRead ? 'transparent' : 'primary.main',
        borderLeftWidth: '3px',
        borderLeftColor: getPriorityColor(email.urgency),
        minHeight: 120,
        boxShadow: isDragging 
          ? '0 8px 25px rgba(0,0,0,0.25), 0 0 0 2px rgba(25, 118, 210, 0.3)' 
          : 'none',
        backgroundColor: isDragging 
          ? 'rgba(255, 255, 255, 0.95)' 
          : 'background.paper',
        backdropFilter: isDragging ? 'blur(2px)' : 'none',
        '&:hover': {
          boxShadow: isDragging ? '0 8px 25px rgba(0,0,0,0.25), 0 0 0 2px rgba(25, 118, 210, 0.3)' : 2,
          backgroundColor: isDragging ? 'rgba(255, 255, 255, 0.95)' : 'action.hover',
        },
        '&:active': {
          transform: isDragging ? 'rotate(2deg) scale(1.02)' : 'translateY(0px)',
        }
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
      draggable={draggable}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        {/* Header con avatar y acciones */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 0.75 }}>
          <Badge
            variant="dot"
            color="primary"
            invisible={email.isRead}
            sx={{
              '& .MuiBadge-dot': {
                backgroundColor: getPriorityColor(email.urgency),
              }
            }}
          >
            <Avatar
              sx={{ 
                width: 28, 
                height: 28, 
                fontSize: '0.75rem',
                bgcolor: getPriorityColor(email.urgency),
              }}
            >
              {getInitials(getSenderName(email))}
            </Avatar>
          </Badge>
          
          <Box sx={{ ml: 1, flexGrow: 1, minWidth: 0 }}>
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: email.isRead ? 400 : 600,
                color: 'text.primary',
                fontSize: '0.8rem',
                lineHeight: 1.2,
              }}
            >
              {getSenderName(email)}
            </Typography>
            <Typography 
              variant="caption" 
              color="text.secondary"
              sx={{ fontSize: '0.7rem' }}
            >
              {getTimeAgo(email.received_at || email.receivedAt || email.timestamp || email.date || email.receivedDateTime)}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onToggleStar?.(email.id);
              }}
              sx={{ opacity: isHovered ? 1 : 0, transition: 'opacity 0.2s' }}
            >
              {email.isStarred ? <Star color="warning" /> : <StarBorder />}
            </IconButton>
          </Box>
        </Box>

        {/* Asunto */}
        <Typography 
          variant="body2" 
          sx={{ 
            fontWeight: email.isRead ? 400 : 600,
            mb: 0.75,
            display: '-webkit-box',
            WebkitLineClamp: 1,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            fontSize: '0.85rem',
            lineHeight: 1.3,
          }}
        >
          {email.subject}
        </Typography>

        {/* Preview del contenido */}
        <Typography 
          variant="body2" 
          color="text.secondary"
          sx={{ 
            mb: 1.25,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            fontSize: '0.75rem',
            lineHeight: 1.3,
          }}
        >
          {email.preview}
        </Typography>

        {/* Footer con badges y acciones */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', gap: 0.75, flexWrap: 'wrap' }}>
            {email.emailType === 'reply' && (
              <Chip
                label="Respondido"
                size="small"
                sx={{
                  backgroundColor: '#17a2b8',
                  color: 'white',
                  fontSize: '0.625rem',
                  height: 18,
                  '& .MuiChip-label': {
                    px: 0.75,
                  },
                }}
              />
            )}
            {email.emailType === 'sent' && (
              <Chip
                label="Enviado"
                size="small"
                sx={{
                  backgroundColor: '#28a745',
                  color: 'white',
                  fontSize: '0.625rem',
                  height: 18,
                  '& .MuiChip-label': {
                    px: 0.75,
                  },
                }}
              />
            )}
            {email.emailType !== 'sent' && email.emailType !== 'reply' && (
              <Chip
                label={getPriorityLabel(email.urgency)}
                size="small"
                sx={{
                  backgroundColor: getPriorityColor(email.urgency),
                  color: 'white',
                  fontSize: '0.625rem',
                  height: 18,
                  '& .MuiChip-label': {
                    px: 0.75,
                  },
                }}
              />
            )}
            {/* Only show AI confidence for received emails, not sent or replied emails */}
            {email.emailType !== 'sent' && email.emailType !== 'reply' && (
              <Chip
                label={`IA ${email.ai_confidence !== undefined ? Math.round(email.ai_confidence * 100) : 0}%`}
                size="small"
                variant="outlined"
                sx={{
                  borderColor: getConfidenceColor(email.ai_confidence),
                  color: getConfidenceColor(email.ai_confidence),
                  fontSize: '0.625rem',
                  height: 18,
                  '& .MuiChip-label': {
                    px: 0.75,
                  },
                }}
              />
            )}
          </Box>

          <Box
            sx={{
              display: 'flex',
              gap: 0.5,
              opacity: isHovered ? 1 : 0,
              transition: 'opacity 0.2s',
            }}
          >
            {/* Only show reply button for received emails, not sent or replied emails */}
            {email.emailType !== 'sent' && email.emailType !== 'reply' && (
              <Tooltip title="Responder">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onReply?.(email);
                  }}
                  sx={{ color: 'primary.main' }}
                >
                  <Reply fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {!email.isRead && email.emailType !== 'sent' && email.emailType !== 'reply' && (
              <Tooltip title="Marcar como leído">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onMarkAsRead?.(email.id);
                  }}
                >
                  <MarkEmailRead fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {email.emailType !== 'sent' && email.emailType !== 'reply' && (
              <Tooltip title="Archivar">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onArchive?.(email.id);
                  }}
                >
                  <Archive fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default EmailCard;