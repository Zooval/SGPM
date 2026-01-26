# Created by ximen at 10/1/2026
# language: es




Característica: Recepción de documentos
  Como asesor migratorio
  Quiero gestionar los documentos de los migrantes
  Para validar que cumplan con los requisitos del proceso de visa

  Antecedentes:
    Dado que existe un migrante registrado con un proceso de visa activo

  @criterio1
  Escenario: Registrar documentos del migrante en un proceso de visa
    Dado que el migrante entrega su carpeta con los documentos necesarios
    Cuando el asesor  revisa la carpeta con los documentos
    Entonces  registra los documentos
    Y se habilita el perfil del migrante para el proceso de visa

  @criterio2
  Escenario: Registro de observaciones por documentos incorrectos
    Cuando el asesor verifica la correctitud de los documentos
    Y encuentra inconsistencias en los documentos
    Entonces el asesor registra las observaciones
    Y se notifica al migrante los cambios a realizar

  @criterio3
  Escenario: Identificación de documentos faltantes
    Dado que el migrante no ha entregado todos los documentos requeridos
    Cuando se valida la completitud de los documentos
    Entonces el expediente queda marcado como incompleto