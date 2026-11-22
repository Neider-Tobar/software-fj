"""Simulación de operaciones válidas e inválidas. La aplicación nunca se detiene."""
from gestor import SistemaGestion
from logger import RUTA_LOG, log
from servicios import AlquilerEquipo, Asesoria, ReservaSala


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
