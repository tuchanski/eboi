from machine import Pin, PWM
from utime import sleep, time
from umqtt.simple import MQTTClient
import network
import dht

buzzer = PWM(Pin(14))
led = Pin(15, Pin.PULL_UP)
buzzer.duty(0)
pir_pin = Pin(21, Pin.IN)

dht_pin = Pin(23)
dht_sensor = dht.DHT22(dht_pin)

mqtt_server = "broker.hivemq.com" 
mqtt_topic_motion = "esp32/motion"
mqtt_topic_temperature = "esp32/temperature"
mqtt_topic_humidity = "esp32/humidity"
mqtt_client_id = "esp32-motion-client-" + str(time())

motion_detected = False
last_detection_time = 0
motion_timeout = 3

# Change to your local connection
wifi_ssid = '' # Name
wifi_password = '' # Password

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    
    while not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        sleep(1)
    
    print("Conectado ao Wi-Fi, IP:", wlan.ifconfig()[0])

def connect_mqtt():
    client = MQTTClient(mqtt_client_id, mqtt_server)
    try:
        client.connect()
        print("Conectado ao broker MQTT")
        return client
    except Exception as e:
        print("Falha ao conectar no broker MQTT:", e)
        sleep(5)
        return connect_mqtt()

def read_and_publish_dht_data(client):
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        client.publish(mqtt_topic_temperature, str(temperature))
        client.publish(mqtt_topic_humidity, str(humidity))

        print("Temperatura:", temperature, "°C")
        print("Umidade:", humidity, "%")

    except Exception as e:
        print("Erro ao ler dados do DHT22:", e)

connect_wifi()
mqtt_client = connect_mqtt()

while True:
    if pir_pin.value() and (time() - last_detection_time) > motion_timeout:
        print("Movimento detectado!")
        buzzer.freq(500)
        buzzer.duty(256)
        led.on()
        last_detection_time = time()
        
        mqtt_client.publish(mqtt_topic_motion, "Movimento detectado!")
        
        read_and_publish_dht_data(mqtt_client)

        sleep(1)
        led.off()
        sleep(1)
    else:
        buzzer.duty(0)
        led.off()
        sleep(0.1)
