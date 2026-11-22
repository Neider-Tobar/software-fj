"""Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas.

POO + manejo avanzado de excepciones, sin base de datos.
Ejecución: python software_fj_completo.py
"""
import logging
import os
import re
from abc import ABC, abstractmethod
from enum import Enum
from itertools import count


# ========================================================================
# MÓDULO: excepciones.py
# ========================================================================
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


# ========================================================================
# MÓDULO: logger.py
# ========================================================================
# Ruta absoluta de la carpeta "logs" ubicada junto a este archivo.
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "software_fj.log")


def _crear_logger() -> logging.Logger:
    """Crea (una sola vez) el logger del sistema y lo devuelve."""
    logger = logging.getLogger("software_fj")  # obtiene un logger con nombre propio
    if logger.handlers:                         # si ya fue configurado, no se duplica
        return logger
    logger.setLevel(logging.INFO)               # registra INFO, WARNING, ERROR y CRITICAL
    logger.propagate = False                    # evita imprimir los mensajes dos veces
    try:
        os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)       # crea logs/ si no existe
        manejador = logging.FileHandler(RUTA_LOG, encoding="utf-8")  # escribe en el archivo
    except OSError:
        # Si el disco no permite escribir, la app NO se detiene: usa la consola.
        manejador = logging.StreamHandler()
    # Formato de cada línea: fecha | nivel | mensaje
    manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    logger.addHandler(manejador)                # asocia el manejador al logger
    return logger


# Logger global que importan los demás módulos: `from logger import log`.
log = _crear_logger()


