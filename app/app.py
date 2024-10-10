from flask import Flask, render_template
import psycopg2 as db_manager

# Lê o arquivo que contém as informações de configurações do banco
def read_db_settings_file():
    try:
        with open("app/config/db_settings.txt", "r") as settings:
            info = settings.read().strip().split(",")
            return info
    except FileNotFoundError:
        print("File path not found")
        return None

# Estabelece a conexão com o banco de dados
def get_db_connection():
    properties = read_db_settings_file()

    if properties is not None:
        conn = db_manager.connect(database=properties[0], host=properties[1],
                                   user=properties[2], password=properties[3],
                                     port=properties[4])
        return conn
    
    # Retornando None
    return properties

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def getHomeScreen():
    conn = get_db_connection()
    conn.cursor()
    return render_template("home/home.html")

app.run("localhost", 8080, None)