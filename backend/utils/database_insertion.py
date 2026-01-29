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

    # Create table
    create_table_query = f"""
    CREATE TABLE {table_name} (
        {table_schema}
    );
    """
    cursor.execute(create_table_query)
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