"""Simulación de 12 operaciones: válidas e inválidas. La app nunca se detiene."""
from gestor import SistemaGestion
from logger import RUTA_LOG, log
from servicios import AlquilerEquipo, Asesoria, ReservaSala


def main():
    log.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ ===")
    s = SistemaGestion()

    print("\n1-3. Clientes")
    ana = s.registrar_cliente(nombre="Ana Pérez", documento="1020304050", email="ana@correo.com", telefono="3101234567")
    s.registrar_cliente(nombre="Luis", documento="abc", email="correo-malo", telefono="123")      # inválido
    s.registrar_cliente(nombre="Carlos Gómez", documento="9876543210")                              # parámetros faltantes
    carlos = s.registrar_cliente(nombre="Carlos Gómez", documento="9876543210", email="carlos@fj.co", telefono="3209876543")

    print("\n4-6. Servicios")
    sala = s.crear_servicio(ReservaSala, "Sala Innovación", 50000, 20, proyector=True)
    equipo = s.crear_servicio(AlquilerEquipo, "Portátil Pro", 80000, "Computador", seguro=True)
    asesoria = s.crear_servicio(Asesoria, "Asesoría Cloud", 120000, "Cloud", nivel="senior")
    s.crear_servicio(Asesoria, "Asesoría Mala", -5, "IA", nivel="dios")                             # inválido
    s.crear_servicio(ReservaSala, "Sala Gigante", 40000, 5000)                                      # inválido
    fuera = s.crear_servicio(AlquilerEquipo, "Proyector 4K", 60000, "Video", disponible=False)

    print("\nCatálogo (polimorfismo en describir):")
    for sv in s.servicios:
        print("  ", sv.describir())

    print("\n7-9. Reservas")
    r1 = s.crear_reserva(ana, sala, 3)
    r2 = s.crear_reserva(carlos, equipo, 5)
    s.crear_reserva(ana, sala, 40)             # duración inválida (encadenada)
    s.crear_reserva(carlos, fuera, 2)          # servicio no disponible
    s.crear_reserva(None, asesoria, 1)         # cliente inválido
    r3 = s.crear_reserva(carlos, asesoria, 2)

    print("\n10-12. Confirmación, cancelación y procesamiento")
    s.operar("Procesar reserva sin confirmar", r1.procesar)                 # no permitido
    s.operar("Confirmar reserva 1", r1.confirmar)
    s.operar("Procesar reserva 1 (10% desc.)", r1.procesar, 0.10)
    s.operar("Cancelar reserva ya procesada", r1.cancelar)                  # no permitido
    s.operar("Confirmar reserva 2", r2.confirmar)
    s.operar("Procesar reserva 2 con descuento absurdo", r2.procesar, 1.5)  # cálculo inconsistente
    s.operar("Cancelar reserva 3", r3.cancelar)
    s.operar("Confirmar reserva 3 cancelada", r3.confirmar)                 # no permitido

    print("\nSobrecarga de cálculo de costos (Sala, 3 h):")
    print("  Solo base         :", sala.calcular_costo(3))
    print("  Con IVA           :", sala.calcular_costo(3, impuesto=0.19))
    print("  Con descuento 10% :", sala.calcular_costo(3, descuento=0.10))
    print("  IVA + descuento   :", sala.calcular_costo(3, 0.19, 0.10))
    print("  Atajo con IVA     :", sala.calcular_costo_con_iva(3))

    print("\nEstado final de reservas:")
    for r in s.reservas:
        print("  ", r.describir())

    log.info("=== FIN DE SIMULACIÓN: la aplicación continuó estable ===")
    print(f"\nSimulación finalizada sin interrupciones. Log en: {RUTA_LOG}")


if __name__ == "__main__":
    main()
