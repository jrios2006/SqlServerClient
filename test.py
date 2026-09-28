import json
import logging

from sqlserver_client import SqlServerClient


def cargar_credenciales():
    with open(
        "config/credenciales.json",
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def mostrar_resultado(titulo, result):
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)

    print(f"success   : {result['success']}")
    print(f"rowcount  : {result['rowcount']}")
    print(f"duration  : {result['duration']} s")
    print(f"metrics   : {result['metrics']}")

    if result["error"]:
        print(f"ERROR     : {result['error']}")

    if result["rows"]:
        print("rows:")
        for row in result["rows"]:
            print(f"  {row}")


def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("Cargando credenciales...")
    cfg = cargar_credenciales()

    db = SqlServerClient(cfg["BBDD"])

    try:

        # ==========================================================
        # 1. HORA DEL SERVIDOR
        # ==========================================================

        result = db.execute_query(
            """
            SELECT
                GETDATE() AS fecha_hora_servidor,
                @@SERVERNAME AS servidor,
                DB_NAME() AS base_datos
            """
        )

        mostrar_resultado(
            "1. INFORMACIÓN DEL SERVIDOR",
            result,
        )

        # ==========================================================
        # 2. CREAR TABLA
        # ==========================================================

        result = db.execute_dml(
            """
            CREATE TABLE dbo.test_sqlserver_client (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nombre NVARCHAR(100) NOT NULL,
                valor INT NOT NULL,
                fecha DATETIME2 NOT NULL DEFAULT SYSDATETIME()
            )
            """
        )

        mostrar_resultado(
            "2. CREACIÓN DE TABLA",
            result,
        )

        if not result["success"]:
            return

        # ==========================================================
        # 3. INSERT MASIVO
        # ==========================================================

        datos = [
            ("Juan", 10),
            ("Ana", 20),
            ("Pedro", 30),
            ("Laura", 40),
            ("Carlos", 50),
        ]

        result = db.bulk_insert(
            """
            INSERT INTO dbo.test_sqlserver_client
                (nombre, valor)
            VALUES (?, ?)
            """,
            datos,
        )

        mostrar_resultado(
            "3. INGESTA DE DATOS",
            result,
        )

        # ==========================================================
        # 4. CONTAR REGISTROS
        # ==========================================================

        result = db.execute_scalar(
            """
            SELECT COUNT(*)
            FROM dbo.test_sqlserver_client
            """
        )

        mostrar_resultado(
            "4. NÚMERO DE REGISTROS",
            result,
        )

        if result["success"]:
            print(
                f"\nRegistros creados: {result['value']}"
            )

        # ==========================================================
        # 5. CONSULTA PARAMETRIZADA
        # ==========================================================

        result = db.execute_query(
            """
            SELECT
                id,
                nombre,
                valor,
                fecha
            FROM dbo.test_sqlserver_client
            WHERE valor >= ?
            ORDER BY id
            """,
            [30],
        )

        mostrar_resultado(
            "5. CONSULTA PARAMETRIZADA",
            result,
        )

        # ==========================================================
        # 6. CREAR PROCEDIMIENTO
        # ==========================================================

        result = db.execute_dml(
            """
            CREATE PROCEDURE dbo.test_sqlserver_client_count
                @valor_minimo INT
            AS
            BEGIN
                SELECT
                    COUNT(*) AS total,
                    @valor_minimo AS valor_minimo
                FROM dbo.test_sqlserver_client
                WHERE valor >= @valor_minimo;
            END
            """
        )

        mostrar_resultado(
            "6. CREACIÓN DEL PROCEDIMIENTO",
            result,
        )

        # ==========================================================
        # 7. EJECUTAR PROCEDIMIENTO
        # ==========================================================

        result = db.execute_procedure(
            "dbo.test_sqlserver_client_count",
            [30],
        )

        mostrar_resultado(
            "7. EJECUCIÓN DEL PROCEDIMIENTO",
            result,
        )

        # ==========================================================
        # 8. LIMPIEZA
        # ==========================================================

        result = db.execute_dml(
            """
            DROP PROCEDURE dbo.test_sqlserver_client_count
            """
        )

        mostrar_resultado(
            "8. ELIMINACIÓN DEL PROCEDIMIENTO",
            result,
        )

        result = db.execute_dml(
            """
            DROP TABLE dbo.test_sqlserver_client
            """
        )

        mostrar_resultado(
            "9. ELIMINACIÓN DE LA TABLA",
            result,
        )

    finally:
        db.close()
        print("\nPool SQL Server cerrado.")


if __name__ == "__main__":
    main()
