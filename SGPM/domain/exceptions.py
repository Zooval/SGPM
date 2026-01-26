class DomainError(Exception):
    """Base de errores de dominio."""


class EstadoSolicitudInvalidoError(DomainError):
    pass


class DocumentoInvalidoError(DomainError):
    pass


class DocumentoExpiradoError(DomainError):
    pass


class CitaInvalidaError(DomainError):
    pass


class ReglaNegocioError(DomainError):
    pass


class TareaYaAsignadaError(DomainError):
    """Error cuando se intenta asignar una tarea ya asignada."""
    pass


class TransicionEstadoTareaNoPermitida(DomainError):
    """Error cuando la transición de estado de una tarea no es válida."""
    pass


class TareaNoEncontradaError(DomainError):
    """Error cuando no se encuentra una tarea."""
    pass