# ========================================================================
# MÓDULO: entidades.py
# ========================================================================
class EntidadBase(ABC):
    """Entidad general del sistema: todo objeto de negocio tiene id y descripción."""

    _TIPO = "Entidad"   # cada familia de clases redefine este nombre (Cliente, Servicio, Reserva)
    _secuencias = {}    # un contador de ids independiente por cada _TIPO

    def __init__(self):
        # Toma (o crea) el contador del tipo y asigna el siguiente número como id.
        secuencia = EntidadBase._secuencias.setdefault(self._TIPO, count(1))
        self._id = next(secuencia)

    @property
    def id(self) -> int:
        """Identificador de solo lectura (no puede modificarse desde fuera)."""
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad concreta devuelve su descripción en texto."""

    def __str__(self) -> str:
        # Al imprimir cualquier entidad se usa su descripción (polimorfismo).
        return self.describir()


class Cliente(EntidadBase):
    """Cliente con datos personales privados y validados."""

    _TIPO = "Cliente"
    # Patrón simple de correo: texto@dominio.ext
    _PATRON_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")

    def __init__(self, nombre=None, documento=None, email=None, telefono=None):
        # 1) Verifica que no falte ningún parámetro obligatorio.
        datos = {"nombre": nombre, "documento": documento, "email": email, "telefono": telefono}
        faltantes = [campo for campo, valor in datos.items() if valor in (None, "")]
        if faltantes:
            raise ParametroFaltanteError(f"Faltan parámetros del cliente: {', '.join(faltantes)}")
        # 2) Asigna mediante las propiedades, que validan cada valor.
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono
        # 3) El id se asigna al final: los clientes inválidos no consumen números.
        super().__init__()

    # ---- Atributos privados (name mangling: __x) con propiedades validadas ----
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        # Mínimo 3 caracteres; solo letras, espacios, apóstrofes o guiones.
        if (not isinstance(valor, str) or len(valor.strip()) < 3
                or not all(c.isalpha() or c in " '-" for c in valor)):
            raise ClienteInvalidoError(f"Nombre inválido: {valor!r}")
        self.__nombre = valor.strip().title()  # normaliza: "ana pérez" -> "Ana Pérez"

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor):
        valor = str(valor).strip()
        # Solo dígitos, entre 6 y 12 caracteres.
        if not valor.isdigit() or not 6 <= len(valor) <= 12:
            raise ClienteInvalidoError(f"Documento inválido (6-12 dígitos): {valor!r}")
        self.__documento = valor

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not self._PATRON_EMAIL.match(valor.strip()):
            raise ClienteInvalidoError(f"Correo inválido: {valor!r}")
        self.__email = valor.strip().lower()  # los correos se guardan en minúscula

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = str(valor).strip()
        # Exactamente 10 dígitos (formato móvil colombiano).
        if not valor.isdigit() or len(valor) != 10:
            raise ClienteInvalidoError(f"Teléfono inválido (10 dígitos): {valor!r}")
        self.__telefono = valor

    def describir(self) -> str:
        """Sobrescribe el método abstracto de EntidadBase."""
        return (f"Cliente #{self.id}: {self.nombre} | Doc: {self.documento} | "
                f"{self.email} | Tel: {self.telefono}")


# ========================================================================
# MÓDULO: servicios.py
# ========================================================================
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


# ========================================================================
# MÓDULO: reserva.py
# ========================================================================
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


# ========================================================================
# MÓDULO: gestor.py
# ========================================================================
class SistemaGestion:
    """Guarda clientes, servicios y reservas en listas y evita que un error detenga el programa."""

    def __init__(self):
        self.clientes = []    # lista de objetos Cliente
        self.servicios = []   # lista de objetos Servicio (cualquier subclase)
        self.reservas = []    # lista de objetos Reserva
        self.exitos = 0       # contador de operaciones exitosas
        self.fallos = 0       # contador de operaciones fallidas

    def _ejecutar(self, etiqueta, funcion, *args, **kwargs):
        """Ejecuta `funcion` capturando cualquier error; devuelve su resultado o None."""
        try:
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as e:
            # Error previsto: se registra con su causa original (si fue encadenado).
            causa = f" | causa: {e.__cause__!r}" if e.__cause__ else ""
            log.error(f"{etiqueta} FALLÓ [{type(e).__name__}]: {e}{causa}")
            print(f"   [X] {etiqueta}: {type(e).__name__} -> {e}")
            self.fallos += 1
            return None
        except Exception as e:  # noqa: BLE001 - error imprevisto: la app debe seguir viva
            log.critical(f"{etiqueta} ERROR INESPERADO [{type(e).__name__}]: {e}")
            print(f"   [X] {etiqueta}: error inesperado {type(e).__name__} -> {e}")
            self.fallos += 1
            return None
        else:
            log.info(f"{etiqueta} OK")
            print(f"   [OK] {etiqueta}")
            self.exitos += 1
            return resultado

    def _registrar(self, lista, etiqueta, fabrica, *args, **kwargs):
        """Crea un objeto con `fabrica`; si tiene éxito lo agrega a `lista`."""
        objeto = self._ejecutar(etiqueta, fabrica, *args, **kwargs)
        if objeto is not None:
            lista.append(objeto)
        return objeto

    # ---- Altas ----
    def registrar_cliente(self, **datos):
        return self._registrar(self.clientes, "Registrar cliente", Cliente, **datos)

    def crear_servicio(self, clase, *args, **kwargs):
        return self._registrar(self.servicios, f"Crear servicio {clase.__name__}", clase, *args, **kwargs)

    def crear_reserva(self, cliente, servicio, duracion):
        return self._registrar(self.reservas, "Crear reserva", Reserva, cliente, servicio, duracion)

    # ---- Cambios de estado (toleran que la reserva sea None si falló su creación) ----
    @staticmethod
    def _aplicar(reserva, accion, *args):
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError(f"No hay una reserva válida para {accion}")
        return getattr(reserva, accion)(*args)

    def confirmar_reserva(self, reserva):
        return self._ejecutar("Confirmar reserva", self._aplicar, reserva, "confirmar")

    def cancelar_reserva(self, reserva):
        return self._ejecutar("Cancelar reserva", self._aplicar, reserva, "cancelar")

    def procesar_reserva(self, reserva, descuento=0.0):
        return self._ejecutar("Procesar reserva", self._aplicar, reserva, "procesar", descuento)

    def resumen(self) -> str:
        """Texto con los totales de la sesión."""
        return (f"Clientes: {len(self.clientes)} | Servicios: {len(self.servicios)} | "
                f"Reservas: {len(self.reservas)} | Operaciones OK: {self.exitos} | Fallidas: {self.fallos}")


# ========================================================================
# MÓDULO: main.py
# ========================================================================
def main():
    log.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ ===")
    s = SistemaGestion()  # sistema con listas internas vacías

    print("\n1. Clientes (válidos, inválidos y con datos faltantes)")
    ana = s.registrar_cliente(nombre="Ana Pérez", documento="1020304050", email="ana@correo.com", telefono="3101234567")
    s.registrar_cliente(nombre="Luis", documento="abc", email="correo-malo", telefono="123")   # inválido
    s.registrar_cliente(nombre="Carlos Gómez", documento="9876543210")                           # faltan datos
    carlos = s.registrar_cliente(nombre="Carlos Gómez", documento="9876543210", email="carlos@fj.co", telefono="3209876543")

    print("\n2. Servicios (válidos, inválidos y no disponible)")
    sala = s.crear_servicio(ReservaSala, "Sala Innovación", 50000, 20, proyector=True)
    equipo = s.crear_servicio(AlquilerEquipo, "Portátil Pro", 80000, "Computador", seguro=True)
    asesoria = s.crear_servicio(Asesoria, "Asesoría Cloud", 120000, "Cloud", nivel="senior")
    s.crear_servicio(Asesoria, "Asesoría Mala", -5, "IA", nivel="senior")      # tarifa negativa
    s.crear_servicio(ReservaSala, "Sala Gigante", 40000, 5000)                  # inválido
    fuera = s.crear_servicio(AlquilerEquipo, "Proyector 4K", 60000, "Video", disponible=False)

    print("\nCatálogo (polimorfismo: cada servicio se describe a su manera):")
    for servicio in s.servicios:
        print("  ", servicio.describir())

    print("\n3. Reservas (exitosas y fallidas)")
    r1 = s.crear_reserva(ana, sala, 3)
    r2 = s.crear_reserva(carlos, equipo, 5)
    s.crear_reserva(ana, sala, 40)            # duración inválida (excepción encadenada)
    s.crear_reserva(carlos, fuera, 2)         # servicio no disponible
    s.crear_reserva(None, asesoria, 1)        # cliente inválido
    r3 = s.crear_reserva(carlos, asesoria, 2)

    print("\n4. Confirmación, cancelación y procesamiento")
    s.procesar_reserva(r1)                    # no permitido: sigue PENDIENTE
    s.confirmar_reserva(r1)
    s.procesar_reserva(r1, descuento=0.10)    # correcto: aplica IVA y 10 % de descuento
    s.cancelar_reserva(r1)                    # no permitido: ya está PROCESADA
    s.confirmar_reserva(r2)
    s.procesar_reserva(r2, descuento=1.5)     # cálculo inconsistente
    s.cancelar_reserva(r3)
    s.confirmar_reserva(r3)                   # no permitido: ya está CANCELADA
    s.confirmar_reserva(None)                 # reserva inexistente (creación fallida)

    print("\n5. Variantes del cálculo de costos (sala, 3 horas)")
    print("  Solo base         :", sala.calcular_costo(3))
    print("  Con IVA           :", sala.calcular_costo(3, impuesto=0.19))
    print("  Con descuento 10% :", sala.calcular_costo(3, descuento=0.10))
    print("  IVA + descuento   :", sala.calcular_costo(3, 0.19, 0.10))
    print("  Atajo con IVA     :", sala.calcular_costo_con_iva(3))

    print("\nEstado final de las reservas:")
    for reserva in s.reservas:
        print("  ", reserva.describir())

    print("\nResumen:", s.resumen())
    log.info(f"=== FIN DE SIMULACIÓN: {s.resumen()} ===")
    print(f"Simulación finalizada sin interrupciones. Log en: {RUTA_LOG}")


if __name__ == "__main__":
    main()
