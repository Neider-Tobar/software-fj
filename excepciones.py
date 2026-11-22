"""Excepciones personalizadas de Software FJ.

Todas heredan de SoftwareFJError, de modo que el sistema puede capturar
cualquier error propio con un único `except SoftwareFJError`, o bien
reaccionar de forma distinta según el tipo concreto de falla.
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema; de ella derivan todas las demás."""


class ParametroFaltanteError(SoftwareFJError):
    """Se omitió un parámetro obligatorio al crear un objeto."""


class ClienteInvalidoError(SoftwareFJError):
    """Algún dato personal del cliente no cumple las reglas de validación."""


class ServicioInvalidoError(SoftwareFJError):
    """Los parámetros de un servicio (tarifa, capacidad, duración...) son inválidos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se intentó reservar un servicio marcado como no disponible."""


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no pudo crearse o procesarse (suele encadenar la causa original)."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se solicitó un cambio de estado que el ciclo de vida de la reserva no permite."""


class CalculoInconsistenteError(SoftwareFJError):
    """Un cálculo de costos recibió valores fuera de rango o produjo un resultado absurdo."""
