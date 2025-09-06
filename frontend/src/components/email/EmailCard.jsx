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
} from '@mui/icons-material';

const EmailCard = ({ 
  email, 
  onMarkAsRead, 
  onArchive, 
  onToggleStar,
  isDragging = false 
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const emailDate = new Date(timestamp);
    const diffInHours = Math.floor((now - emailDate) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Hace menos de 1h';
    if (diffInHours < 24) return `Hace ${diffInHours}h`;
    if (diffInHours < 48) return 'Ayer';
    const days = Math.floor(diffInHours / 24);
    return `Hace ${days} días`;
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
    return '#0078d4'; // Always blue for consistency
  };

  return (
    <Card
      sx={{
        mb: 1,
        cursor: 'pointer',
        opacity: isDragging ? 0.5 : 1,
        transform: isHovered ? 'translateY(-1px)' : 'translateY(0)',
        transition: 'all 0.15s ease-in-out',
        border: email.isRead ? 'none' : '1px solid',
        borderColor: email.isRead ? 'transparent' : 'primary.main',
        borderLeftWidth: '3px',
        borderLeftColor: getPriorityColor(email.urgency),
        minHeight: 120,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
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
              {getInitials(email.sender)}
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
              {email.sender}
            </Typography>
            <Typography 
              variant="caption" 
              color="text.secondary"
              sx={{ fontSize: '0.7rem' }}
            >
              {getTimeAgo(email.timestamp)}
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
            <Chip
              label={`IA ${email.aiConfidence}%`}
              size="small"
              variant="outlined"
              sx={{
                borderColor: getConfidenceColor(email.aiConfidence),
                color: getConfidenceColor(email.aiConfidence),
                fontSize: '0.625rem',
                height: 18,
                '& .MuiChip-label': {
                  px: 0.75,
                },
              }}
            />
          </Box>

          <Box 
            sx={{ 
              display: 'flex', 
              gap: 0.5,
              opacity: isHovered ? 1 : 0,
              transition: 'opacity 0.2s',
            }}
          >
            {!email.isRead && (
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
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default EmailCard;