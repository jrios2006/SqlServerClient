# Ejemplos de salida de ejecución

## `test.py`
```bash
python test.py 
```
```plaintext
Cargando credenciales...

======================================================================
1. INFORMACIÓN DEL SERVIDOR
======================================================================
success   : True
rowcount  : 1
duration  : 0.4007 s
metrics   : {'attempts': 1, 'connection_time': 0.397908, 'query_time': 0.002658}
rows:
  {'fecha_hora_servidor': datetime.datetime(2026, 9, 28, 10, 36, 9, 250000), 'servidor': 'DESKTOP-HJ7J2HO\\SQLEXPRESS', 'base_datos': 'master'}

======================================================================
2. CREACIÓN DE TABLA
======================================================================
success   : True
rowcount  : 0
duration  : 0.0089 s
metrics   : {'attempts': 1, 'connection_time': 3.3e-05, 'query_time': 0.008797}

======================================================================
3. INGESTA DE DATOS
======================================================================
success   : True
rowcount  : 5
duration  : 0.0122 s
metrics   : {'attempts': 1, 'connection_time': 1.6e-05, 'query_time': 0.012174}

======================================================================
4. NÚMERO DE REGISTROS
======================================================================
success   : True
rowcount  : 1
duration  : 0.0018 s
metrics   : {'attempts': 1, 'connection_time': 1.2e-05, 'query_time': 0.001722}

Registros creados: 5

======================================================================
5. CONSULTA PARAMETRIZADA
======================================================================
success   : True
rowcount  : 3
duration  : 0.006 s
metrics   : {'attempts': 1, 'connection_time': 1.5e-05, 'query_time': 0.00594}
rows:
  {'id': 3, 'nombre': 'Pedro', 'valor': 30, 'fecha': datetime.datetime(2026, 9, 28, 10, 36, 9, 273367)}
  {'id': 4, 'nombre': 'Laura', 'valor': 40, 'fecha': datetime.datetime(2026, 9, 28, 10, 36, 9, 273367)}
  {'id': 5, 'nombre': 'Carlos', 'valor': 50, 'fecha': datetime.datetime(2026, 9, 28, 10, 36, 9, 273367)}

======================================================================
6. CREACIÓN DEL PROCEDIMIENTO
======================================================================
success   : True
rowcount  : 0
duration  : 0.0044 s
metrics   : {'attempts': 1, 'connection_time': 1e-05, 'query_time': 0.004327}

======================================================================
7. EJECUCIÓN DEL PROCEDIMIENTO
======================================================================
success   : True
rowcount  : 1
duration  : 0.0049 s
metrics   : {'attempts': 1, 'connection_time': 1.1e-05, 'query_time': 0.004884}
rows:
  {'total': 3, 'valor_minimo': 30}

======================================================================
8. ELIMINACIÓN DEL PROCEDIMIENTO
======================================================================
success   : True
rowcount  : 0
duration  : 0.004 s
metrics   : {'attempts': 1, 'connection_time': 1.8e-05, 'query_time': 0.003884}

======================================================================
9. ELIMINACIÓN DE LA TABLA
======================================================================
success   : True
rowcount  : 0
duration  : 0.0042 s
metrics   : {'attempts': 1, 'connection_time': 2e-05, 'query_time': 0.0041}

Pool SQL Server cerrado.
```

## `test_mensajes.py`
```bash
python test_mensajes.py
```
```plaintext
Cargando credenciales...

======================================================================
1. CREACIÓN DEL PROCEDIMIENTO
======================================================================
Success  : True (Filas: 0)
Duración : 0.0054 s

(No se capturaron mensajes del servidor)

======================================================================
2. EJECUCIÓN DEL PROCEDIMIENTO (Debe mostrar 4 mensajes)
======================================================================
Success  : True (Filas: 1)
Duración : 0.0022 s

Filas devueltas:
  {'estado': 'COMPLETADO', 'valor_resultado': 42}

Mensajes del servidor capturados:
  [Mensaje 1] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]1. Iniciando el procesamiento de datos...
  [Mensaje 2] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]2. Calculando métricas intermedias...
  [Mensaje 3] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]3. Aviso: Se detectaron valores atípicos (Severidad 10).
  [Mensaje 4] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]4. Proceso finalizado correctamente.

======================================================================
3. EJECUCIÓN DML DIRECTA
======================================================================
Success  : True (Filas: 0)
Duración : 0.0014 s

Mensajes del servidor capturados:
  [Mensaje 1] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Mensaje desde una consulta DML directa (sin procedimiento).

======================================================================
4. LIMPIEZA DEL PROCEDIMIENTO
======================================================================
Success  : True (Filas: 0)
Duración : 0.0015 s

(No se capturaron mensajes del servidor)

Pool SQL Server cerrado correctamente.
```

