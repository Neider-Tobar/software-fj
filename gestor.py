"""Sistema de gestión: listas internas y operaciones que nunca detienen la aplicación."""
from entidades import Cliente
from excepciones import SoftwareFJError
from logger import log
from reserva import Reserva


class SistemaGestion:
    def __init__(self):
        self.clientes, self.servicios, self.reservas = [], [], []

    def _ejecutar(self, etiqueta, funcion, *args, **kwargs):
        """Ejecuta una operación capturando cualquier error y registrándolo."""
        try:
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as e:
            causa = f" | causa: {e.__cause__!r}" if e.__cause__ else ""
            log.error(f"{etiqueta} FALLÓ [{type(e).__name__}]: {e}{causa}")
            print(f"   [X] {etiqueta}: {type(e).__name__} -> {e}")
            return None
        except Exception as e:  # error inesperado: la app sigue viva
            log.critical(f"{etiqueta} ERROR INESPERADO [{type(e).__name__}]: {e}")
            print(f"   [X] {etiqueta}: error inesperado {type(e).__name__} -> {e}")
            return None
        else:
            log.info(f"{etiqueta} OK")
            print(f"   [OK] {etiqueta}")
            return resultado

    def registrar_cliente(self, **datos):
        c = self._ejecutar("Registrar cliente", Cliente, **datos)
        if c:
            self.clientes.append(c)
        return c

    def crear_servicio(self, clase, *args, **kwargs):
        s = self._ejecutar(f"Crear servicio {clase.__name__}", clase, *args, **kwargs)
        if s:
            self.servicios.append(s)
        return s

    def crear_reserva(self, cliente, servicio, duracion):
        r = self._ejecutar("Crear reserva", Reserva, cliente, servicio, duracion)
        if r:
            self.reservas.append(r)
        return r

    def operar(self, etiqueta, funcion, *args, **kwargs):
        return self._ejecutar(etiqueta, funcion, *args, **kwargs)
