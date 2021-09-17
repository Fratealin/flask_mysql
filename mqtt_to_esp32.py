# -----------------------------------------------------------
# Sends MQTT messages to esp to control led and buzzer
# Receives sensor data from esp via MQTT
# Returns a dictionary with light, humidity, temperature data
# -----------------------------------------------------------

import paho.mqtt.client as mqtt # Import the MQTT library

import time # The time library is useful for delays

import json # Json library used to get config



# Get MQTT credentials from config file
with open("/home/pi/python_scripts/flask_mysql/config.json", "r") as f:
    config = json.load(f)
    MQTTbroker = config["MQTT"]["MQTTbroker"]
    MQTT_ADDRESS = config["MQTT"]["MQTT_ADDRESS"]
    MQTT_USER = config["MQTT"]["MQTT_USER"]
    MQTT_PASSWORD = config["MQTT"]["MQTT_PASSWORD"]


# define topics to control esp buzzer and led
topic_buzz = "esp32/buzz"
topic_led = "esp32/output"
# define esp sensor topics
topic_light = 'esp32/light'
topic_humidity = 'esp32/humidity'
topic_temperature = 'esp32/temperature'

#initialise dictionary to story mqtt topics
data_dict = {}


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe([(topic_light, 2),(topic_temperature,1),(topic_humidity, 0)]) # the second item in the tuple is qos - quality of service


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + msg.payload.decode())
    data_dict[msg.topic] = msg.payload


def main():
    # Connect to mqtt server
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)

    # Send mqtt message to esp to switch off buzzer at start
    mqtt_client.publish("esp32/buzz", "off")

    mqtt_client.loop_forever()


def get_esp_data():
    # Connect to mqtt server
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)

    # Send mqtt message to esp to switch off buzzer at start
    mqtt_client.publish("esp32/buzz", "off")

    mqtt_client.loop_start() #start loop

    # Wait until light, humidity and temperature topics have been filled
    while len(data_dict) <3:
        continue

    mqtt_client.disconnect() #disconnect
    mqtt_client.loop_stop() #stop loop
    return data_dict

def control_esp(on_or_off):
    # Connect to mqtt server
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_ADDRESS, 1883)

    mqtt_client.loop_start() # start loop

    mqtt_client.publish(topic_buzz, on_or_off)
    mqtt_client.publish(topic_led, on_or_off)

    mqtt_client.disconnect() #disconnect
    mqtt_client.loop_stop() #stop loop

if __name__ == '__main__':
    #main()
    get_esp_data()
