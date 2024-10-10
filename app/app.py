from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# INFORMAÇÕES DE CONEXÃO COM BANCO Postgresql
DB_HOST = "localhost"
DB_NAME = "eBoi"
DB_USER  = "postgres"
DB_PASS = "root"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    return render_template("home/home.html")

# -----------------------------------
# OPERAÇÕES DE USUÁRIO ->

# RESPONSÁVEL POR REGISTRAR O USUÁRIO NO BANCO
@app.route("/registrar_usuario", methods=["POST", "GET"])
def registrar_usuario():
    if request.method == "POST":
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        try:
            cursor.execute("INSERT INTO usuario (Nome, Email, Senha) VALUES (%s,%s,%s)", (nome, email, senha))
            conn.commit()
            flash("Usuário adicionado com sucesso!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            print(f"Erro ao registrar usuário: {e}")
            conn.rollback()
            flash("Erro ao registrar usuário.", "danger")
    return render_template("auth/register.html")

# -----------------------------------
            
if __name__ == "__main__":
    app.run("localhost", 8080, None)