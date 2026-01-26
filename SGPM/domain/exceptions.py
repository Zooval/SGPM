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
