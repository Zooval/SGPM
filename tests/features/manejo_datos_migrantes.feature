# Created by anthony at 10/1/2026
# language: es

Característica: Manejo de datos de los migrantes
  Se encarga del registro de la información de los clientes que solicitan un proceso migratorio,
  la actualización de la información de los mismos, en sí la gestión de los migrantes.

  Escenario: Registro exitoso de un solicitante con información válida
    Dado que el gestor migratorio inicia un nuevo registro de solicitante
    Cuando ingresa información biográfica y migratoria válida del solicitante
    Entonces el sistema crea el expediente digital del solicitante
    Y genera un identificador único del expediente
    Y registra la fecha y hora de inicio del proceso migratorio

  Escenario: Prevención de inicio de múltiples procesos para un mismo solicitante
    Dado que existe un expediente migratorio activo asociado a un solicitante
    Cuando el gestor migratorio intenta iniciar un nuevo proceso migratorio para el mismo solicitante
    Entonces el sistema impide la creación de un nuevo expediente
    Y notifica al gestor que el solicitante ya cuenta con un proceso migratorio activo

  Escenario: Validación de coherencia de la información biográfica del solicitante
    Dado que el gestor migratorio ingresa la información del solicitante
    Cuando se detecta información biográfica inconsistente
    Entonces el sistema identifica la inconsistencia
    Y notifica al gestor que la información debe ser corregida antes de continuar

  Escenario: Disponibilidad del expediente digital para seguimiento del proceso
    Dado que un expediente migratorio ha sido registrado correctamente
    Cuando el gestor migratorio consulta el expediente del solicitante
    Entonces el sistema muestra la información biográfica y migratoria del solicitante
    Y presenta el estado actual del proceso migratorio
    Y permite su seguimiento conforme a las etapas definidas por el negocio