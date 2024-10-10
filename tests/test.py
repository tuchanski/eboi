import psycopg2 as db_manager

def read_db_settings_file():
    try:
        with open("app/config/db_settings.txt", "r") as settings:
            info = settings.read().strip().split(",")
            return info
    except FileNotFoundError:
        print("File path not found")
        return None

def get_db_connection():

    DB_PROPERTIES = read_db_settings_file()

    if DB_PROPERTIES is not None:
        conn = db_manager.connect(database=DB_PROPERTIES[0], host=DB_PROPERTIES[1],
                                   user=DB_PROPERTIES[2], password=DB_PROPERTIES[3],
                                     port=DB_PROPERTIES[4])
        return conn
    
    return None

conn = get_db_connection()

print(conn.status)