"""Clase abstracta Servicio y tres servicios especializados (polimorfismo)."""
from abc import abstractmethod

from entidades import EntidadBase
from excepciones import CalculoInconsistenteError, ServicioInvalidoError


def _es_numero(valor) -> bool:
    """True si es int o float. Se excluye bool, porque True/False serían 1/0."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _texto_obligatorio(valor, campo: str) -> str:
    """Valida que sea un texto no vacío y lo devuelve sin espacios sobrantes."""
    if not isinstance(valor, str) or not valor.strip():
        raise ServicioInvalidoError(f"El campo '{campo}' es obligatorio")
    return valor.strip()


class Servicio(EntidadBase):
    """Servicio genérico. Las subclases definen validación, costo bruto y descripción."""

    _TIPO = "Servicio"
    IVA = 0.19  # impuesto vigente usado por las variantes de cálculo

    def __init__(self, nombre, tarifa_base, disponible=True):
        # Valida los datos comunes a todos los servicios.
        nombre = _texto_obligatorio(nombre, "nombre")
        if not _es_numero(tarifa_base) or tarifa_base <= 0:
            raise ServicioInvalidoError(f"Tarifa base inválida: {tarifa_base!r}")
        super().__init__()                     # id asignado solo si todo es válido
        self._nombre = nombre
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    # ---- Métodos abstractos: cada servicio los implementa a su manera ----
    @abstractmethod
    def validar_parametros(self, duracion) -> None:
        """Lanza ServicioInvalidoError si la duración no es válida para este servicio."""

    @abstractmethod
    def _costo_bruto(self, duracion) -> float:
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def describir(self) -> str:
        """Descripción legible del servicio."""

    # ---- Método con variantes (sobrecarga mediante parámetros opcionales) ----
    def calcular_costo(self, duracion, impuesto=None, descuento=0.0) -> float:
        """Calcula el costo final. Variantes de uso:

        calcular_costo(d)                 -> costo bruto
        calcular_costo(d, impuesto=0.19)  -> con impuesto
        calcular_costo(d, descuento=0.10) -> con descuento
        calcular_costo(d, 0.19, 0.10)     -> con impuesto y descuento
        """
        self.validar_parametros(duracion)  # polimorfismo: cada subclase valida distinto
        if not _es_numero(descuento) or not 0 <= descuento < 1:
            raise CalculoInconsistenteError(f"Descuento fuera de rango [0,1): {descuento!r}")
        if impuesto is not None and (not _es_numero(impuesto) or not 0 <= impuesto <= 1):
            raise CalculoInconsistenteError(f"Impuesto fuera de rango [0,1]: {impuesto!r}")
        # Fórmula: bruto x (1 - descuento) x (1 + impuesto)
        total = self._costo_bruto(duracion) * (1 - descuento) * (1 + (impuesto or 0))
        if total <= 0:  # defensa ante resultados absurdos
            raise CalculoInconsistenteError(f"Costo calculado no positivo: {total}")
        return round(total, 2)

    def calcular_costo_con_iva(self, duracion) -> float:
        """Atajo: costo con el IVA vigente y sin descuento."""
        return self.calcular_costo(duracion, impuesto=self.IVA)


class ReservaSala(Servicio):
    """Reserva de salas. La duración se mide en horas (1 a 12)."""

    CARGO_PROYECTOR = 20000  # valor fijo si la sala incluye proyector

    def __init__(self, nombre, tarifa_hora, capacidad, proyector=False, disponible=True):
        # Valida lo propio de la sala antes de crear el objeto.
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or not 1 <= capacidad <= 200:
            raise ServicioInvalidoError(f"Capacidad inválida (1-200): {capacidad!r}")
        super().__init__(nombre, tarifa_hora, disponible)
        self._capacidad = capacidad
        self._proyector = bool(proyector)

    def validar_parametros(self, duracion):
        if not _es_numero(duracion) or not 1 <= duracion <= 12:
            raise ServicioInvalidoError(f"Una sala se reserva entre 1 y 12 horas (recibido: {duracion!r})")

    def _costo_bruto(self, duracion):
        # Tarifa por hora x horas, más el cargo fijo del proyector si aplica.
        return self._tarifa_base * duracion + (self.CARGO_PROYECTOR if self._proyector else 0)

    def describir(self):
        return (f"Sala '{self.nombre}' | cap. {self._capacidad} | "
                f"proyector: {'sí' if self._proyector else 'no'} | ${self._tarifa_base:,.0f}/h")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos. La duración se mide en días enteros (1 a 30)."""

    RECARGO_SEGURO = 1.10  # el seguro encarece el alquiler un 10 %

    def __init__(self, nombre, tarifa_dia, tipo_equipo, seguro=False, disponible=True):
        tipo_equipo = _texto_obligatorio(tipo_equipo, "tipo de equipo")
        super().__init__(nombre, tarifa_dia, disponible)
        self._tipo_equipo = tipo_equipo
        self._seguro = bool(seguro)

    def validar_parametros(self, duracion):
        if not isinstance(duracion, int) or isinstance(duracion, bool) or not 1 <= duracion <= 30:
            raise ServicioInvalidoError(f"Un equipo se alquila entre 1 y 30 días enteros (recibido: {duracion!r})")

    def _costo_bruto(self, duracion):
        base = self._tarifa_base * duracion
        return base * self.RECARGO_SEGURO if self._seguro else base

    def describir(self):
        return (f"Equipo '{self.nombre}' ({self._tipo_equipo}) | "
                f"seguro: {'sí' if self._seguro else 'no'} | ${self._tarifa_base:,.0f}/día")


class Asesoria(Servicio):
    """Asesoría especializada. La duración se mide en horas (0.5 a 8)."""

    # Multiplicador de la tarifa según la experiencia del asesor.
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido {nivel!r}; use {list(self.NIVELES)}")
        especialidad = _texto_obligatorio(especialidad, "especialidad")
        super().__init__(nombre, tarifa_hora, disponible)
        self._especialidad = especialidad
        self._nivel = nivel

    def validar_parametros(self, duracion):
        if not _es_numero(duracion) or not 0.5 <= duracion <= 8:
            raise ServicioInvalidoError(f"Una asesoría dura entre 0.5 y 8 horas (recibido: {duracion!r})")

    def _costo_bruto(self, duracion):
        return self._tarifa_base * duracion * self.NIVELES[self._nivel]

    def describir(self):
        return (f"Asesoría '{self.nombre}' | {self._especialidad} | nivel {self._nivel} | "
                f"${self._tarifa_base:,.0f}/h")
