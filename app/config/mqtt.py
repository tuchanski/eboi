import paho.mqtt.client as mqtt
import threading
import time

MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883

#MQTT_TOPIC_DATA = 'wokwi/data'
#MQTT_TOPIC_COMMAND = 'wokwi/command'

MQTT_TOPIC_COORDINATES = 'esp32/coordinates'
MQTT_TOPIC_TEMPERATURE = 'esp32/temperature'
MQTT_TOPIC_HUMIDITY = 'esp32/humidity'
MQTT_TOPIC_MOTION = 'esp32/motion'

mqtt_list = [MQTT_TOPIC_COORDINATES, MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_HUMIDITY, MQTT_TOPIC_MOTION]

message_coordinates = None
message_temperature = None
message_humidity = None
message_motion = None

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
    global message_coordinates, message_temperature, message_humidity, message_motion

    if msg.topic == MQTT_TOPIC_COORDINATES:
        message_coordinates = msg.payload.decode()
        print(f"Coordenadas recebidas: {message_coordinates}")
    
    elif msg.topic == MQTT_TOPIC_TEMPERATURE:
        message_temperature = msg.payload.decode()
        print(f"Temperatura recebida: {message_temperature}")
        
    elif msg.topic == MQTT_TOPIC_HUMIDITY:
        message_humidity = msg.payload.decode()
        print(f"Umidade recebida: {message_humidity}")
       
    elif msg.topic == MQTT_TOPIC_MOTION:
        message_motion = msg.payload.decode()
        print(f"Movimento recebido: {message_motion}")
      
    else:
        print(f"Mensagem de tópico desconhecido: {msg.topic} -> {msg.payload.decode()}")

def init_mqtt():
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("Iniciando loop MQTT...")
        client.loop_forever()
    except Exception as e:
        print(f"Erro na inicialização do MQTT: {e}")

def start_thread():
    try:
        mqtt_thread = threading.Thread(target=init_mqtt)
        mqtt_thread.daemon = True
        mqtt_thread.start()
        print("Thread MQTT iniciada com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar a thread MQTT: {e}")
