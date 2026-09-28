# SqlServerClient

Cliente Microsoft SQL Server para Python basado en `pyodbc`. Esta librería proporciona una API robusta y fácil de usar para interactuar con bases de datos SQL Server, implementando de forma nativa un pool de conexiones, sistema de reintentos y recolección de métricas de ejecución.

## Características

- Pool de conexiones integrado (reutilización de conexiones para mayor rendimiento).
- Sistema de reintentos automático ante fallos transitorios.
- Métricas de ejecución (tiempo de conexión, tiempo de consulta, intentos).
- Operaciones `SELECT` estándar y en modo *streaming* (por bloques).
- Ejecución de consultas DML (INSERT, UPDATE, DELETE).
- Inserciones masivas (`bulk insert`) optimizadas usando `fast_executemany`.
- Ejecución de procedimientos almacenados y funciones escalares.
- Soporte para *Context Manager* (`with ... as db:`).
- Retorno de resultados en formato de diccionario por defecto.

## Requisitos Previos (Dependencias del Sistema)

Para que `pyodbc` pueda comunicarse con SQL Server, **es obligatorio** tener instalado el gestor de ODBC y el driver de Microsoft (`ODBC Driver 18 for SQL Server`) a nivel de sistema operativo. No basta con instalar dependencias de Python.

### Windows
1. Descarga el instalador oficial desde la página de Microsoft: [Download ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).
2. Ejecuta el archivo `.msi` y sigue el asistente de instalación.

### Linux (Arch Linux / Manjaro / RebornOS)
Debes instalar el gestor `unixodbc` desde los repositorios oficiales y el driver de Microsoft desde el repositorio de usuarios (AUR):
```bash
# 1. Instalar el gestor ODBC
sudo pacman -S unixodbc

# 2. Instalar el driver de Microsoft (usando un helper como yay o paru)
yay -S msodbcsql18
```

### Linux (Ubuntu / Debian)
Añade la clave GPG y el repositorio de Microsoft, luego instala los paquetes:
```bash
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
curl -fsSL https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

## Instalación (Dependencias de Python)

Una vez que el sistema operativo tiene los drivers necesarios, instala la librería de Python en tu entorno virtual:

```bash
pip install pyodbc
```
*(O añade `pyodbc` a tu archivo `requirements.txt` y ejecuta `pip install -r requirements.txt`)*

## Configuración

El cliente espera un diccionario de configuración con los siguientes parámetros:

```python
cfg = {
    "servidor": "IP_O_NOMBRE_SERVIDOR",
    "puerto": 1433,
    "database": "nombre_bd",
    "usuario": "tu_usuario",
    "password": "tu_password",
    # Opcionales:
    "driver": "ODBC Driver 18 for SQL Server", # Por defecto
    "trust_server_certificate": True,          # Útil para entornos de desarrollo/Express
    "encrypt": "yes"                           # Por defecto en Driver 18
}
```

## Ejemplos de Uso

### Inicialización y Context Manager

Es altamente recomendable usar el cliente con un bloque `with` para asegurar que el pool de conexiones se cierre y libere correctamente al terminar.

```python
from sqlserver_client import SqlServerClient

cfg = { ... } # Tu diccionario de configuración

with SqlServerClient(cfg) as db:
    # Tu código aquí
    pass
# Al salir del bloque, db.close() se ejecuta automáticamente
```

### 1. Ejecutar una consulta SELECT

```python
result = db.execute_query(
    """
    SELECT id, nombre, valor 
    FROM dbo.usuarios 
    WHERE valor >= ?
    """, 
    params=[30]
)

if result["success"]:
    for row in result["rows"]:
        print(row["nombre"])
```

### 2. Inserción Masiva (Bulk Insert)

Ideal para ingestar grandes volúmenes de datos de forma rápida.

```python
datos = [
    ("Juan", 10),
    ("Ana", 20),
    ("Pedro", 30)
]

result = db.bulk_insert(
    "INSERT INTO dbo.usuarios (nombre, valor) VALUES (?, ?)",
    datos
)
print(f"Filas insertadas: {result['rowcount']}")
```

### 3. Ejecutar un Procedimiento Almacenado

```python
result = db.execute_procedure(
    "dbo.mi_procedimiento",
    params=[1, "parámetro_texto"]
)
```

## Troubleshooting (Solución de problemas comunes)

**Error: `Can't open lib 'ODBC Driver 18 for SQL Server' : file not found`**
- **Causa:** El sistema operativo no tiene instalado el driver especificado.
- **Solución:** Revisa la sección "Requisitos Previos" e instala `msodbcsql18` (y `unixodbc` en Linux).

