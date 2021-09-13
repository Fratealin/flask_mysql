import paho.mqtt.client as mqtt # Import the MQTT library

import time # The time library is useful for delays

myTopic = "esp32/buzz"
MQTTbroker = "localhost"


MQTT_ADDRESS = '192.168.1.15'
MQTT_USER = 'alidore'
MQTT_PASSWORD = 'mournes'
topic_light = 'esp32/light'
topic_humidity = 'esp32/humidity'
topic_temperature = 'esp32/temperature'


data_dict = {}

counter = 0

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe([(topic_light, 2),(topic_temperature,1),(topic_humidity, 0)]) # the second item in the tuple is qos - quality of service


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + msg.payload.decode())
    print(".")
    data_dict[msg.topic] = msg.payload


def main():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.publish("esp32/buzz", "off")

    mqtt_client.loop_forever()


def get_esp_data():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.publish("esp32/buzz", "off")

    mqtt_client.loop_start()

    while len(data_dict) <3:
        continue
    mqtt_client.disconnect() #disconnect
    mqtt_client.loop_stop() #stop loop
    return data_dict


def subscribe_and_publish():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_message=on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_start()
    

    counter = 0
    while counter <= 3:
        continue




    mqtt_client.subscribe("esp32/light")   
    time.sleep(2)
    mqtt_client.publish("esp32/output", "on")
    time.sleep(2)
        
    mqtt_client.disconnect() #disconnect
    mqtt_client.loop_stop() #stop loop

def control_esp(on_or_off):
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    #mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)

    mqtt_client.loop_start()

    mqtt_client.publish("esp32/buzz", on_or_off)
    mqtt_client.publish("esp32/output", on_or_off)



    #while len(data_dict) <3:
    #    continue
    mqtt_client.disconnect() #disconnect
    mqtt_client.loop_stop() #stop loop

if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()

