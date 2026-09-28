import json
from sqlserver_client import SqlServerClient

with open("config/credenciales.json", "r") as f:
    cfg = json.load(f)["BBDD"]

with SqlServerClient(cfg) as db:
    # 1. Crear SP con múltiples cursores
    db.execute_dml("""
        CREATE PROCEDURE dbo.test_multi_cursor
        AS
        BEGIN
            PRINT 'Generando primer reporte...';
            SELECT 1 AS id, 'Ventas' AS departamento;
            
            PRINT 'Generando segundo reporte...';
            SELECT 'Madrid' AS ciudad, 2500 AS total;
            
            SELECT 'Sin mensajes previos' AS estado;
        END
    """)

    # 2. Ejecutar y mostrar
    result = db.execute_procedure("dbo.test_multi_cursor")
    
    print(f"Total de cursores capturados: {len(result.get('resultsets', []))}")
    
    for i, rs in enumerate(result.get("resultsets", [])):
        print(f"\n--- Cursor {i + 1} ---")
        for row in rs["rows"]:
            print(row)
            
    print("\nMensajes capturados:")
    for msg in result["messages"]:
        print(f" - {msg}")

    # 3. Limpiar
    db.execute_dml("DROP PROCEDURE dbo.test_multi_cursor")