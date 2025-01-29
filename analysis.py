import pyodbc
import json
import csv
from datetime import datetime

# Configuración de conexión a SQL Server
CONN_STRING = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1434;DATABASE=pubs;UID=sa;PWD=root*2025"

def execute_query(query):
    """Ejecuta una consulta en SQL Server y devuelve los resultados."""
    conn = pyodbc.connect(CONN_STRING)
    cursor = conn.cursor()
    cursor.execute(query)
    # Obtener nombres de columnas
    columns = [columna[0] for columna in cursor.description]  

    # Convertir resultado a lista de diccionarios
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return results

def log_results(check_type, results):
    """Guarda los resultados en un archivo JSON y CSV."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Guardar en JSON
    with open(f"{check_type}_{timestamp}.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4, default=str)

    # Guardar en CSV
    with open(f"{check_type}_{timestamp}.csv", "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        if results:
            writer.writerow(results[0].keys())  # Encabezados
            for row in results:
                writer.writerow(row.values())

    print(f"[INFO] Resultados guardados en {check_type}_{timestamp}.json y {check_type}_{timestamp}.csv")

def detect_orphan_records():
    """Detecta registros huérfanos en la base de datos."""
    query = """
    SELECT 
        fk.name AS ForeignKeyName,
        OBJECT_NAME(fk.parent_object_id) AS ChildTable,
        c1.name AS ChildColumn,
        OBJECT_NAME(fk.referenced_object_id) AS ParentTable,
        c2.name AS ParentColumn
    FROM sys.foreign_keys fk
    INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
    INNER JOIN sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
    INNER JOIN sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id;
    """

    foreign_keys = execute_query(query)
    orphan_records = []

    for fk in foreign_keys:
        child_table = fk["ChildTable"]
        child_column = fk["ChildColumn"]
        parent_table = fk["ParentTable"]
        parent_column = fk["ParentColumn"]

        orphan_query = f"""
        SELECT '{child_table}' AS TableName, {child_column} AS OrphanValue
        FROM {child_table}
        WHERE {child_column} NOT IN (SELECT {parent_column} FROM {parent_table});
        """

        orphan_data = execute_query(orphan_query)
        orphan_records.extend(orphan_data)

    log_results("FKs_no_asociadas_a_PK", orphan_records)

def detect_duplicate_keys():
    """Detecta claves duplicadas en índices únicos."""
    query = """
    SELECT 
        t.name AS TableName, 
        c.name AS ColumnName
    FROM sys.indexes i
    INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    INNER JOIN sys.tables t ON i.object_id = t.object_id
    WHERE i.is_unique = 1;
    """

    unique_keys = execute_query(query)
    duplicate_keys = []

    for key in unique_keys:
        table_name = key["TableName"]
        column_name = key["ColumnName"]

        dup_query = f"""
        SELECT '{table_name}' AS TableName, '{column_name}' AS ColumnName, {column_name} AS DuplicateValue, COUNT(*) AS DuplicateCount
        FROM {table_name}
        GROUP BY {column_name}
        HAVING COUNT(*) > 1;
        """

        duplicates = execute_query(dup_query)
        duplicate_keys.extend(duplicates)

    log_results("PK_duplicadas", duplicate_keys)

def detect_missing_foreign_keys():
    """Detecta relaciones que deberían tener claves foráneas pero no están implementadas."""
    query = """
    SELECT t.name AS TableName, c.name AS ColumnName
    FROM sys.tables t
    INNER JOIN sys.columns c ON t.object_id = c.object_id
    WHERE c.name LIKE '%Id%' 
    AND NOT EXISTS (
        SELECT 1 FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        WHERE fkc.parent_object_id = t.object_id AND fkc.parent_column_id = c.column_id
    );
    """

    missing_fks = execute_query(query)
    log_results("tablas_sin_FK", missing_fks)

def detect_foreign_keys_not_in_primary_key():
    """Detecta claves foráneas que no forman parte de una clave primaria."""
    query = """
    SELECT 
        fk.name AS ForeignKeyName,
        OBJECT_NAME(fk.parent_object_id) AS TableName,
        c1.name AS ForeignKeyColumn
    FROM sys.foreign_keys fk
    INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
    INNER JOIN sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
    WHERE NOT EXISTS (
        SELECT 1 FROM sys.key_constraints pk
        INNER JOIN sys.index_columns ic ON pk.parent_object_id = ic.object_id AND pk.unique_index_id = ic.index_id
        WHERE pk.type = 'PK' AND pk.parent_object_id = fk.parent_object_id AND ic.column_id = fkc.parent_column_id
    );
    """

    fks_not_in_pk = execute_query(query)
    log_results("FK_no_son_parte_de_PK", fks_not_in_pk)

def main():
    print("[INFO] Iniciando auditoría de base de datos en SQL Server...")
    detect_orphan_records()
    detect_duplicate_keys()
    detect_missing_foreign_keys()
    detect_foreign_keys_not_in_primary_key()
    print("[INFO] Auditoría completada.")

if __name__ == "__main__":
    main()
