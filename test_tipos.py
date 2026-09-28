import json
import logging
from datetime import date, datetime

from sqlserver_client import SqlServerClient

def cargar_credenciales():
    with open("config/credenciales.json", "r", encoding="utf-8") as f:
        # Extraemos BBDD directamente aquí
        return json.load(f)

def mostrar_resultado(titulo, result, db_instance=None):
    print(f"\n{'=' * 70}")
    print(titulo)
    print(f"{'=' * 70}")

    if result["error"]:
        print(f"ERROR: {result['error']}")
        return

    print(f"Success  : {result['success']} (Filas: {result['rowcount']})")
    print(f"Duración : {result['duration']} s")
    
    # Si pasamos la instancia y hay filas, imprimimos el JSON nativo
    if db_instance and result.get("rows"):
        print("\nFormato JSON Nativo (con fechas serializadas):")
        # Usamos la nueva función del cliente
        json_output = db_instance.result_to_json(result["rows"])
        print(json_output)

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    
    print("Cargando credenciales...")
    cfg = cargar_credenciales()
    db = SqlServerClient(cfg['BBDD'])

    try:
        # 0. LIMPIEZA PREVIA (Por si una ejecución anterior falló a la mitad)
        db.execute_dml("DROP PROCEDURE IF EXISTS dbo.test_buscar_por_rol")
        db.execute_dml("DROP TABLE IF EXISTS dbo.test_complejo")
        
        # 1. CREAR TABLA CON TIPOS VARIADOS
        result = db.execute_dml("""
            CREATE TABLE dbo.test_complejo (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nombre NVARCHAR(100) NOT NULL,
                fecha_nacimiento DATE NULL,
                fecha_registro DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                saldo DECIMAL(10, 2) NULL,
                datos_json NVARCHAR(MAX) NULL 
                    CHECK (datos_json IS NULL OR ISJSON(datos_json) = 1)
            )
        """)
        mostrar_resultado("1. CREACIÓN DE TABLA COMPLEJA", result)

        if not result["success"]:
            return

        # 2. INSERCIÓN DE DATOS (Fechas, Nulls, Strings JSON)
        datos = [
            (
                "Administrador", 
                date(1985, 10, 25), 
                2500.50, 
                json.dumps({"rol": "admin", "permisos": ["lectura", "escritura", "borrado"]})
            ),
            (
                "Usuario Básico", 
                None, 
                None, 
                json.dumps({"rol": "user", "permisos": ["lectura"]})
            ),
            (
                "Invitado", 
                date(2000, 1, 1), 
                0.00, 
                None  # Nulo en el campo JSON
            )
        ]

        result = db.bulk_insert("""
            INSERT INTO dbo.test_complejo 
                (nombre, fecha_nacimiento, saldo, datos_json)
            VALUES (?, ?, ?, ?)
        """, datos)
        mostrar_resultado("2. INGESTA DE DATOS", result)

        # 3. CONSULTA ESTÁNDAR Y CONVERSIÓN A JSON
        result = db.execute_query("""
            SELECT id, nombre, fecha_nacimiento, fecha_registro, saldo, datos_json
            FROM dbo.test_complejo
        """)
        mostrar_resultado("3. CONSULTA Y SERIALIZACIÓN A JSON", result, db_instance=db)

        # 4. CREAR PROCEDIMIENTO QUE FILTRA USANDO FUNCIONES JSON DE SQL SERVER
        # Vamos a buscar usuarios según un valor dentro de la columna datos_json
        result = db.execute_dml("""
            CREATE PROCEDURE dbo.test_buscar_por_rol
                @rol_buscado NVARCHAR(50)
            AS
            BEGIN
                SELECT id, nombre, saldo 
                FROM dbo.test_complejo
                WHERE JSON_VALUE(datos_json, '$.rol') = @rol_buscado;
            END
        """)
        mostrar_resultado("4. CREACIÓN DE PROCEDIMIENTO CON PARSEO JSON EN SQL", result)

        # 5. EJECUTAR PROCEDIMIENTO ALMACENADO
        result = db.execute_procedure("dbo.test_buscar_por_rol", ["admin"])
        mostrar_resultado("5. EJECUCIÓN DEL PROCEDIMIENTO (Busca Rol 'admin')", result, db_instance=db)

        # 6. LIMPIEZA
        result = db.execute_dml("DROP PROCEDURE dbo.test_buscar_por_rol")
        mostrar_resultado("6. ELIMINACIÓN DEL PROCEDIMIENTO", result)

        result = db.execute_dml("DROP TABLE dbo.test_complejo")
        mostrar_resultado("7. ELIMINACIÓN DE LA TABLA", result)

    finally:
        db.close()
        print("\nPool SQL Server cerrado correctamente.")

if __name__ == "__main__":
    main()