## `test_tipos.py`
```bash
python test_tipos.py 
```
```plaintext
Cargando credenciales...

======================================================================
1. CREACIÓN DE TABLA COMPLEJA
======================================================================
Success  : True (Filas: 0)
Duración : 0.006 s

======================================================================
2. INGESTA DE DATOS
======================================================================
Success  : True (Filas: 3)
Duración : 0.0132 s

======================================================================
3. CONSULTA Y SERIALIZACIÓN A JSON
======================================================================
Success  : True (Filas: 3)
Duración : 0.0018 s

Formato JSON Nativo (con fechas serializadas):
[
  {
    "id": 1,
    "nombre": "Administrador",
    "fecha_nacimiento": "1985-10-25",
    "fecha_registro": "2026-09-28T10:42:09.264638",
    "saldo": 2500.5,
    "datos_json": "{\"rol\": \"admin\", \"permisos\": [\"lectura\", \"escritura\", \"borrado\"]}"
  },
  {
    "id": 2,
    "nombre": "Usuario B\u00e1sico",
    "fecha_nacimiento": null,
    "fecha_registro": "2026-09-28T10:42:09.264638",
    "saldo": null,
    "datos_json": "{\"rol\": \"user\", \"permisos\": [\"lectura\"]}"
  },
  {
    "id": 3,
    "nombre": "Invitado",
    "fecha_nacimiento": "2000-01-01",
    "fecha_registro": "2026-09-28T10:42:09.264638",
    "saldo": 0.0,
    "datos_json": null
  }
]

======================================================================
4. CREACIÓN DE PROCEDIMIENTO CON PARSEO JSON EN SQL
======================================================================
Success  : True (Filas: 0)
Duración : 0.0026 s

======================================================================
5. EJECUCIÓN DEL PROCEDIMIENTO (Busca Rol 'admin')
======================================================================
Success  : True (Filas: 1)
Duración : 0.0079 s

Formato JSON Nativo (con fechas serializadas):
[
  {
    "id": 1,
    "nombre": "Administrador",
    "saldo": 2500.5
  }
]

======================================================================
6. ELIMINACIÓN DEL PROCEDIMIENTO
======================================================================
Success  : True (Filas: 0)
Duración : 0.0035 s

======================================================================
7. ELIMINACIÓN DE LA TABLA
======================================================================
Success  : True (Filas: 0)
Duración : 0.0047 s

Pool SQL Server cerrado correctamente.
```

## `test_cursores.py`
```bash
python test_cursores.py 
```
```plaintext
Total de cursores capturados: 3

--- Cursor 1 ---
{'id': 1, 'departamento': 'Ventas'}

--- Cursor 2 ---
{'ciudad': 'Madrid', 'total': 2500}

--- Cursor 3 ---
{'estado': 'Sin mensajes previos'}

Mensajes capturados:
 - [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Generando primer reporte...
 - [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Generando segundo reporte...
```

## `Fallo en Credenciales`
```bash
time python test_cursores.py 
```
```plaintext
SQL Server error: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Error de inicio de sesión del usuario 'sa'. (18456) (SQLDriverConnect)")
SQL Server error: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Error de inicio de sesión del usuario 'sa'. (18456) (SQLDriverConnect)")
Total de cursores capturados: 0

Mensajes capturados:
SQL Server error: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Error de inicio de sesión del usuario 'sa'. (18456) (SQLDriverConnect)")

real    0m1,093s
user    0m0,151s
sys     0m0,053s

## Otra ejecución con usuario no válido

SQL Server error: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Error de inicio de sesión del usuario 'sa1'. (18456) (SQLDriverConnect)")
SQL Server error: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Error de inicio de sesión del usuario 'sa1'. (18456) (SQLDriverConnect)")
Total de cursores capturados: 0

Mensajes capturados:
SQL Server error: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Error de inicio de sesión del usuario 'sa1'. (18456) (SQLDriverConnect)")

real    0m0,295s
user    0m0,147s
sys     0m0,072s

## Otra ejecución con base de datos no válida

SQL Server error: ('42000', "[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]No se puede abrir la base de datos 'master1' solicitada por el inicio de sesión. Error de inicio de sesión. (4060) (SQLDriverConnect)")
SQL Server error: ('42000', "[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]No se puede abrir la base de datos 'master1' solicitada por el inicio de sesión. Error de inicio de sesión. (4060) (SQLDriverConnect)")
Total de cursores capturados: 0

Mensajes capturados:
SQL Server error: ('42000', "[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]No se puede abrir la base de datos 'master1' solicitada por el inicio de sesión. Error de inicio de sesión. (4060) (SQLDriverConnect)")

real    0m1,054s
user    0m0,166s
sys     0m0,044s

## Otra ejecución con Ip inexistente o error en la comunicación

SQL Server error: ('HYT00', '[HYT00] [Microsoft][ODBC Driver 18 for SQL Server]Login timeout expired (0) (SQLDriverConnect)')
SQL Server error: ('HYT00', '[HYT00] [Microsoft][ODBC Driver 18 for SQL Server]Login timeout expired (0) (SQLDriverConnect)')
Total de cursores capturados: 0

Mensajes capturados:
SQL Server error: ('HYT00', '[HYT00] [Microsoft][ODBC Driver 18 for SQL Server]Login timeout expired (0) (SQLDriverConnect)')

real    1m34,402s
user    0m0,128s
sys     0m0,068s

## Otra ejecución con driver odbc cambiado

SQL Server error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server' : file not found (0) (SQLDriverConnect)")
SQL Server error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server' : file not found (0) (SQLDriverConnect)")
Total de cursores capturados: 0

Mensajes capturados:
SQL Server error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server' : file not found (0) (SQLDriverConnect)")

real    0m0,203s
user    0m0,140s
sys     0m0,058s

```


