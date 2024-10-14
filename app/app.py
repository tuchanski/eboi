# Instale o driver para comunicação com o Postgresql pip install psycopg2

from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, session
import psycopg2
import psycopg2.extras
import os
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)

# INFORMAÇÕES DE CONEXÃO COM BANCO Postgresql
DB_HOST = "localhost"
DB_NAME = "eBoi"
DB_USER  = "postgres"
DB_PASS = "postgres" # MUDE CONFORME A SUA MÁQUINA
DB_PORT = "5432"

# CONEXÃO COM BANCO DE DADOS
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

# -- GERAL DO MQTT --

# CONFIGURAÇÕES MQTT
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
MQTT_TOPIC_DATA = 'wokwi/data'
MQTT_TOPIC_COMMAND = 'wokwi/command'

# ÚLTIMA MENSAGEM RECEBIDA PELO MQTT
mqtt_message = None

# CALLBACK QUANDO SE CONECTA NO MQTT BROKER
def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao MQTT Broker com código: {rc}")
    client.subscribe(MQTT_TOPIC_DATA)

# CALLBACK PRA TRATAR MENSAGENS RECEBIDAS
def on_message(client, userdata, msg):
    global mqtt_message
    mqtt_message = msg.payload.decode()
    print(f"Mensagem recebida: {mqtt_message}")

# INICIALIZA CLIENTE MQTT EM UMA THREAD SEPARADA
def init_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# INICIALIZA A THREAD QND O APP FLASK INICIAR
mqtt_thread = threading.Thread(target=init_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

# -- FIM DA SESSÃO GERAL DO MQTT --

# VERIFICA SE USUÁRIO É ADMINISTRADOR OU NÃO. CASO NÃO SEJA/NÃO ESTEJA LOGADO, REDIRECIONA P/ HOME.
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "usuario_id" not in session or session.get("usuario_tipo") != "admin":
            flash("Acesso restrito aos administradores.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrap

def login_required(f):
    @wraps(f)
    def wrap2(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Você precisa estar logado para acessar esta página.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap2

# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    usuario_tipo = session.get('usuario_tipo')
    if usuario_tipo:
        return render_template("home/home.html", usuario_tipo=usuario_tipo)
    else:
        return redirect(url_for("login"))

# ROTA DA PÁGINA COTAR
@app.route("/cotar")
def cotar():
    return render_template("others/cotar.html")

# ROTA DA PÁGINA SOBRE NOS
@app.route("/sobre-nos")
def sobre_nos():
    return render_template("others/sobre-nos.html")

# ROTA DA PÁGINA FAQ
@app.route("/faq")
def faq():
    return render_template("others/faq.html")

# ROTA EDITAR SENSORES
@app.route("/editar_sensores")
def editar_sensores():
    return render_template("admin/editar_sensores.html")

# ROTA EDITAR ATUADOERS
@app.route("/editar_atuadores")
def editar_atuadores():
    return render_template("admin/editar_atuadores.html")

# LÓGICA DO LOGIN COM VALIDAÇÃO
@app.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("login"))
            
            session["usuario_id"] = usuario["id"]
            session["usuario_email"] = usuario["email"]
            session["usuario_tipo"] = usuario["tipo"]

            flash("Login bem-sucedido!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erro ao buscar usuário: {e}", "danger")
            return redirect(url_for("login"))
    return render_template("auth/login.html")

# TELA DO PERFIL DO USUÁRIO

@app.route("/perfil")
@login_required
def perfil():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        id = session["usuario_id"]
        cursor.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        return render_template("profile/perfil.html", usuario=usuario)
    except Exception as e:
        print(f"Erro ao recuperar usuário: {e}")
    return redirect(url_for("index"))

# ROTA PARA LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("login"))


@app.route("/admin")
# @admin_required
def admin():
    return render_template("admin/admin.html")

# -----------------------------------
# - PERMISSÕES DE ADMIN -

# 1. CRUD DE USUÁRIO ->

# RECUPERA OS USUÁRIOS E CONTÉM ATALHOS PARA EDITAR E EXCLUIR
@app.route("/recuperar_usuarios", methods=["GET"])
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
    return redirect(url_for("index"))

# REGISTRAR O USUÁRIO NO BANCO
@app.route("/registrar_usuario", methods=["POST", "GET"])
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
    return render_template("admin/register_user.html")

# EDITAR E DELETAR USUÁRIO NO BANCO
@app.route("/gerenciar_usuario/<int:id>", methods=["POST", "GET"])
@admin_required
def gerenciar_usuario(id):
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
        if 'editar' in request.form:
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
                flash("Erro ao atualizar usuário.", "danger")
        elif 'deletar' in request.form:
            try:
                cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
                conn.commit()
                flash("Usuário deletado com sucesso!", "warning")
                return redirect(url_for("index"))
            except Exception as e:
                flash(f"Erro ao deletar usuário: {e}", "danger")
                conn.rollback()

    return render_template("admin/manage_user.html", usuario=usuario)

# 2. REGISTROS DE SENSOR/ATUADOR ->
@app.route("/registrar_dispositivos", methods=["GET", "POST"])
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
    return render_template("admin/register_dispositivos.html")

# ROTA PARA VISUALIZAÇÃO DOS DADOS EM TEMPO REAL (PERMITIDO ADM E USUÁRIO NORMAL)
@app.route("/dados-tempo-real")
@login_required
def dados_tempo_real():
    global mqtt_message
    return render_template("mqtt/dados_tempo_real.html", message=mqtt_message)

# ROTA PRA ENVIAR COMANDOS VIA MQTT
@app.route("/comando-remoto", methods=["GET", "POST"])
@login_required
def comando_remoto():
    if request.method == "POST":
        comando = request.form["comando"]
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC_COMMAND, comando)
        flash(f"Comando '{comando}' enviado com sucesso!", "success")
    return render_template("mqtt/comando_remoto.html")

# -----------------------------------
            
if __name__ == "__main__":
    app.run("localhost", 8080, None)