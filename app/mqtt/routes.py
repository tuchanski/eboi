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
