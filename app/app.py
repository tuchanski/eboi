import os
from functools import wraps

import psycopg2
import psycopg2.extras
import paho.mqtt.client as mqtt_client

from flask import Flask, render_template, request, flash, redirect, url_for, session
from config.db import db, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from admin.routes import admin_bp
from auth.routes import auth_bp
from general.routes import general_bp
from flask_sqlalchemy import SQLAlchemy
from config import mqtt as mqtt_package

app = Flask(__name__)
app.secret_key = os.urandom(24)


app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(general_bp)

mqtt_thread = mqtt_package.start_thread()

# -----------------------------------

# DECORATIVOS
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
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrap2

# -----------------------------------
# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    usuario_tipo = session.get('usuario_tipo')
    if usuario_tipo:
        return render_template("home/home.html", usuario_tipo=usuario_tipo)
    else:
        return redirect(url_for("auth.login"))


# ROTA PARA VISUALIZAÇÃO DOS DADOS EM TEMPO REAL (PERMITIDO ADM E USUÁRIO NORMAL)
@app.route("/dados-tempo-real")
@login_required
def dados_tempo_real():
    global mqtt_message
    return render_template("mqtt/dados_tempo_real.html", temperature=mqtt_package.message_temperature, humidity=mqtt_package.message_humidity,
                            motion=mqtt_package.message_motion, coordinates=mqtt_package.message_coordinates)

# ROTA PRA ENVIAR COMANDOS VIA MQTT
@app.route("/comando-remoto", methods=["GET", "POST"])
@login_required
def comando_remoto():
    if request.method == "POST":
        comando = request.form["comando"]
        client = mqtt_client.Client()
        client.connect(mqtt_package.MQTT_BROKER, mqtt_package.MQTT_PORT, 60)
        client.publish(mqtt_package.MQTT_TOPIC_COMMAND, comando)
        flash(f"Comando '{comando}' enviado com sucesso!", "success")
    return render_template("mqtt/comando_remoto.html")

# -----------------------------------
            
if __name__ == "__main__":
    app.run("localhost", 8080, None)