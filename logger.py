"""Configuración del archivo de logs (único uso de archivos del sistema)."""
import logging
import os

RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "software_fj.log")


def obtener_logger() -> logging.Logger:
    logger = logging.getLogger("software_fj")
    if not logger.handlers:
        os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(RUTA_LOG, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
        logger.addHandler(handler)
    return logger


log = obtener_logger()
