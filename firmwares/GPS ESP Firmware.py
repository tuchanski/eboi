import time
import machine
from time import sleep
from micropyGPS import MicropyGPS
from umqtt.simple import MQTTClient
import network

BROKER_ADDRESS = "broker.hivemq.com"
BROKER_PORT = 1883
CLIENT_ID = "esp32_gps_client"
TOPIC = "esp32/coordinates"

USERNAME = ""
PASSWORD = ""

# Change to your local connection
wifi_ssid = '' # Name
wifi_password = '' # Password

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

    while not wlan.isconnected():
        print("Aguardando conexão Wi-Fi...")
        sleep(1)

    print('Conectado a Wi-Fi:', wlan.ifconfig())

def connect_mqtt(client_id, broker_address, port, username, password):
    client = MQTTClient(client_id, broker_address, port, user=username, password=password)

    try:
        client.connect()
        print("Conectado ao broker MQTT")
    except OSError as e:
        print(f"Erro ao conectar ao broker MQTT: {e}")
        return None

    return client

connect_wifi()

gps = MicropyGPS(local_offset=0)
gps_serial = machine.UART(2, baudrate=9600, tx=17, rx=16)

mqtt_client = connect_mqtt(CLIENT_ID, BROKER_ADDRESS, BROKER_PORT, USERNAME, PASSWORD)

while True:
    try:
        if mqtt_client is None:
            print("Tentando reconectar ao broker MQTT...")
            mqtt_client = connect_mqtt(CLIENT_ID, BROKER_ADDRESS, BROKER_PORT, USERNAME, PASSWORD)

        if gps_serial.any():
            line = gps_serial.readline()
            if line:
                try:
                    line = line.decode('utf-8')
                    for char in line:
                        gps.update(char)
                    
                    if gps.valid:
                        latitude = gps.latitude[0] + (gps.latitude[1] / 60)
                        longitude = gps.longitude[0] + (gps.longitude[1] / 60)

                        if gps.latitude[2] == 'S':
                            latitude = -latitude
                        if gps.longitude[2] == 'W':
                            longitude = -longitude

                        print(f"Latitude: {latitude:.6f}°")
                        print(f"Longitude: {longitude:.6f}°")

                        payload = f"Latitude: {latitude:.6f}°, Longitude: {longitude:.6f}°"
                        mqtt_client.publish(TOPIC, payload.encode())
                        print("Dados enviados ao broker MQTT")
                    else:
                        print("Aguardando fixação do sinal...")
                except Exception as e:
                    print(f"Erro ao decodificar linha: {e}. Ignorando a linha.")
    except Exception as e:
        print(f"Erro na conexão MQTT ou publicação: {e}. Tentando reconectar.")
        mqtt_client = None

    sleep(0.5)