**Error: `Login timeout expired` al conectar a SQL Server Express**
- **Causa:** Por defecto, SQL Server Express desactiva las conexiones de red por TCP/IP y utiliza puertos dinámicos.
- **Solución:** 
  1. Abre el "SQL Server Configuration Manager" en el servidor.
  2. Ve a "SQL Server Network Configuration" -> "Protocols for SQLEXPRESS".
  3. Habilita "TCP/IP".
  4. En las propiedades de TCP/IP (pestaña IP Addresses), ve a "IPAll", borra el valor de "TCP Dynamic Ports" y pon `1433` en "TCP Port".
  5. Reinicia el servicio de SQL Server.

### 4. Serialización a JSON (Fechas y Decimales)
La librería incluye un método para exportar los resultados a JSON nativo, gestionando automáticamente la conversión de objetos `datetime`, `date` (a formato ISO 8601) y `Decimal` (a numéricos de JSON).

```python
result = db.execute_query("SELECT id, fecha, saldo FROM cobros")
json_string = db.result_to_json(result["rows"])
print(json_string)
```

### 5. Captura de Mensajes (PRINT / RAISERROR)
Cualquier mensaje informativo generado por el motor de SQL Server (`PRINT` o avisos `RAISERROR` de severidad baja) se recolecta automáticamente y se expone en la clave "messages".

```python
result = db.execute_procedure("dbo.sp_procesar_datos")
for msg in result["messages"]:
    print(f"Log del motor: {msg}")
```

### 6. Múltiples Cursores (ResultSets)

Si un procedimiento almacenado devuelve múltiples consultas SELECT simultáneas, el cliente navega por todas ellas y las almacena secuencialmente en la clave "`resultsets`". Por retrocompatibilidad, la clave "`rows`" siempre contendrá los datos del primer cursor.

```python
result = db.execute_procedure("dbo.sp_multiples_reportes")
for i, cursor in enumerate(result["resultsets"]):
    print(f"Cursor {i} devolvió {cursor['rowcount']} filas.")
```

---

### Documentación de los Programas de Prueba (Test Suite)

Esta batería de pruebas sirve como ejemplos funcionales y garantiza que todas las capacidades de la librería operan correctamente. 

*   **`test.py` (Operaciones Base y CRUD):** Es el flujo de trabajo principal. Comprueba que la conexión funciona (extrayendo la fecha y nombre del servidor), ejecuta sentencias DDL para crear tablas, prueba la inserción masiva (`bulk_insert`), verifica la ejecución de funciones escalares (`COUNT(*)`) y parámetros en consultas `SELECT`, además de probar la creación y ejecución de un procedimiento almacenado estándar. Finaliza limpiando la base de datos.
*   **`test_tipos.py` (Tipos Complejos y Exportación JSON):** Valida la robustez del mapeo de datos. Crea una tabla con tipos `DATE`, `DATETIME2`, `DECIMAL` y una columna validada para contenido `JSON` interno. Inserta valores normales y nulos (`NULL`). Luego, prueba la función de utilidad `result_to_json` para asegurar que el diccionario de Python se transforma limpiamente en un string JSON serializable, y comprueba la interoperabilidad con la función `JSON_VALUE` nativa de SQL Server.
*   **`test_mensajes.py` (Captura de Logs del Motor):** Garantiza que la librería puede extraer la salida secundaria del servidor sin romperse. Crea un procedimiento almacenado que intercala comandos `PRINT` y un `RAISERROR` de nivel informativo (severidad 10) con una salida `SELECT`. También prueba la recolección de mensajes a través de una sentencia DML directa.
*   **`test_cursores.py` (Navegación de Múltiples ResultSets):** Comprueba la capacidad avanzada del cliente para iterar sobre varios bloques de datos. Ejecuta un procedimiento almacenado que devuelve tres consultas `SELECT` distintas separadas por comandos `PRINT`. Valida que todos los cursores se capturen de forma ordenada dentro de la lista `resultsets` y que los mensajes no interrumpan el flujo de lectura.
