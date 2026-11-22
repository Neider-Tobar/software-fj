"""Configuración del archivo de logs.

Es el único uso de archivos del sistema: toda la información de negocio
vive en objetos y listas en memoria (no hay base de datos).
"""
import logging  # módulo estándar de registro de eventos
import os       # manejo de rutas y creación de carpetas

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
