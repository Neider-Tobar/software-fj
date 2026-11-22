# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Python 3.8+ · sin librerías externas · sin base de datos.  
Ejecución: `python main.py` (es una simulación automática; no pide datos).

## Estructura
| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y 7 derivadas) |
| `logger.py` | Configuración del log `logs/software_fj.log` (único uso de archivos) |
| `entidades.py` | `EntidadBase` (abstracta) y `Cliente` (atributos privados + propiedades validadas) |
| `servicios.py` | `Servicio` (abstracta) + `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reserva.py` | `Reserva` y `EstadoReserva`: PENDIENTE → CONFIRMADA → PROCESADA / CANCELADA |
| `gestor.py` | `SistemaGestion`: listas internas y ejecución protegida de operaciones |
| `main.py` | Simulación de operaciones válidas e inválidas |

## Principios aplicados
- **Abstracción:** `EntidadBase` y `Servicio` con métodos abstractos.
- **Herencia y polimorfismo:** los tres servicios sobrescriben validación, costo y descripción.
- **Encapsulación:** datos del cliente privados con setters que validan.
- **Sobrecarga:** `calcular_costo(duracion, impuesto=None, descuento=0.0)` con 4 variantes.
- **Excepciones:** personalizadas, `try/except/else/finally` y encadenamiento con `raise ... from`.
- **Logs:** todo evento y error queda registrado; la aplicación nunca se detiene.

## Integrantes
- [Nombre completo]
