from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from config import db
import psycopg2
import psycopg2.extras

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

conn = db.get_connection()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        email = request.form["email"]
        senha = request.form["password"]
        try:
            cursor.execute("SELECT * FROM usuario WHERE Email = %s AND Senha = %s", (email, senha))
            usuario = cursor.fetchone()
            if not usuario:
                flash("Informações incorretas.", "danger")
                return redirect(url_for("auth.login"))
            
            session["usuario_id"] = usuario["id"]
            session["usuario_email"] = usuario["email"]
            session["usuario_tipo"] = usuario["tipo"]

            flash("Login bem-sucedido!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erro ao buscar usuário: {e}", "danger")
            return redirect(url_for("auth.login"))
        finally:
            cursor.close()
    return render_template("auth/login.html")

# ROTA PARA LOGOUT
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))