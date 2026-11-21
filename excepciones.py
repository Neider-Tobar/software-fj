"""Excepciones personalizadas de Software FJ."""


class SoftwareFJError(Exception):
    """Excepción base del sistema. Todas las demás heredan de ella."""


class ParametroFaltanteError(SoftwareFJError):
    """Falta un parámetro obligatorio."""


class ClienteInvalidoError(SoftwareFJError):
    """Datos de cliente inválidos."""


class ServicioInvalidoError(SoftwareFJError):
    """Parámetros de servicio inválidos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio no está disponible para reservar."""


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no pudo crearse o procesarse correctamente."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Transición de estado u operación no permitida."""


class CalculoInconsistenteError(SoftwareFJError):
    """El cálculo de costos produjo un resultado inconsistente."""
