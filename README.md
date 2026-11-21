# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto en Python 3.8+ (sin librerías externas, sin base de datos). Ejecución: `python main.py`

## Estructura
| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y 7 derivadas) |
| `logger.py` | Configuración del log (`logs/software_fj.log`), único uso de archivos |
| `entidades.py` | `EntidadBase` (abstracta) y `Cliente` (atributos privados + propiedades validadas) |
| `servicios.py` | `Servicio` (abstracta) + `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reserva.py` | `Reserva`: estados PENDIENTE → CONFIRMADA → PROCESADA / CANCELADA |
| `gestor.py` | `SistemaGestion`: listas internas y ejecución protegida de operaciones |
| `main.py` | Simulación de 12+ operaciones válidas e inválidas |

## Conceptos aplicados
- **Abstracción:** `EntidadBase` y `Servicio` (métodos abstractos `describir`, `validar_parametros`, `_costo_bruto`).
- **Herencia y polimorfismo:** los tres servicios sobrescriben validación, costo y descripción.
- **Encapsulación:** datos del cliente privados (`__nombre`, etc.) con setters que validan.
- **Sobrecarga:** `calcular_costo(duracion, impuesto=None, descuento=0.0)` admite 4 variantes, más `calcular_costo_con_iva`.
- **Excepciones:** personalizadas; `try/except`, `try/except/else/finally` (`Reserva.procesar`, `SistemaGestion._ejecutar`); encadenamiento con `raise ... from e`.
- **Logs:** todo evento y error se registra; la aplicación nunca se detiene.

## Reparto sugerido (5 integrantes)
1. `excepciones.py` + `logger.py` 2. `entidades.py` (Cliente) 3. `servicios.py` 4. `reserva.py` 5. `gestor.py` + `main.py` + README
