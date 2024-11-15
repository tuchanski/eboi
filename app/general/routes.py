from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
from models import Usuario  # Modelo do SQLAlchemy
from extensions import db

general_bp = Blueprint('general', __name__, url_prefix='/eboi')

def login_required(f):
    @wraps(f)
    def wrap2(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Você precisa estar logado para acessar esta página.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrap2

# ROTA DA PÁGINA COTAR
@general_bp.route("/cotar")
@login_required
def cotar():
    usuario_tipo = session.get('usuario_tipo')
    return render_template("others/cotar.html", usuario_tipo=usuario_tipo)

# ROTA DA PÁGINA SOBRE NOS
@general_bp.route("/sobre-nos")
@login_required
def sobre_nos():
    usuario_tipo = session.get('usuario_tipo')
    return render_template("others/sobre-nos.html", usuario_tipo=usuario_tipo)

# ROTA DA PÁGINA FAQ
@general_bp.route("/faq")
@login_required
def faq():
    usuario_tipo = session.get('usuario_tipo')
    return render_template("others/faq.html", usuario_tipo=usuario_tipo)

# TELA DO PERFIL DO USUÁRIO
@general_bp.route("/perfil")
@login_required
def perfil():
    try:
        id = session["usuario_id"]
        
        usuario = Usuario.query.get(id)
        
        if usuario:
            return render_template("profile/perfil.html", usuario=usuario)
        else:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"Erro ao recuperar usuário: {e}", "danger")
        return redirect(url_for("index"))
