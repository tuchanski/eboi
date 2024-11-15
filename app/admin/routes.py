from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import psycopg2
import psycopg2.extras
from functools import wraps
from config import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

conn = db.get_connection()

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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        query = """
        SELECT 'Sensor_Posicao' AS tipo, id, esp_gpsid FROM Sensor_Posicao
        UNION ALL
        SELECT 'Sensor_Distancia' AS tipo, id, esp_portaoid FROM Sensor_Distancia
        UNION ALL
        SELECT 'Sensor_Temperatura' AS tipo, id, esp_portaoid FROM Sensor_Temperatura;
        """
        cursor.execute(query)
        sensores = cursor.fetchall()
        if not sensores:
            flash("Sensores não encontrados.", "danger")
            return redirect(url_for("index"))
        return render_template("/admin/manage_sensor.html", data=sensores)
    except Exception as e:
        print(f"Erro ao recuperar sensores: {e}")
    finally:
        cursor.close()
    return redirect(url_for("index"))

# DELETA SENSORES DO BANCO
@admin_bp.route("/deletar_sensor/<string:tipo>/<int:id>", methods=["POST", "GET"])
@admin_required
def deletar_sensor(tipo, id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if tipo == "Sensor_Posicao":
            cursor.execute("DELETE FROM Sensor_Posicao WHERE id = %s", (id,))
        elif tipo == "Sensor_Distancia":
            cursor.execute("DELETE FROM Sensor_Distancia WHERE id = %s", (id,))
        elif tipo == "Sensor_Temperatura":
            cursor.execute("DELETE FROM Sensor_Temperatura WHERE id = %s", (id,))
        else:
            flash("Tipo de sensor inválido.", "danger")
            return redirect(url_for("gerencia_sensores"))

        if cursor.rowcount > 0:
            conn.commit()
            flash("Sensor deletado com sucesso!", "warning")
        else:
            flash("Sensor não encontrado.", "danger")
            conn.rollback()
    except Exception as e:
        flash(f"Erro ao deletar sensor: {e}", "danger")
        conn.rollback()
    finally:
        cursor.close()
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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        query = """
        SELECT 'LED' AS tipo, id FROM LED
        UNION ALL
        SELECT 'Buzzer' AS tipo, id FROM Buzzer
        UNION ALL
        SELECT 'ESP_GPS' AS tipo, id FROM ESP_Gps;
        """
        cursor.execute(query)
        atuadores = cursor.fetchall()
        if not atuadores:
            flash("Atuadores não encontrados.", "danger")
            return redirect(url_for("index"))
        return render_template("/admin/manage_actuator.html", data=atuadores)
    except Exception as e:
        print(f"Erro ao recuperar atuadores: {e}")
    finally:
        cursor.close()
    return redirect(url_for("index"))

# DELETA ATUADORES DO BANCO
@admin_bp.route("/deletar_atuador/<string:tipo>/<int:id>", methods=["POST", "GET"])
@admin_required
def deletar_atuador(tipo, id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if tipo == "LED":
            cursor.execute("DELETE FROM LED WHERE id = %s", (id,))
        elif tipo == "Buzzer":
            cursor.execute("DELETE FROM Buzzer WHERE id = %s", (id,))
        elif tipo == "ESP_GPS":
            cursor.execute("DELETE FROM ESP_Gps WHERE id = %s", (id,))
        else:
            flash("Tipo de atuador inválido.", "danger")
            return redirect(url_for("gerencia_atuadores"))

        if cursor.rowcount > 0:
            conn.commit()
            flash("Atuador deletado com sucesso!", "warning")
        else:
            flash("Atuador não encontrado.", "danger")
            conn.rollback()

    except Exception as e:
        flash(f"Erro ao deletar atuador: {e}", "danger")
        conn.rollback()
    finally:
        cursor.close()
    return redirect(url_for("gerencia_atuadores"))

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
    finally:
        cursor.close()
    return redirect(url_for("index"))

# REGISTRAR O USUÁRIO NO BANCO
@admin_bp.route("/registrar_usuario", methods=["POST", "GET"])
@admin_required
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
            return redirect(url_for("index"))
        finally:
            cursor.close()
    return render_template("admin/register_user.html")

# GERENCIA OPERAÇÕES DE DELETE E EDIT DE USUÁRIOS REGISTRADOS NO BANCO
@admin_bp.route("/gerencia_usuario", methods=["POST", "GET"])
@admin_required
def gerencia_usuario():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM usuario")
        usuarios = cursor.fetchall()
        if not usuarios:
            flash("Usuários não encontrados.", "danger")
            return redirect(url_for("index"))
        return render_template("/admin/manage_user.html", data=usuarios)
    except Exception as e:
        print(f"Erro ao recuperar usuários: {e}")
    finally:
        cursor.close()
    return redirect(url_for("index"))

# EDITA USUÁRIO NO BANCO
@admin_bp.route("/editar_usuario/<int:id>", methods=["POST", "GET"])
@admin_required
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
    finally:
        cursor.close()
    
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

    try:
        cursor.execute(
            "UPDATE usuario SET Nome = %s, Email = %s, Senha = %s WHERE id = %s",
            (nome, email, senha, id)
        )
        conn.commit()
        flash("Dados do usuário atualizados com sucesso!", "success")
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        conn.rollback()
    finally:
        cursor.close()
    
    return render_template("admin/edit_user.html", usuario=usuario)

# DELETA USUÁRIO NO BANCO
@admin_bp.route("/deletar_usuario/<int:id>", methods=["POST", "GET"])
@admin_required
def deletar_usuario(id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
        conn.commit()
        flash("Usuário deletado com sucesso!", "warning")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Erro ao deletar usuário: {e}", "danger")
        conn.rollback()
    finally:
        cursor.close()

# 2. REGISTROS DE SENSOR/ATUADOR ->
@admin_bp.route("/registrar_dispositivos", methods=["GET", "POST"])
@admin_required
def registrar_dispositivos():
    if request.method == "POST":
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dispositivo = request.form["dispositivo"]
        esp_portao_id = request.form.get("esp_portaoid")
        localizacao = request.form.get("localizacao")
        data_instalacao = request.form.get("data_instalacao")
        fazenda_id = request.form.get("fazendaid")
        
        try:
            if dispositivo == "portao":
                cursor.execute(
                    "INSERT INTO ESP_Portao (Localizacao, Data_Instalacao, FazendaID) VALUES (%s, %s, %s)",
                    (localizacao, data_instalacao, fazenda_id)
                )
                flash("ESP Portão registrado com sucesso!", "success")
            elif dispositivo == "sensor_distancia":
                cursor.execute(
                    "INSERT INTO Sensor_Distancia (ESP_PortaoID) VALUES (%s)", (esp_portao_id,)
                )
                flash("Sensor de Distância registrado com sucesso!", "success")
            elif dispositivo == "buzzer":
                cursor.execute(
                    "INSERT INTO Buzzer (ESP_PortaoID) VALUES (%s)", (esp_portao_id,)
                )
                flash("Buzzer registrado com sucesso!", "success")
            elif dispositivo == "led":
                cursor.execute(
                    "INSERT INTO LED (ESP_PortaoID) VALUES (%s)", (esp_portao_id,)
                )
                flash("LED registrado com sucesso!", "success")
            elif dispositivo == "sensor_temperatura":
                cursor.execute(
                    "INSERT INTO Sensor_Temperatura (ESP_PortaoID) VALUES (%s)", (esp_portao_id,)
                )
                flash("Sensor de Temperatura registrado com sucesso!", "success")
            conn.commit()
            return redirect(url_for("index"))
        except Exception as e:
            conn.rollback()
            flash(f"Erro ao registrar {dispositivo}: {e}", "danger")
        finally:
            cursor.close()
    return render_template("admin/register_dispositivos.html")

