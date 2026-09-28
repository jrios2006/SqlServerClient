"""
sqlserver_client.py
===================

Cliente Microsoft SQL Server para Python basado en ``pyodbc``.

Proporciona una API similar a PostgresClient:
- Pool de conexiones (inicialización perezosa)
- Reintentos
- Métricas de ejecución
- SELECT normal y streaming
- DML y Bulk insert
- Ejecución de procedimientos y funciones escalares
- Soporte nativo para múltiples cursores (ResultSets)
- Soporte para exportación a JSON (fechas y decimales)
- Captura de mensajes del motor (PRINT, RAISERROR)

Información de auditoría:
    Todas las operaciones devuelven metadatos de versión de la librería:
        - library_version
        - build_date
"""

import json
import logging
import queue
import time
from datetime import datetime, date
from decimal import Decimal
from threading import Lock

import pyodbc

__version__ = "1.3.0"
__build_date__ = "2026-09-26"


def conversor_json(obj):
    """Convierte fechas a ISO 8601 y decimales a float para serialización JSON."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo {type(obj)} no serializable")


class SqlServerClient:
    """
    Cliente Microsoft SQL Server con pool de conexiones,
    reintentos y métricas.
    """

    def __init__(
        self,
        cfg: dict,
        pool_size=5,
        retry=1,
        autocommit=True,
        dictionary=True,
    ):
        self.cfg = cfg
        self.retry = retry
        self.autocommit = autocommit
        self.dictionary = dictionary
        self.pool_size = pool_size

        self.logger = logging.getLogger("SqlServerClient")

        driver = cfg.get("driver", "ODBC Driver 18 for SQL Server")
        server = cfg["servidor"]
        port = cfg.get("puerto", 1433)
        database = cfg["database"]
        usuario = cfg["usuario"]
        password = cfg["password"]

        trust_server_certificate = cfg.get("trust_server_certificate", True)
        encrypt = cfg.get("encrypt", "yes")

        self.connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={usuario};"
            f"PWD={password};"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={'yes' if trust_server_certificate else 'no'};"
        )

        self._pool = queue.Queue(maxsize=pool_size)
        self._created_connections = 0
        self._pool_lock = Lock()
        self._closed = False

    # -----------------------------
    # CONNECTION POOL
    # -----------------------------

    def _create_connection(self):
        return pyodbc.connect(self.connection_string, autocommit=self.autocommit)

    def _get_connection(self):
        if self._closed:
            raise RuntimeError("SqlServerClient está cerrado")

        try:
            return self._pool.get_nowait()
        except queue.Empty:
            with self._pool_lock:
                if self._created_connections < self.pool_size:
                    conn = self._create_connection()
                    self._created_connections += 1
                    return conn
            return self._pool.get()

    def _put_connection(self, conn):
        if self._closed:
            try:
                conn.close()
            except Exception:
                pass
            return
        self._pool.put(conn)

    # -----------------------------
    # RESULT BASE Y FORMATO
    # -----------------------------

    def _result_base(self):
        return {
            "library_version": __version__,
            "build_date": __build_date__,
            "success": False,
            "rows": [],
            "rowcount": 0,
            "resultsets": [],
            "messages": [],
            "duration": 0.0,
            "error": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "attempts": 0,
                "connection_time": 0.0,
                "query_time": 0.0,
            },
        }

    def result_to_json(self, result_dict, indent=2):
        return json.dumps(result_dict, default=conversor_json, indent=indent)

    def _extract_messages(self, cursor):
        raw_msgs = getattr(cursor, "messages", None)
        if not raw_msgs:
            return []
        
        cleaned = []
        for msg in raw_msgs:
            if isinstance(msg, tuple) and len(msg) > 1:
                cleaned.append(msg[1])
            else:
                cleaned.append(str(msg))
        return cleaned

    # -----------------------------
    # CORE EXECUTION
    # -----------------------------

    def _execute(self, func):
        result = self._result_base()
        start_total = time.time()
        attempts = 0

        while attempts <= self.retry:
            attempts += 1
            conn = None

            try:
                conn_start = time.time()
                conn = self._get_connection()
                conn_time = time.time() - conn_start

                query_start = time.time()
                value = func(conn)
                query_time = time.time() - query_start

                if isinstance(value, dict):
                    result.update(value)

                result["metrics"]["connection_time"] += round(conn_time, 6)
                result["metrics"]["query_time"] += round(query_time, 6)
                result["metrics"]["attempts"] = attempts
                result["success"] = True
                break

            except Exception as e:
                result["error"] = str(e)
                result["metrics"]["attempts"] = attempts
                if attempts > self.retry:
                    self.logger.error(f"SQL Server error: {e}")

            finally:
                if conn is not None:
                    self._put_connection(conn)

        result["duration"] = round(time.time() - start_total, 4)
        return result

    # -----------------------------
    # CURSOR / ROW CONVERSION
    # -----------------------------

    def _rows_as_dicts(self, cursor, rows):
        if not self.dictionary:
            return rows
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    # -----------------------------
    # SELECT
    # -----------------------------

    def execute_query(self, query, params=None, stream=False, fetch_size=1000):
        def run(conn):
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or [])
                all_resultsets = []
                messages = self._extract_messages(cursor)

                while True:
                    if cursor.description is not None:
                        if stream:
                            rows = []
                            while True:
                                chunk = cursor.fetchmany(fetch_size)
                                if not chunk:
                                    break
                                rows.extend(self._rows_as_dicts(cursor, chunk))
                            all_resultsets.append({"rows": rows, "rowcount": len(rows)})
                        else:
                            fetched = cursor.fetchall()
                            rows = self._rows_as_dicts(cursor, fetched)
                            all_resultsets.append({"rows": rows, "rowcount": len(rows)})

                    if not cursor.nextset():
                        break
                    
                    messages.extend(self._extract_messages(cursor))

                mensajes_unicos = list(dict.fromkeys(messages))
                primer_rs = all_resultsets[0] if all_resultsets else {"rows": [], "rowcount": 0}

                return {
                    "rows": primer_rs["rows"],
                    "rowcount": primer_rs["rowcount"],
                    "resultsets": all_resultsets,
                    "messages": mensajes_unicos
                }
            finally:
                cursor.close()

        return self._execute(run)

    # -----------------------------
    # DML
    # -----------------------------

    def execute_dml(self, query, params=None):
        def run(conn):
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or [])
                messages = self._extract_messages(cursor)
                
                while cursor.nextset():
                    messages.extend(self._extract_messages(cursor))

                if not self.autocommit:
                    conn.commit()

                mensajes_unicos = list(dict.fromkeys(messages))
                return {
                    "rowcount": (cursor.rowcount if cursor.rowcount >= 0 else 0),
                    "messages": mensajes_unicos
                }
            finally:
                cursor.close()

        return self._execute(run)

    # -----------------------------
    # BULK INSERT
    # -----------------------------

    def bulk_insert(self, query, data, batch_size=None):
        def run(conn):
            cursor = conn.cursor()
            try:
                cursor.fast_executemany = True
                total = 0

                if batch_size:
                    for i in range(0, len(data), batch_size):
                        batch = data[i:i + batch_size]
                        cursor.executemany(query, batch)
                        total += len(batch)
                else:
                    cursor.executemany(query, data)
                    total = len(data)

                if not self.autocommit:
                    conn.commit()

                return {
                    "rowcount": total,
                    "messages": self._extract_messages(cursor)
                }
            finally:
                cursor.close()

        return self._execute(run)

    # -----------------------------
    # PROCEDURE & SCALAR
    # -----------------------------

    def execute_procedure(self, procedure_name, params=None):
        placeholders = ",".join(["?"] * len(params or []))
        query = f"EXEC {procedure_name} {placeholders}" if placeholders else f"EXEC {procedure_name}"
        return self.execute_query(query, params or [])

    def execute_scalar(self, query, params=None):
        def run(conn):
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or [])
                messages = self._extract_messages(cursor)

                while cursor.description is None:
                    if not cursor.nextset():
                        break
                    messages.extend(self._extract_messages(cursor))

                value = None
                rc = 0

                if cursor.description:
                    row = cursor.fetchone()
                    value = row[0] if row is not None else None
                    rc = 1 if row else 0

                    while cursor.nextset():
                        messages.extend(self._extract_messages(cursor))

                mensajes_unicos = list(dict.fromkeys(messages))
                return {
                    "value": value, 
                    "rowcount": rc,
                    "messages": mensajes_unicos
                }
            finally:
                cursor.close()

        return self._execute(run)

    # -----------------------------
    # CONTEXT MANAGER & CLOSE
    # -----------------------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._closed:
            return
        self._closed = True
        while True:
            try:
                conn = self._pool.get_nowait()
            except queue.Empty:
                break
            try:
                conn.close()
            except Exception:
                pass
        self._created_connections = 0