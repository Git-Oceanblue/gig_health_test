from asyncio.log import logger
import pyodbc

# configuration code

def conn_to_db():

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

# Function for the table existance check

def table_existance(table_name,cursor):
    cursor.execute(f"""
        SELECT 1 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = '{table_name}';
    """)
    exists = cursor.fetchone()

    if exists:
        return True
    else:
        return None

# Schema creadtion using the exisintg data

def create_schema(data):
    all_columns = set(data.keys())

    #returning the table schema
    return {
        "column_defs": ", ".join([f"[{col}] NVARCHAR(MAX)" for col in all_columns]),
        "columns": ", ".join([f"[{col}]" for col in all_columns])
    }

# creating the table

def create_table(cursor, table_name, column_defs):

        create_sql = f"""
            CREATE TABLE {table_name} (
                {column_defs}
            );
        """
        if cursor.execute(create_sql):
            return True
        else:
            return False

# data insertion script

def insert_data(cursor, table_name, data, columns):

    placeholders = ', '.join(['%s'] * len(data))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
    cursor.execute(insert_query, list(data.values()))


# get the columns names

def get_columns(cursor, table_name):
    cursor.execute(f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}';
    """)
    columns = cursor.fetchall()
    return [col[0] for col in columns]

# main function which makes the connection to the DB in aws and

def main_insert(data,table_name):

    conn = conn_to_db()
    cursor = conn.cursor()

    try:
        if table_existance(cursor,table_name):
            logger.info(f"\n✓ Table '{table_name}' exists.\n")
            existing_columns = get_columns(cursor, table_name)
            insert_data(cursor, table_name, data, ", ".join(existing_columns))
            logger.info(f"✓ Data inserted into existing table '{table_name}'.\n")
            conn.commit()
        else:
            logger.info(f"\n✗ Table '{table_name}' does not exist. Creating table...\n")
            schema = create_schema(data)
            create_table(cursor, table_name, schema["column_defs"])
            logger.info(f"✓ Table '{table_name}' created successfully.\n")
            insert_data(cursor, table_name, data, schema["columns"])
            logger.info(f"✓ Data inserted into new table '{table_name}'.\n")
            conn.commit()

    except Exception as e:
        logger.error(f"\n✗ Error in main_insert: {e}")
        conn.rollback()
        logger.info("✗ Transaction rolled back\n")
        raise

    finally:
        # Clean up resources
        if cursor:
            cursor.close()
            logger.info("✓ Cursor closed")
        if conn:
            conn.close()
            logger.info("✓ Connection closed")
