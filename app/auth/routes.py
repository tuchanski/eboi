from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash
from models import Usuario
from config.db import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["password"]
        try:
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario or usuario.senha != senha:
                flash("Informações incorretas.", "danger")
                return redirect(url_for("auth.login"))
            session["usuario_id"] = usuario.id
            session["usuario_email"] = usuario.email
            session["usuario_tipo"] = usuario.tipo

            flash("Login bem-sucedido!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erro ao buscar usuário: {e}", "danger")
            return redirect(url_for("auth.login"))
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))
