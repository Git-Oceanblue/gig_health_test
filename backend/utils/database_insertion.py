def schema_creator(table_name):

def create_table_if_not_exists(cursor, table_name, table_schema):
    """
    Create a table only if it does not already exist.
    Returns:
        True  -> if table was created
        None  -> if table already existed
    """

    # Check if table exists
    cursor.execute(f"""
        SELECT 1 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = '{table_name}';
    """)
    
    exists = cursor.fetchone()

    if exists:
        return None  # Table already exists

    else:
        # Collect all unique keys across all rows
        all_columns = set()
        for row in data:
            all_columns.update(row.keys())

        # Check if table exists
        cursor.execute(f"""
            SELECT 1
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = '{table_name}';
        """)

        exists = cursor.fetchone()
        if exists:
            return None

        # Build dynamic schema (all columns as NVARCHAR(MAX))
        column_defs = ", ".join([f"[{col}] NVARCHAR(MAX)" for col in all_columns])

        create_sql = f"""
            CREATE TABLE {table_name} (
                {column_defs}
            );
        """

        cursor.execute(create_sql)
        return True


def insert_data(cursor, table_name, data):
    """
    Insert data into a specified table in the database.

    Parameters:
    cursor (cursor object): The database cursor to execute SQL commands.
    table_name (str): The name of the table to insert data into.
    data (dict): A dictionary where keys are column names and values are the corresponding data to insert.

    Returns:
    None
    """
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
    cursor.execute(insert_query, list(data.values()))


# configuration code

def conn_to_db():
    import pyodbc

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=tcp:sqlserver100101.database.windows.net,1433;"
        "DATABASE=restaurant_db;"
        "UID=azuresql;"
        "PWD=Aazure$01;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    conn = pyodbc.connect(conn_str)

    return conn

def main_insert(conn, data, person_id=None):
    """
    Insert normalized resume data into Azure SQL.

    Args:
        conn: Database connection
        data: Resume dictionary
        person_id: Optional identifier

    Returns:
        person_id
    """
    cursor = conn.cursor()

    try:
        if not person_id:
            person_id = generate_person_id()

        logger.info(f"\n{'=' * 60}")
        logger.info(f"INSERTING RESUME DATA FOR PERSON_ID: {person_id}")
        logger.info(f"{'=' * 60}\n")

        # Ensure tables exist
        create_all_tables(cursor)

        # Insert all sections
        insert_personal_details(cursor, person_id, data)
        insert_employment_records(cursor, person_id, data)
        insert_reference_records(cursor, person_id, data)
        insert_education_records(cursor, person_id, data)
        insert_certification_records(cursor, person_id, data)

        conn.commit()
        logger.info(f"\n✓ All data committed successfully for person_id: {person_id}\n")
        return person_id

    except Exception as e:
        logger.error(f"\n✗ Error in main_insert: {e}")
        conn.rollback()
        logger.info("✗ Transaction rolled back\n")
        raise

    finally:
        cursor.close()

