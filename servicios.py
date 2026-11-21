"""Clase abstracta Servicio y tres servicios especializados (polimorfismo)."""
from abc import abstractmethod

from entidades import EntidadBase
from excepciones import CalculoInconsistenteError, ServicioInvalidoError


class Servicio(EntidadBase):
    IVA = 0.19

    def __init__(self, nombre, tarifa_base, disponible=True):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El nombre del servicio es obligatorio")
        if not isinstance(tarifa_base, (int, float)) or isinstance(tarifa_base, bool) or tarifa_base <= 0:
            raise ServicioInvalidoError(f"Tarifa base inválida: {tarifa_base!r}")
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    @abstractmethod
    def validar_parametros(self, duracion) -> None:
        """Valida la duración solicitada según el tipo de servicio."""

    @abstractmethod
    def _costo_bruto(self, duracion) -> float:
        """Costo antes de impuestos y descuentos."""

    @abstractmethod
    def describir(self) -> str:
        ...

    def calcular_costo(self, duracion, impuesto=None, descuento=0.0) -> float:
        """Método con variantes (sobrecarga mediante parámetros opcionales):

        calcular_costo(d)                    -> costo bruto sin impuesto
        calcular_costo(d, impuesto=0.19)     -> costo + impuesto
        calcular_costo(d, descuento=0.10)    -> costo con descuento
        calcular_costo(d, 0.19, 0.10)        -> costo con ambos
        """
        self.validar_parametros(duracion)
        if not 0 <= descuento < 1:
            raise CalculoInconsistenteError(f"Descuento fuera de rango [0,1): {descuento}")
        if impuesto is not None and not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango [0,1]: {impuesto}")
        total = self._costo_bruto(duracion) * (1 - descuento) * (1 + (impuesto or 0))
        if total <= 0:
            raise CalculoInconsistenteError(f"Costo calculado no positivo: {total}")
        return round(total, 2)

    def calcular_costo_con_iva(self, duracion) -> float:
        """Variante rápida: aplica el IVA vigente."""
        return self.calcular_costo(duracion, impuesto=self.IVA)


class ReservaSala(Servicio):
    """Reserva de salas; duración en horas."""

    def __init__(self, nombre, tarifa_hora, capacidad, proyector=False, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or not 1 <= capacidad <= 200:
            raise ServicioInvalidoError(f"Capacidad inválida (1-200): {capacidad!r}")
        self._capacidad = capacidad
        self._proyector = proyector

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 1 <= duracion <= 12:
            raise ServicioInvalidoError(f"Una sala se reserva entre 1 y 12 horas (recibido: {duracion!r})")

    def _costo_bruto(self, duracion):
        return self._tarifa_base * duracion + (20000 if self._proyector else 0)

    def describir(self):
        return (f"Sala '{self.nombre}' | cap. {self._capacidad} | "
                f"proyector: {'sí' if self._proyector else 'no'} | ${self._tarifa_base:,.0f}/h")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos; duración en días."""

    def __init__(self, nombre, tarifa_dia, tipo_equipo, seguro=False, disponible=True):
        super().__init__(nombre, tarifa_dia, disponible)
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ServicioInvalidoError("El tipo de equipo es obligatorio")
        self._tipo = tipo_equipo.strip()
        self._seguro = seguro

    def validar_parametros(self, duracion):
        if not isinstance(duracion, int) or isinstance(duracion, bool) or not 1 <= duracion <= 30:
            raise ServicioInvalidoError(f"Un equipo se alquila entre 1 y 30 días enteros (recibido: {duracion!r})")

    def _costo_bruto(self, duracion):
        base = self._tarifa_base * duracion
        return base * 1.10 if self._seguro else base

    def describir(self):
        return (f"Equipo '{self.nombre}' ({self._tipo}) | seguro: {'sí' if self._seguro else 'no'} | "
                f"${self._tarifa_base:,.0f}/día")


class Asesoria(Servicio):
    """Asesoría especializada; duración en horas."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido {nivel!r}; use {list(self.NIVELES)}")
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("La especialidad es obligatoria")
        self._especialidad = especialidad.strip()
        self._nivel = nivel

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 0.5 <= duracion <= 8:
            raise ServicioInvalidoError(f"Una asesoría dura entre 0.5 y 8 horas (recibido: {duracion!r})")

    def _costo_bruto(self, duracion):
        return self._tarifa_base * duracion * self.NIVELES[self._nivel]

    def describir(self):
        return (f"Asesoría '{self.nombre}' | {self._especialidad} | nivel {self._nivel} | "
                f"${self._tarifa_base:,.0f}/h")
