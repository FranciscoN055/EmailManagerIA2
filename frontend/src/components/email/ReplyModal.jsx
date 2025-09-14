import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  IconButton,
  Paper,
  Chip,
  Avatar,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Close, Send, Reply } from '@mui/icons-material';

const ReplyModalNew = ({ 
  open, 
  onClose, 
  email, 
  onSendReply,
  isSending = false 
}) => {
  const [replyBody, setReplyBody] = useState('');
  const [error, setError] = useState('');

  const handleSend = async () => {
    if (!replyBody.trim()) {
      setError('El mensaje de respuesta no puede estar vacío');
      return;
    }

    try {
      setError('');
      await onSendReply(email.id, replyBody.trim());
      setReplyBody('');
      onClose();
    } catch (err) {
      setError(err.message || 'Error al enviar la respuesta');
    }
  };

  const handleClose = () => {
    setReplyBody('');
    setError('');
    onClose();
  };

  const getSenderName = (email) => {
    if (email?.sender_name && typeof email.sender_name === 'string') {
      return email.sender_name;
    }
    if (email?.sender) {
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

  if (!email) return null;

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          minHeight: '70vh',
          maxHeight: '90vh',
        }
      }}
    >
      <DialogTitle sx={{ 
        pb: 1, 
        borderBottom: '1px solid #e0e0e0',
        backgroundColor: 'background.paper'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Reply color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Responder correo
            </Typography>
          </Box>
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', flex: 1 }}>
        {/* Email original */}
        <Paper 
          elevation={1} 
          sx={{ 
            m: 2, 
            p: 2, 
            backgroundColor: 'background.default',
            borderLeft: `4px solid ${getPriorityColor(email.urgency)}`
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
            <Avatar
              sx={{ 
                width: 32, 
                height: 32, 
                fontSize: '0.75rem',
                bgcolor: getPriorityColor(email.urgency),
                mr: 1.5
              }}
            >
              {getInitials(getSenderName(email))}
            </Avatar>
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {getSenderName(email)}
                </Typography>
                <Chip
                  label={getPriorityLabel(email.urgency)}
                  size="small"
                  sx={{
                    backgroundColor: getPriorityColor(email.urgency),
                    color: 'white',
                    fontSize: '0.625rem',
                    height: 18,
                  }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                <strong>Asunto:</strong> {email.subject}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, fontSize: '0.8rem' }}>
                <strong>Contenido del mensaje original:</strong>
              </Typography>
              <Box sx={{ 
                maxHeight: '200px', 
                overflow: 'auto',
                border: '1px solid #e0e0e0',
                borderRadius: 1,
                p: 1.5,
                backgroundColor: 'background.paper',
                fontSize: '0.875rem',
                lineHeight: 1.4,
                '& pre': {
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                  fontFamily: 'inherit',
                },
                '& p': {
                  margin: '0 0 12px 0',
                  lineHeight: '1.6',
                  '&:last-child': {
                    marginBottom: 0,
                  }
                },
                '& br': {
                  lineHeight: '1.6',
                }
              }}>
                {email.body_content ? (
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: email.body_content
                        .replace(/\n\n/g, '</p><p>')  // Dobles saltos de línea = párrafos
                        .replace(/\n/g, '<br/>')      // Saltos simples = <br/>
                        .replace(/^/, '<p>')          // Inicio con <p>
                        .replace(/$/, '</p>')         // Final con </p>
                        .replace(/<p><\/p>/g, '')     // Limpiar párrafos vacíos
                    }} 
                  />
                ) : email.body_preview ? (
                  <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                    {email.body_preview}
                  </div>
                ) : email.preview ? (
                  <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                    {email.preview}
                  </div>
                ) : (
                  <div style={{ color: '#666', fontStyle: 'italic' }}>
                    Sin contenido previo disponible
                  </div>
                )}
              </Box>
            </Box>
          </Box>
        </Paper>

        {/* Formulario de respuesta */}
        <Box sx={{ p: 2, flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
            Tu respuesta:
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            multiline
            rows={12}
            fullWidth
            value={replyBody}
            onChange={(e) => setReplyBody(e.target.value)}
            placeholder="Escribe tu respuesta aquí..."
            variant="outlined"
            sx={{
              flex: 1,
              '& .MuiOutlinedInput-root': {
                fontSize: '0.875rem',
                lineHeight: 1.5,
              },
            }}
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2, borderTop: '1px solid #e0e0e0' }}>
        <Button 
          onClick={handleClose} 
          disabled={isSending}
          sx={{ mr: 1 }}
        >
          Cancelar
        </Button>
        <Button
          onClick={handleSend}
          variant="contained"
          startIcon={isSending ? <CircularProgress size={16} /> : <Send />}
          disabled={isSending || !replyBody.trim()}
          sx={{
            backgroundColor: 'primary.main',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
            minWidth: 120,
          }}
        >
          {isSending ? 'Enviando...' : 'Enviar'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ReplyModalNew;
