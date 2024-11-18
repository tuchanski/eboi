from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from config import db
from functools import wraps
import psycopg2
import psycopg2.extras
import paho.mqtt.client as mqtt_client
from config import mqtt as mqtt_package

from models import HistoricoLocalizacao
from models import HistoricoWarning

mqtt_bp = Blueprint('auth', __name__, url_prefix='/mqtt')

conn = db.get_connection()

def login_required(f):
    @wraps(f)
    def wrap2(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Você precisa estar logado para acessar esta página.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrap2

# ROTA PARA VISUALIZAÇÃO DOS DADOS EM TEMPO REAL (PERMITIDO ADM E USUÁRIO NORMAL)
@mqtt_bp.route("/dados-tempo-real")
@login_required
def dados_tempo_real():
    global mqtt_message
    return render_template("mqtt/dados_tempo_real.html", message=mqtt_package.mqtt_message)

# ROTA PRA ENVIAR COMANDOS VIA MQTT
@mqtt_bp.route("/comando-remoto", methods=["GET", "POST"])
@login_required
def comando_remoto():
    if request.method == "POST":
        comando = request.form["comando"]
        client = mqtt_client.Client()
        client.connect(mqtt_package.MQTT_BROKER, mqtt_package.MQTT_PORT, 60)
        client.publish(mqtt_package.MQTT_TOPIC_COMMAND, comando)
        flash(f"Comando '{comando}' enviado com sucesso!", "success")
    return render_template("mqtt/comando_remoto.html")

