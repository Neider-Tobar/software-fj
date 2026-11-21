"""Clase abstracta base y clase Cliente con encapsulación y validaciones."""
import re
from abc import ABC, abstractmethod
from itertools import count

from excepciones import ClienteInvalidoError, ParametroFaltanteError


class EntidadBase(ABC):
    """Clase abstracta que representa cualquier entidad general del sistema."""

    _contador = count(1)

    def __init__(self):
        self._id = next(EntidadBase._contador)

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""

    def __str__(self) -> str:
        return self.describir()


class Cliente(EntidadBase):
    """Cliente con datos personales encapsulados y validados."""

    _EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")

    def __init__(self, nombre=None, documento=None, email=None, telefono=None):
        super().__init__()
        faltantes = [k for k, v in (("nombre", nombre), ("documento", documento),
                                    ("email", email), ("telefono", telefono)) if v in (None, "")]
        if faltantes:
            raise ParametroFaltanteError(f"Faltan parámetros del cliente: {', '.join(faltantes)}")
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono

    # --- Propiedades con validación (datos privados) ---
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3 or any(c.isdigit() for c in valor):
            raise ClienteInvalidoError(f"Nombre inválido: {valor!r}")
        self.__nombre = valor.strip().title()

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor):
        valor = str(valor).strip()
        if not valor.isdigit() or not 6 <= len(valor) <= 12:
            raise ClienteInvalidoError(f"Documento inválido (6-12 dígitos): {valor!r}")
        self.__documento = valor

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not self._EMAIL.match(valor.strip()):
            raise ClienteInvalidoError(f"Correo inválido: {valor!r}")
        self.__email = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = str(valor).strip()
        if not valor.isdigit() or len(valor) != 10:
            raise ClienteInvalidoError(f"Teléfono inválido (10 dígitos): {valor!r}")
        self.__telefono = valor

    def describir(self) -> str:
        return f"Cliente #{self.id}: {self.nombre} | Doc: {self.documento} | {self.email} | Tel: {self.telefono}"
