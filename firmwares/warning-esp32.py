from machine import Pin, PWM
from utime import sleep, time
from umqtt.simple import MQTTClient
import network
import dht

WIFI_SSID = ""  # Nome da rede
WIFI_PASSWORD = ""  # Senha da rede

BROKER_ADDRESS = "broker.hivemq.com"
BROKER_PORT = 1883
CLIENT_ID = "esp32_motion_client"
TOPIC_MOTION = "esp32/motion"
TOPIC_TEMPERATURE = "esp32/temperature"
TOPIC_HUMIDITY = "esp32/humidity"
USERNAME = ""
PASSWORD = ""

buzzer = PWM(Pin(14))
buzzer.duty(0)
led = Pin(15, Pin.OUT)
pir_sensor = Pin(21, Pin.IN)
dht_sensor = dht.DHT22(Pin(23))

motion_timeout = 3
last_detection_time = 0

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        sleep(1)
    
    print("Conectado ao Wi-Fi:", wlan.ifconfig())

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER_ADDRESS, BROKER_PORT, user=USERNAME, password=PASSWORD)
    try:
        client.connect()
        print("Conectado ao broker MQTT")
        return client
    except Exception as e:
        print(f"Erro ao conectar ao broker MQTT: {e}")
        sleep(5)
        return connect_mqtt()

def publish_dht_data(client):
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        client.publish(TOPIC_TEMPERATURE, str(temperature))
        client.publish(TOPIC_HUMIDITY, str(humidity))
        print(f"Temperatura: {temperature} °C, Umidade: {humidity} %")
    except Exception as e:
        print(f"Erro ao ler dados do DHT22: {e}")

connect_wifi()
mqtt_client = connect_mqtt()

while True:
    if pir_sensor.value() and (time() - last_detection_time > motion_timeout):
        print("Movimento detectado!")
        buzzer.freq(500)
        buzzer.duty(256)
        led.on()
        last_detection_time = time()

        mqtt_client.publish(TOPIC_MOTION, "Movimento detectado!")
        publish_dht_data(mqtt_client)

        sleep(1)
        buzzer.duty(0)
        led.off()
    else:
        buzzer.duty(0)
        led.off()
    sleep(0.1)
