from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import psycopg2
import psycopg2.extras
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from models import Usuario, SensorPosicao, SensorDistancia, SensorTemperatura, LED, Buzzer, ESPGps, ESPPortao
from config import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "usuario_id" not in session or session.get("usuario_tipo") != "admin":
            flash("Acesso restrito aos administradores.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrap

@admin_bp.route("/")
@admin_required
def admin():
    return render_template("admin/admin.html")

# GERENCIA SENSORES DO BANCO
@admin_bp.route("/gerencia_sensor", methods=["POST", "GET"])
@admin_required
def gerencia_sensores():
    try:
        sensores = (
            db.session.query(
                SensorPosicao.id.label("id"),
                SensorPosicao.esp_gps_id.label("esp_id"),
                db.literal("Sensor_Posicao").label("tipo")
            )
            .union_all(
                db.session.query(
                    SensorDistancia.id,
                    SensorDistancia.esp_portao_id.label("esp_id"),
                    db.literal("Sensor_Distancia").label("tipo")
                )
            )
            .union_all(
                db.session.query(
                    SensorTemperatura.id,
                    SensorTemperatura.esp_portao_id.label("esp_id"),
                    db.literal("Sensor_Temperatura").label("tipo")
                )
            )
            .all()
        )
        
        if not sensores:
            flash("Sensores não encontrados.", "danger")
            return redirect(url_for("index"))
        
        return render_template("/admin/editar_sensor.html", data=sensores)
    except Exception as e:
        flash(f"Erro ao recuperar sensores: {e}", "danger")
        return redirect(url_for("index"))

# DELETA SENSORES DO BANCO
@admin_bp.route("/deletar_sensor/<string:tipo>/<int:id>", methods=["POST", "GET"])
@admin_required
def deletar_sensor(tipo, id):
    try:
        if tipo == "Sensor_Posicao":
            sensor = db.session.query(SensorPosicao).filter_by(id=id).first()
        elif tipo == "Sensor_Distancia":
            sensor = db.session.query(SensorDistancia).filter_by(id=id).first()
        elif tipo == "Sensor_Temperatura":
            sensor = db.session.query(SensorTemperatura).filter_by(id=id).first()
        else:
            flash("Tipo de sensor inválido.", "danger")
            return redirect(url_for("gerencia_sensores"))

        if sensor:
            db.session.delete(sensor)
            db.session.commit()
            flash("Sensor deletado com sucesso!", "warning")
        else:
            flash("Sensor não encontrado.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao deletar sensor: {e}", "danger")
    return redirect(url_for("gerencia_sensores"))


# ROTA EDITAR SENSORES
@admin_bp.route("/editar_sensores")
@admin_required
def editar_sensores():
    return render_template("admin/edit/editar_sensores.html")

# GERENCIA ATUADORES DO BANCO
@admin_bp.route("/gerencia_atuador", methods=["POST", "GET"])
@admin_required
def gerencia_atuadores():
    try:
        atuadores = (
            db.session.query(LED.id, db.literal("LED").label("tipo"))
            .union_all(db.session.query(Buzzer.id, db.literal("Buzzer").label("tipo")))
            .union_all(db.session.query(ESPGps.id, db.literal("ESP_GPS").label("tipo")))
            .all()
        )
        if not atuadores:
            flash("Atuadores não encontrados.", "danger")
            return redirect(url_for("index"))
        return render_template("/admin/manage_actuator.html", data=atuadores)
    except Exception as e:
        flash(f"Erro ao recuperar atuadores: {e}", "danger")
        return redirect(url_for("index"))


# DELETA ATUADORES DO BANCO
@admin_bp.route("/deletar_atuador/<string:tipo>/<int:id>", methods=["POST", "GET"])
@admin_required
def deletar_atuador(tipo, id):
    try:
        if tipo == "LED":
            atuador = db.session.query(LED).filter_by(id=id).first()
        elif tipo == "Buzzer":
            atuador = db.session.query(Buzzer).filter_by(id=id).first()
        elif tipo == "ESP_GPS":
            atuador = db.session.query(ESPGps).filter_by(id=id).first()
        else:
            flash("Tipo de atuador inválido.", "danger")
            return redirect(url_for("gerencia_atuadores"))

        if atuador:
            db.session.delete(atuador)
            db.session.commit()
            flash("Atuador deletado com sucesso!", "warning")
        else:
            flash("Atuador não encontrado.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao deletar atuador: {e}", "danger")
    return redirect(url_for("gerencia_atuadores"))

@admin_bp.route("/adicionar_bovino")
@admin_required
def adicionar_bovino():
    return render_template("admin/register_boi.html")

@admin_bp.route("/editar_atuadores")
@admin_required
def editar_atuadores():
    return render_template("admin/edit/editar_atuadores.html")

# ROTA ADICIONAR SENSORES
@admin_bp.route("/adicionar_sensores")
@admin_required
def add_sensores():
    return render_template("admin/add/adicionar_sensores.html")

# ROTA ADICIONAR ATUADORES
@admin_bp.route("/adicionar_atuadores")
@admin_required
def add_atuadores():
    return render_template("admin/add/adicionar_atuadores.html")

# -----------------------------------
# - PERMISSÕES DE ADMIN -

# 1. CRUD DE USUÁRIO ->

# RECUPERA OS USUÁRIOS
@admin_bp.route("/recuperar_usuarios", methods=["GET"])
@admin_required
def recuperar_usuarios():
    try:
        usuarios = db.session.query(Usuario).all()
        if not usuarios:
            flash("Usuários não encontrados.", "danger")
            return redirect(url_for("index"))
        return render_template("/admin/get_users.html", data=usuarios)
    except Exception as e:
        flash(f"Erro ao recuperar usuários: {e}", "danger")
        return redirect(url_for("index"))

# REGISTRAR O USUÁRIO NO BANCO
@admin_bp.route("/registrar_usuario", methods=["POST", "GET"])
@admin_required
def registrar_usuario():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        try:
            usuario = Usuario(nome=nome, email=email, senha=senha)
            db.session.add(usuario)
            db.session.commit()
            flash("Usuário adicionado com sucesso!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao registrar usuário: {e}", "danger")
            return redirect(url_for("index"))
    return render_template("admin/register_user.html")

# GERENCIA OPERAÇÕES DE DELETE E EDIT DE USUÁRIOS REGISTRADOS NO BANCO
@admin_bp.route("/gerencia_usuario", methods=["POST", "GET"])
@admin_required
def gerencia_usuario():
    try:
        usuarios = Usuario.query.all()
        if not usuarios:
            flash("Usuários não encontrados.", "danger")
            return redirect(url_for("index"))
        return render_template("/admin/manage_user.html", data=usuarios)
    except SQLAlchemyError as e:
        flash(f"Erro ao recuperar usuários: {e}", "danger")
        return redirect(url_for("index"))

# EDITA USUÁRIO NO BANCO
@admin_bp.route("/editar_usuario/<int:id>", methods=["POST", "GET"])
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        try:
            usuario.nome = nome
            usuario.email = email
            usuario.senha = senha
            db.session.commit()
            flash("Dados do usuário atualizados com sucesso!", "success")
            return redirect(url_for("admin_bp.gerencia_usuario"))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Erro ao atualizar usuário: {e}", "danger")

    return render_template("admin/edit_user.html", usuario=usuario)

# DELETA USUÁRIO NO BANCO
@admin_bp.route("/deletar_usuario/<int:id>", methods=["POST", "GET"])
@admin_required
def deletar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuário deletado com sucesso!", "warning")
        return redirect(url_for("admin_bp.gerencia_usuario"))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Erro ao deletar usuário: {e}", "danger")
        return redirect(url_for("admin_bp.gerencia_usuario"))

# 2. REGISTROS DE SENSOR/ATUADOR ->
@admin_required
@admin_bp.route("/registrar_dispositivos", methods=["GET", "POST"])
def registrar_dispositivos():
    if request.method == "POST":
        dispositivo = request.form["dispositivo"]
        esp_portao_id = request.form.get("esp_portaoid")
        localizacao = request.form.get("localizacao")
        data_instalacao = request.form.get("data_instalacao")
        fazenda_id = request.form.get("fazendaid")
        
        try:
            if dispositivo == "portao":
                esp_portao = ESPPortao(localizacao=localizacao, data_instalacao=data_instalacao, fazenda_id=fazenda_id)
                db.session.add(esp_portao)
                db.session.commit()
                flash("ESP Portão registrado com sucesso!", "success")

            elif dispositivo == "sensor_distancia":
                sensor_distancia = SensorDistancia(esp_portao_id=esp_portao_id)
                db.session.add(sensor_distancia)
                db.session.commit()
                flash("Sensor de Distância registrado com sucesso!", "success")

            elif dispositivo == "buzzer":
                buzzer = Buzzer(esp_portao_id=esp_portao_id)
                db.session.add(buzzer)
                db.session.commit()
                flash("Buzzer registrado com sucesso!", "success")

            elif dispositivo == "led":
                led = LED(esp_portao_id=esp_portao_id)
                db.session.add(led)
                db.session.commit()
                flash("LED registrado com sucesso!", "success")

            elif dispositivo == "sensor_temperatura":
                sensor_temperatura = SensorTemperatura(esp_portao_id=esp_portao_id)
                db.session.add(sensor_temperatura)
                db.session.commit()
                flash("Sensor de Temperatura registrado com sucesso!", "success")

            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao registrar {dispositivo}: {e}", "danger")
    
    return render_template("admin/register_dispositivos.html")

