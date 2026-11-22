"""Clase abstracta base del sistema y la clase Cliente (con encapsulación)."""
import re                          # expresiones regulares para validar el correo
from abc import ABC, abstractmethod  # soporte de clases y métodos abstractos
from itertools import count          # generador de números consecutivos

from excepciones import ClienteInvalidoError, ParametroFaltanteError


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
