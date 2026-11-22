"""Clase Reserva: integra cliente, servicio, duración y estado."""
from enum import Enum

from entidades import Cliente, EntidadBase
from excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                         ReservaInvalidaError, ServicioInvalidoError,
                         ServicioNoDisponibleError)
from logger import log
from servicios import Servicio


class EstadoReserva(Enum):
    """Estados posibles; un Enum evita errores de escritura con textos sueltos."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


# Tabla de transiciones permitidas: estado actual -> estados a los que puede pasar.
_TRANSICIONES = {
    EstadoReserva.PENDIENTE: {EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA},
    EstadoReserva.CONFIRMADA: {EstadoReserva.PROCESADA, EstadoReserva.CANCELADA},
    EstadoReserva.PROCESADA: set(),   # estado final
    EstadoReserva.CANCELADA: set(),   # estado final
}


class Reserva(EntidadBase):
    """Reserva de un servicio por un cliente durante una duración dada."""

    _TIPO = "Reserva"

    def __init__(self, cliente, servicio, duracion):
        # Validaciones previas: la reserva solo nace si todo es correcto.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible")
        try:
            servicio.validar_parametros(duracion)
        except ServicioInvalidoError as e:
            # Encadenamiento: se conserva la causa original con `from e`.
            raise ReservaInvalidaError(f"Duración inválida para la reserva: {e}") from e
        super().__init__()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = EstadoReserva.PENDIENTE   # toda reserva inicia pendiente
        self._costo_total = None                 # se calcula al procesar

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def _cambiar_estado(self, nuevo: EstadoReserva, accion: str):
        """Aplica una transición solo si la tabla _TRANSICIONES la permite."""
        if nuevo not in _TRANSICIONES[self._estado]:
            raise OperacionNoPermitidaError(
                f"No se puede {accion} una reserva en estado {self._estado.value}")
        self._estado = nuevo

    def confirmar(self):
        """PENDIENTE -> CONFIRMADA."""
        self._cambiar_estado(EstadoReserva.CONFIRMADA, "confirmar")
        log.info(f"Reserva #{self.id} confirmada")

    def cancelar(self):
        """PENDIENTE o CONFIRMADA -> CANCELADA."""
        self._cambiar_estado(EstadoReserva.CANCELADA, "cancelar")
        log.info(f"Reserva #{self.id} cancelada")

    def procesar(self, descuento=0.0):
        """CONFIRMADA -> PROCESADA, calculando el costo final con IVA y descuento."""
        if EstadoReserva.PROCESADA not in _TRANSICIONES[self._estado]:
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas CONFIRMADAS (estado: {self._estado.value})")
        try:
            costo = self._servicio.calcular_costo(self._duracion, Servicio.IVA, descuento)
        except (CalculoInconsistenteError, ServicioInvalidoError) as e:
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}") from e
        else:
            # Solo si no hubo error se guarda el costo y se cambia el estado.
            self._costo_total = costo
            self._estado = EstadoReserva.PROCESADA
            log.info(f"Reserva #{self.id} procesada. Total: ${costo:,.2f}")
        finally:
            # Se ejecuta SIEMPRE, haya o no error: deja constancia del intento.
            log.info(f"Intento de procesamiento finalizado para reserva #{self.id} "
                     f"(estado: {self._estado.value})")

    def describir(self) -> str:
        costo = f"${self._costo_total:,.2f}" if self._costo_total is not None else "pendiente"
        return (f"Reserva #{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} | "
                f"duración: {self._duracion} | estado: {self._estado.value} | total: {costo}")
