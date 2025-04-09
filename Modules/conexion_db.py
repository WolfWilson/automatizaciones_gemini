import pyodbc

def get_connection(server="SQL01", database="Gestion"):
    """
    Intenta conectarse a SQL Server, probando varios drivers.
    Usa Trusted_Connection=yes para Windows Authentication.
    """
    drivers = [
        '{SQL Server Native Client 11.0}',
        '{SQL Server Native Client 10.0}',
        '{SQL Server Native Client 2008}',
        '{SQL Server}',
        '{ODBC Driver 17 for SQL Server}',
        '{ODBC Driver 13 for SQL Server}',
        '{ODBC Driver 11 for SQL Server}'
    ]

    for driver in drivers:
        try:
            print(f"🔄 Probando conexión con {driver} en {server}\\{database}...")
            conn = pyodbc.connect(
                f'DRIVER={driver};'
                f'SERVER={server};'
                f'DATABASE={database};'
                'Trusted_Connection=yes;'
            )
            print(f"✅ Conexión exitosa a {server}\\{database} con {driver}.")
            return conn
        except pyodbc.Error as e:
            print(f"❌ Error con {driver} en {server}\\{database}: {e}")

    raise Exception(f"⚠ No se pudo conectar a la base de datos {database} en {server} con ningún driver.")


def ejecutar_procedimiento(server, database, query, parametros=()):
    """
    Ejecuta un procedimiento almacenado y devuelve resultados como lista de dicts.
    Maneja errores y devuelve {"error": "..."} en caso de fallo.
    """
    conn = None
    cursor = None
    import pyodbc

    try:
        conn = get_connection(server, database)
        cursor = conn.cursor()

        cursor.execute(query, parametros)

        if cursor.description:
            columnas = [col[0] for col in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, row)) for row in filas] if filas else []
        else:
            return []

    except pyodbc.ProgrammingError as e:
        return {"error": f"Error SP/sintaxis: {e}"}
    except pyodbc.OperationalError as e:
        return {"error": f"Error operacional o de conexión: {e}"}
    except pyodbc.Error as e:
        return {"error": f"Error ODBC genérico: {e}"}
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def buscar_por_dni(dni):
    # Ajusta el nombre real del SP y sus parámetros
    query = "EXEC Gestion.dbo.will_aura_datos @Nro_doc = ?"
    resultado = ejecutar_procedimiento("SQL01", "Gestion", query, (dni,))
    
    if isinstance(resultado, dict) and "error" in resultado:
        print(f"⚠ Error interno al buscar DNI {dni}: {resultado['error']}")
        return []

    return resultado  # lista de dicts si hay filas, o lista vacía
