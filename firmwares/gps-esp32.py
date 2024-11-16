import time
import machine
from micropyGPS import MicropyGPS
from umqtt.simple import MQTTClient
import network

WIFI_SSID = ""  # Nome da rede
WIFI_PASSWORD = ""  # Senha da rede

BROKER_ADDRESS = "broker.hivemq.com"
BROKER_PORT = 1883
CLIENT_ID = "esp32_gps_client"
TOPIC = "esp32/coordinates"
USERNAME = ""
PASSWORD = ""

gps = MicropyGPS(local_offset=0)
gps_serial = machine.UART(2, baudrate=9600, tx=17, rx=16)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        print("Aguardando conexão Wi-Fi...")
        time.sleep(1)

    print("Conectado ao Wi-Fi:", wlan.ifconfig())

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER_ADDRESS, BROKER_PORT, user=USERNAME, password=PASSWORD)
    try:
        client.connect()
        print("Conectado ao broker MQTT")
        return client
    except OSError as e:
        print(f"Erro ao conectar ao broker MQTT: {e}")
        return None

connect_wifi()
mqtt_client = connect_mqtt()

while True:
    try:
        if mqtt_client is None:
            print("Tentando reconectar ao broker MQTT...")
            mqtt_client = connect_mqtt()

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

                        payload = f"Latitude: {latitude:.6f}°, Longitude: {longitude:.6f}°"
                        mqtt_client.publish(TOPIC, payload.encode())
                        print("Dados enviados:", payload)
                    else:
                        print("Aguardando fixação do sinal GPS...")
                except Exception as e:
                    print(f"Erro ao processar linha do GPS: {e}")
    except Exception as e:
        print(f"Erro na conexão MQTT: {e}")
        mqtt_client = None
    time.sleep(0.5)
