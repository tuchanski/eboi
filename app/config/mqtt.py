import paho.mqtt.client as mqtt
import threading

MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
MQTT_TOPIC_DATA = 'wokwi/data'
MQTT_TOPIC_COMMAND = 'wokwi/command'

mqtt_message = None

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao MQTT Broker com código: {rc}")
    client.subscribe(MQTT_TOPIC_DATA)

def on_message(client, userdata, msg):
    global mqtt_message
    mqtt_message = msg.payload.decode()
    print(f"Mensagem recebida: {mqtt_message}")

def init_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

def start_thread():
    mqtt_thread = threading.Thread(target=init_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()
