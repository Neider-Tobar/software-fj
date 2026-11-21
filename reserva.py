"""Clase Reserva: integra cliente, servicio, duración y estado."""
from entidades import Cliente, EntidadBase
from excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                         ReservaInvalidaError, ServicioInvalidoError,
                         ServicioNoDisponibleError)
from logger import log
from servicios import Servicio


class Reserva(EntidadBase):
    PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA = "PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA"

    def __init__(self, cliente, servicio, duracion):
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible")
        try:
            servicio.validar_parametros(duracion)
        except ServicioInvalidoError as e:
            # Encadenamiento de excepciones
            raise ReservaInvalidaError(f"Duración inválida para la reserva: {e}") from e
        self._cliente, self._servicio, self._duracion = cliente, servicio, duracion
        self._estado = self.PENDIENTE
        self._costo_total = None

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self):
        if self._estado != self.PENDIENTE:
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva en estado {self._estado}")
        self._estado = self.CONFIRMADA
        log.info(f"Reserva #{self.id} confirmada")

    def cancelar(self):
        if self._estado in (self.CANCELADA, self.PROCESADA):
            raise OperacionNoPermitidaError(f"No se puede cancelar una reserva en estado {self._estado}")
        self._estado = self.CANCELADA
        log.info(f"Reserva #{self.id} cancelada")

    def procesar(self, descuento=0.0):
        """Procesa la reserva calculando el costo final (try/except/else/finally)."""
        if self._estado != self.CONFIRMADA:
            raise OperacionNoPermitidaError(f"Solo se procesan reservas CONFIRMADAS (estado: {self._estado})")
        try:
            costo = self._servicio.calcular_costo(self._duracion, Servicio.IVA, descuento)
        except CalculoInconsistenteError as e:
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}") from e
        else:
            self._costo_total = costo
            self._estado = self.PROCESADA
            log.info(f"Reserva #{self.id} procesada. Total: ${costo:,.2f}")
        finally:
            log.info(f"Intento de procesamiento finalizado para reserva #{self.id} (estado: {self._estado})")

    def describir(self):
        costo = f"${self._costo_total:,.2f}" if self._costo_total else "pendiente"
        return (f"Reserva #{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} | "
                f"duración: {self._duracion} | estado: {self._estado} | total: {costo}")
