from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
from models import Usuario
from models import HistoricoWarning
from models import HistoricoLocalizacao

general_bp = Blueprint('general', __name__, url_prefix='/eboi')

def login_required(f):
    @wraps(f)
    def wrap2(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Você precisa estar logado para acessar esta página.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrap2

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
