# Instale o driver para comunicação com o Postgresql pip install psycopg2

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
# CRUD DE USUÁRIO ->

# ESSE AQUI POR ENQUANTO TÁ ESTILIZADO COMO UM PROTÓTIPO DO PAINEL DE ADMIN. RECUPERA OS USUÁRIOS E CONTÉM ATALHOS PARA EDITAR E EXCLUIR.
@app.route("/recuperar_usuarios", methods=["GET"])
def recuperar_usuarios():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM usuario")
        usuarios = cursor.fetchall()
        if not usuarios:
            flash("Usuários não encontrados.", "danger")
            return redirect(url_for("index"))
        return render_template("/admin/get_users.html", data=usuarios)
    except Exception as e:
        print(f"Erro ao recuperar usuários: {e}")
    return redirect(url_for("index"))

# RESPONSÁVEL POR REGISTRAR O USUÁRIO NO BANCO (PRIVILÉGIO DE ADMIN)
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

# RESPONSÁVEL POR EDITAR O USUÁRIO NO BANCO (PRIVILÉGIO DE ADMIN)
@app.route("/editar_usuario/<int:id>", methods=["POST", "GET"])
def editar_usuario(id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"Erro ao buscar usuário: {e}", "danger")
        conn.rollback()
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        try:
            cursor.execute("UPDATE usuario SET Nome = %s, Email = %s, Senha = %s WHERE id = %s", (nome, email, senha, id))
            conn.commit()
            flash("Dados do usuário atualizados com sucesso!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            print(f"Erro ao atualizar usuário: {e}")
            conn.rollback()
            flash("Erro ao atualizar usuário.", "danger")
    return render_template("admin/edit_user.html", id=id)

# RESPONSÁVEL POR DELETAR O USUÁRIO NO BANCO (PRIVILÉGIO DE ADMIN)
@app.route("/deletar_usuario/<int:id>", methods=["GET"])
def deletar_usuario(id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("index"))
        cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
        conn.commit()
        flash("Dados deletados", "warning")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Erro ao buscar usuário: {e}", "danger")
        conn.rollback()
        return redirect(url_for("index"))

# -----------------------------------
            
if __name__ == "__main__":
    app.run("localhost", 8080, None)