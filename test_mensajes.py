import json
import logging

from sqlserver_client import SqlServerClient

def cargar_credenciales():
    with open("config/credenciales.json", "r", encoding="utf-8") as f:
        return json.load(f)["BBDD"]

def mostrar_resultado(titulo, result):
    print(f"\n{'=' * 70}")
    print(titulo)
    print(f"{'=' * 70}")

    if result["error"]:
        print(f"ERROR: {result['error']}")
        return

    print(f"Success  : {result['success']} (Filas: {result['rowcount']})")
    print(f"Duración : {result['duration']} s")
    
    if result.get("rows"):
        print("\nFilas devueltas:")
        for row in result["rows"]:
            print(f"  {row}")

    # Mostrar específicamente los mensajes capturados
    mensajes = result.get("messages", [])
    if mensajes:
        print("\nMensajes del servidor capturados:")
        for i, msg in enumerate(mensajes, 1):
            print(f"  [Mensaje {i}] {msg}")
    else:
        print("\n(No se capturaron mensajes del servidor)")

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    
    print("Cargando credenciales...")
    cfg = cargar_credenciales()
    db = SqlServerClient(cfg)

    try:
        # 0. LIMPIEZA PREVIA
        db.execute_dml("DROP PROCEDURE IF EXISTS dbo.test_generar_mensajes")

        # 1. CREAR PROCEDIMIENTO CON PRINT Y RAISERROR
        result = db.execute_dml("""
            CREATE PROCEDURE dbo.test_generar_mensajes
            AS
            BEGIN
                -- Emitir mensajes estándar
                PRINT '1. Iniciando el procesamiento de datos...';
                
                PRINT '2. Calculando métricas intermedias...';
                
                -- Emitir un aviso usando RAISERROR con severidad 10 (Informativo)
                RAISERROR ('3. Aviso: Se detectaron valores atípicos (Severidad 10).', 10, 1);
                
                PRINT '4. Proceso finalizado correctamente.';
                
                -- Devolver un pequeño resultset normal para confirmar ejecución
                SELECT 'COMPLETADO' AS estado, 42 AS valor_resultado;
            END
        """)
        mostrar_resultado("1. CREACIÓN DEL PROCEDIMIENTO", result)

        if not result["success"]:
            return

        # 2. EJECUTAR EL PROCEDIMIENTO Y CAPTURAR MENSAJES
        result = db.execute_procedure("dbo.test_generar_mensajes")
        mostrar_resultado("2. EJECUCIÓN DEL PROCEDIMIENTO (Debe mostrar 4 mensajes)", result)

        # 3. PROBAR MENSAJES EN UN BLOQUE ANÓNIMO (DML)
        result = db.execute_dml("""
            PRINT 'Mensaje desde una consulta DML directa (sin procedimiento).'
        """)
        mostrar_resultado("3. EJECUCIÓN DML DIRECTA", result)

        # 4. LIMPIEZA FINAL
        result = db.execute_dml("DROP PROCEDURE dbo.test_generar_mensajes")
        mostrar_resultado("4. LIMPIEZA DEL PROCEDIMIENTO", result)

    finally:
        db.close()
        print("\nPool SQL Server cerrado correctamente.")

if __name__ == "__main__":
    main()