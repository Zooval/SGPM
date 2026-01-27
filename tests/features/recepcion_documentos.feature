# Created by Bryan at 10/1/2026
# language: es

Característica: Recepción de documentos
  Como asesor migratorio
  Quiero gestionar los documentos de los solicitantes
  Para garantizar que cumplan con los requisitos del proceso de visa

  Antecedentes:
    Dado que existe un solicitante registrado con un proceso de visa activo


  @criterio1
  Escenario: Registrar documentos entregados por el solicitante
    Dado que el solicitante entrega un documento
    Cuando el asesor registra el documento
    Entonces el documento queda registrado con estado "RECIBIDO"
    Y se asocia al expediente del solicitante

  @criterio2
  Escenario: Marcar el estado de un documento como aprobado o rechazado
    Dado que existe un documento con estado "RECIBIDO"
    Cuando el asesor revisa el contenido del documento y es correcto
    Entonces el asesor marca el documento con estado "APROBADO"

  @criterio3
  Escenario: Registrar observación sobre un documento incorrecto
    Dado que existe un documento con estado "RECIBIDO"
    Cuando el asesor identifica una inconsistencia en el documento
    Entonces el asesor registra una observación
    Y el documento queda marcado con estado "RECHAZADO"

  @criterio4
  Escenario: Habilitar al solicitante para el proceso de visa
    Dado que el solicitante tiene todos los documentos requeridos
    Y todos los documentos están en estado "APROBADO"
    Cuando el asesor marca al solicitante como habilitado
    Entonces el solicitante queda habilitado para el proceso de visa

  @criterio5
  Escenario: Marcar un documento como vencido al superar su fecha de expiración
    Dado que existe un documento con fecha de expiración
    Y el documento se encuentra en estado "APROBADO"
    Cuando la fecha de hoy supera la fecha de expiración del documento
    Entonces el documento queda marcado con estado "VENCIDO"

