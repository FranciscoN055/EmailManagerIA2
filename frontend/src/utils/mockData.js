export const generateMockEmails = () => {
  const senders = [
    'Juan Pérez (Estudiante)',
    'Dr. María García (Coordinadora)',
    'Ana Silva (Secretaria Académica)',
    'Prof. Carlos López (Docente)',
    'Rectoría ICIF',
    'Laura Martínez (Estudiante)',
    'Ing. Roberto Torres (Docente)',
    'Decanato de Facultad',
    'Sistema de Notas',
    'Carmen Ruiz (Estudiante)',
    'Dr. Alberto Vásquez (Docente)',
    'Comité Académico',
    'Sofia Hernández (Estudiante)',
    'Biblioteca Central',
    'IT Support ICIF',
    'Ministerio de Educación',
    'Coordinación de Práticas',
    'José Ramírez (Estudiante)',
    'Dra. Patricia Morales (Docente)',
    'Finanzas ICIF'
  ];

  const subjects = [
    // Urgent
    'URGENTE: Problema con sistema de notas - Cierre de período',
    'CRÍTICO: Estudiante hospitalizado durante examen final',
    'EMERGENCIA: Falla eléctrica en laboratorio de computación',
    'URGENTE: Reunión extraordinaria Consejo Académico HOY',
    'CRÍTICO: Acreditación internacional - Documentos faltantes',
    
    // High priority
    'Solicitud de aplazamiento de examen por enfermedad',
    'Problema con calificaciones en el sistema',
    'Reunión Comité Curricular - Confirmación asistencia',
    'Revisión de proyecto de tesis - Plazo vencimiento',
    'Homologación de materias - Estudiante transferido',
    'Solicitud de cambio de horario por trabajo',
    
    // Medium priority
    'Informe mensual de rendimiento académico',
    'Planificación horarios próximo semestre',
    'Actualización de pensum académico',
    'Solicitud de constancia de estudios',
    'Propuesta de nuevo electivo profesional',
    'Evaluación docente - Resultados período',
    
    // Low priority
    'Invitación: Congreso Internacional de Ingeniería',
    'Newsletter: Novedades educativas del mes',
    'Felicitaciones por ranking institucional',
    'Evento de networking alumni',
    'Encuesta de satisfacción estudiantil',
    'Actualización de políticas institucionales'
  ];

  const previews = [
    'Buenos días Directora, espero se encuentre bien. Le escribo para informarle sobre una situación que requiere su atención inmediata...',
    'Estimada Dra. Silva, adjunto encontrará el informe solicitado con las observaciones correspondientes. El análisis muestra...',
    'Directora, necesito su autorización para proceder con el cambio solicitado. Los estudiantes han manifestado su preocupación...',
    'Cordial saludo. Me permito contactarla para solicitar una reunión urgente debido a los inconvenientes presentados...',
    'Apreciada Directora, espero se encuentre bien. Le envío la documentación requerida para el proceso de acreditación...',
    'Buenos días. Adjunto el reporte de calificaciones del período actual. Se observan algunas inconsistencias que deben ser revisadas...',
    'Estimada Directora Silva, los estudiantes del grupo A han solicitado una extensión del plazo para la entrega del proyecto...',
    'Cordial saludo Directora. El Comité Académico ha programado una sesión extraordinaria para tratar temas urgentes del currículo...',
    'Buenos días Dra. Silva. Me dirijo a usted para informarle sobre los avances del proyecto de mejoramiento académico...',
    'Estimada Directora, adjunto encontrará el cronograma de actividades para el próximo período académico...'
  ];

  const urgencyLevels = ['urgent', 'high', 'medium', 'low', 'processed'];
  const urgencyWeights = [5, 15, 40, 30, 10]; // Pesos para distribución realista

  const getWeightedRandomUrgency = () => {
    const random = Math.random() * 100;
    let cumulativeWeight = 0;
    
    for (let i = 0; i < urgencyWeights.length; i++) {
      cumulativeWeight += urgencyWeights[i];
      if (random <= cumulativeWeight) {
        return urgencyLevels[i];
      }
    }
    return 'medium';
  };

  const emails = [];
  const numEmails = 50; // Generar 50 correos para el demo

  for (let i = 0; i < numEmails; i++) {
    const urgency = getWeightedRandomUrgency();
    const isRead = Math.random() > 0.6; // 40% sin leer
    const isStarred = Math.random() > 0.85; // 15% marcados
    
    // Generar timestamp basado en urgencia
    let hoursAgo;
    switch (urgency) {
      case 'urgent':
        hoursAgo = Math.random() * 1; // Última hora
        break;
      case 'high':
        hoursAgo = 1 + Math.random() * 2; // 1-3 horas
        break;
      case 'medium':
        hoursAgo = 3 + Math.random() * 21; // 3-24 horas (hoy)
        break;
      case 'low':
        hoursAgo = 24 + Math.random() * 24; // 24-48 horas (mañana)
        break;
      case 'processed':
        hoursAgo = 48 + Math.random() * 168; // 2 días a 1 semana
        break;
      default:
        hoursAgo = Math.random() * 24;
    }

    const timestamp = new Date(Date.now() - hoursAgo * 60 * 60 * 1000);
    
    // Seleccionar asunto apropiado para la urgencia
    let subjectIndex;
    switch (urgency) {
      case 'urgent':
        subjectIndex = Math.floor(Math.random() * 5);
        break;
      case 'high':
        subjectIndex = 5 + Math.floor(Math.random() * 6);
        break;
      case 'medium':
        subjectIndex = 11 + Math.floor(Math.random() * 6);
        break;
      case 'low':
        subjectIndex = 17 + Math.floor(Math.random() * 6);
        break;
      case 'processed':
        subjectIndex = Math.floor(Math.random() * subjects.length);
        break;
      default:
        subjectIndex = Math.floor(Math.random() * subjects.length);
    }

    // Confianza de IA basada en urgencia (urgente tiene menos confianza por ser más difícil de clasificar)
    let aiConfidence;
    switch (urgency) {
      case 'urgent':
        aiConfidence = 75 + Math.random() * 20; // 75-95%
        break;
      case 'high':
        aiConfidence = 80 + Math.random() * 15; // 80-95%
        break;
      case 'medium':
        aiConfidence = 85 + Math.random() * 12; // 85-97%
        break;
      case 'low':
        aiConfidence = 90 + Math.random() * 8;  // 90-98%
        break;
      case 'processed':
        aiConfidence = 95 + Math.random() * 5;  // 95-100%
        break;
      default:
        aiConfidence = 80 + Math.random() * 15;
    }

    emails.push({
      id: `email-${i + 1}`,
      sender: senders[Math.floor(Math.random() * senders.length)],
      subject: subjects[subjectIndex],
      preview: previews[Math.floor(Math.random() * previews.length)],
      timestamp: timestamp.toISOString(),
      urgency: urgency,
      isRead: urgency === 'processed' ? true : isRead,
      isStarred: isStarred,
      aiConfidence: Math.round(aiConfidence),
      hasAttachments: Math.random() > 0.7, // 30% con archivos adjuntos
      tags: []
    });
  }

  // Ordenar por timestamp (más recientes primero)
  return emails.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
};

export const getEmailsByUrgency = (emails, urgency) => {
  return emails.filter(email => email.urgency === urgency);
};

export const getUnreadCount = (emails) => {
  return emails.filter(email => !email.isRead).length;
};

export const getStarredCount = (emails) => {
  return emails.filter(email => email.isStarred).length;
};

export const getEmailStats = (emails) => {
  const stats = {
    total: emails.length,
    unread: getUnreadCount(emails),
    starred: getStarredCount(emails),
    byUrgency: {
      urgent: getEmailsByUrgency(emails, 'urgent').length,
      high: getEmailsByUrgency(emails, 'high').length,
      medium: getEmailsByUrgency(emails, 'medium').length,
      low: getEmailsByUrgency(emails, 'low').length,
      processed: getEmailsByUrgency(emails, 'processed').length,
    }
  };
  
  return stats;
};