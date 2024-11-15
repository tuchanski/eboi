import psycopg2

DB_HOST = "localhost"
DB_NAME = "eBoi"
DB_USER  = "postgres"
DB_PASS = "postgres"
DB_PORT = "5432"

def get_connection():
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
