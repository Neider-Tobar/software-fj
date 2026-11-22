"""Sistema de gestión: listas internas y ejecución protegida de operaciones."""
from entidades import Cliente
from excepciones import ReservaInvalidaError, SoftwareFJError
from logger import log
from reserva import Reserva


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
