import React, { useState, useEffect } from 'react';
import { Box, Tooltip, Typography } from '@mui/material';

const PriorityProgressBar = ({ stats }) => {
  const [hoveredSegment, setHoveredSegment] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const total = stats.total || 0;
  const processed = stats.byUrgency?.processed || 0;
  const processedPercentage = total > 0 ? Math.round((processed / total) * 100) : 0;

  // Update timestamp when stats change
  useEffect(() => {
    setLastUpdate(new Date());
  }, [stats]);

  const getTimeAgo = () => {
    const now = new Date();
    const diffInMinutes = Math.floor((now - lastUpdate) / (1000 * 60));
    if (diffInMinutes < 1) return 'hace menos de 1 min';
    if (diffInMinutes === 1) return 'hace 1 min';
    return `hace ${diffInMinutes} min`;
  };

  // New order: processed first, then pending by priority
  const segments = [
    { 
      key: 'processed', 
      count: stats.byUrgency?.processed || 0, 
      color: '#6c757d', 
      label: 'Correos procesados',
      tooltip: `${stats.byUrgency?.processed || 0} correos procesados (${processedPercentage}% del total)`
    },
    { 
      key: 'urgent', 
      count: stats.byUrgency?.urgent || 0, 
      color: '#dc3545', 
      label: 'Urgentes pendientes',
      tooltip: `${stats.byUrgency?.urgent || 0} correos urgentes pendientes (${total > 0 ? Math.round(((stats.byUrgency?.urgent || 0) / total) * 100) : 0}% del total)`
    },
    { 
      key: 'high', 
      count: stats.byUrgency?.high || 0, 
      color: '#fd7e14', 
      label: 'Alta prioridad pendientes',
      tooltip: `${stats.byUrgency?.high || 0} correos alta prioridad pendientes (${total > 0 ? Math.round(((stats.byUrgency?.high || 0) / total) * 100) : 0}% del total)`
    },
    { 
      key: 'medium', 
      count: stats.byUrgency?.medium || 0, 
      color: '#198754', 
      label: 'Media prioridad pendientes',
      tooltip: `${stats.byUrgency?.medium || 0} correos media prioridad pendientes (${total > 0 ? Math.round(((stats.byUrgency?.medium || 0) / total) * 100) : 0}% del total)`
    },
    { 
      key: 'low', 
      count: stats.byUrgency?.low || 0, 
      color: '#0078d4', 
      label: 'Baja prioridad pendientes',
      tooltip: `${stats.byUrgency?.low || 0} correos baja prioridad pendientes (${total > 0 ? Math.round(((stats.byUrgency?.low || 0) / total) * 100) : 0}% del total)`
    },
  ];

  const activeSegments = segments.filter(segment => segment.count > 0);

  return (
    <Box sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      gap: { sm: 1.5, md: 2 },
      flexDirection: { xs: 'column', lg: 'row' }
    }}>
      <Typography 
        variant="body2" 
        color="text.primary" 
        sx={{ 
          fontSize: '0.875rem',
          fontWeight: 600,
          mr: 1
        }}
      >
        Progreso de respuestas:
      </Typography>
      
      <Box
        sx={{  
          width: { sm: 250, md: 300 },
          height: 24,
          borderRadius: '12px',
          backgroundColor: '#f5f5f5',
          display: 'flex',
          overflow: 'hidden',
          border: '1px solid rgba(0,0,0,0.1)',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        {activeSegments.map((segment, index) => {
          const percentage = total > 0 ? (segment.count / total) * 100 : 0;
          const isHovered = hoveredSegment === segment.key;
          
          return (
            <Tooltip
              key={segment.key}
              title={
                <Typography variant="caption" sx={{ fontWeight: 500 }}>
                  {segment.tooltip}
                </Typography>
              }
              placement="top"
              arrow
            >
              <Box
                sx={{
                  height: '100%',
                  backgroundColor: segment.color,
                  width: `${percentage}%`,
                  transition: 'all 0.5s ease-in-out',
                  cursor: 'pointer',
                  opacity: hoveredSegment && !isHovered ? 0.6 : 1,
                  transform: isHovered ? 'scaleY(1.1)' : 'scaleY(1)',
                  transformOrigin: 'bottom',
                  minWidth: percentage > 0 ? '2px' : '0px',
                  borderRight: index < activeSegments.length - 1 ? '1px solid rgba(255,255,255,0.3)' : 'none',
                }}
                onMouseEnter={() => setHoveredSegment(segment.key)}
                onMouseLeave={() => setHoveredSegment(null)}
              />
            </Tooltip>
          );
        })}
        
        {/* Segmento vacío si no hay correos */}
        {activeSegments.length === 0 && (
          <Box
            sx={{
              height: '100%',
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#999',
              fontSize: '0.7rem',
            }}
          >
            No hay correos
          </Box>
        )}
      </Box>

      {/* Progress text and timestamp */}
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', ml: 1 }}>
        <Typography 
          variant="caption" 
          sx={{ 
            fontSize: '0.75rem', 
            fontWeight: 600,
            color: 'text.primary'
          }}
        >
          {processedPercentage}% procesado - {processed} de {total} respondidos
        </Typography>
        <Typography 
          variant="caption" 
          sx={{ 
            fontSize: '0.65rem', 
            color: 'text.secondary',
            mt: 0.25
          }}
        >
          Actualizado {getTimeAgo()}
        </Typography>
      </Box>
    </Box>
  );
};

export default PriorityProgressBar;