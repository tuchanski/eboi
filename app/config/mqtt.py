import paho.mqtt.client as mqtt
import threading
from config import db
from models import HistoricoLocalizacao
from models import HistoricoWarning

from flask import current_app as app

MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883

MQTT_TOPIC_COORDINATES = 'eboi/coordinates'
MQTT_TOPIC_TEMPERATURE = 'eboi/temperature'
MQTT_TOPIC_HUMIDITY = 'eboi/humidity'
MQTT_TOPIC_MOTION = 'eboi/motion'

mqtt_list = [MQTT_TOPIC_COORDINATES, MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_HUMIDITY, MQTT_TOPIC_MOTION]

# Usado apenas para verificar se valores recebidos são diferentes para salvar no banco.
last_values = {
    "coordinates": None,
    "temperature": None,
    "humidity": None,
    "motion": None
}

def salvar_historico(sensor, valor, app, bovino_id=None):
    with app.app_context():
        try:
            if sensor == "coordinates":
                historico = HistoricoLocalizacao(bovino_id=bovino_id, localizacao=valor)
            elif sensor == "motion":
                historico = HistoricoWarning(sensor=sensor, valor=valor)
            else:
                if last_values.get(sensor) != valor:
                    historico = HistoricoWarning(sensor=sensor, valor=valor)
                    last_values[sensor] = valor
                else:
                    print(f"Valor não salvo para o sensor {sensor}, pois é igual ao último: {valor}")
                    return

            db.session.add(historico)
            db.session.commit()
            print(f"Dados salvos no banco para o sensor {sensor}: {valor}")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar no banco: {e}")


def on_connect(client, userdata, flags, rc):
    
    if rc == 0:
        print("Conectado ao MQTT Broker!")
        for topic in mqtt_list:
            try:
                client.subscribe(topic)
                print(f"Inscrito no tópico: {topic}")
            except Exception as e:
                print(f"Erro ao inscrever-se no tópico {topic}: {e}")
    else:
        print(f"Falha na conexão, código de erro: {rc}")

def on_message(client, userdata, msg):
   
    app = userdata

    if msg.topic == MQTT_TOPIC_COORDINATES:
        value = msg.payload.decode()
        print(f"Coordenadas recebidas: {value}")
        salvar_historico("coordinates", value, app, bovino_id=1) # Bovino 1

    elif msg.topic == MQTT_TOPIC_TEMPERATURE:
        value = msg.payload.decode()
        print(f"Temperatura recebida: {value}")
        salvar_historico("temperature", value, app)

    elif msg.topic == MQTT_TOPIC_HUMIDITY:
        value = msg.payload.decode()
        print(f"Umidade recebida: {value}")
        salvar_historico("humidity", value, app)

    elif msg.topic == MQTT_TOPIC_MOTION:
        value = msg.payload.decode()
        print(f"Movimento recebido: {value}")
        salvar_historico("motion", value, app)

    else:
        print(f"Mensagem de tópico desconhecido: {msg.topic} -> {msg.payload.decode()}")

def init_mqtt(app):
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.user_data_set(app)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("Iniciando loop MQTT...")
        client.loop_forever()
    except Exception as e:
        print(f"Erro na inicialização do MQTT: {e}")

def start_thread(app):
    try:
        mqtt_thread = threading.Thread(target=init_mqtt, args=(app,))
        mqtt_thread.daemon = True
        mqtt_thread.start()
        print("Thread MQTT iniciada com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar a thread MQTT: {e}")
