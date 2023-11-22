import random
import os
from paho.mqtt import client as mqtt_client
from dotenv import dotenv_values
from typing import Callable

class MQTTService:

    __broker = str(dotenv_values(".env")["MQTT_HOST"])
    __port = 8883 # type: ignore
    __sub_topic = str(dotenv_values(".env")["MQTT_SUB_TOPIC"])
    __pub_topic = str(dotenv_values(".env")["MQTT_PUB_TOPIC"])
    __username = str(dotenv_values(".env")["MQTT_USERNAME"])
    __password = str(dotenv_values(".env")["MQTT_PASSWORD"])

    # Generate a Client ID with the subscribe prefix.
    __client_id = f'{__sub_topic}_{__pub_topic}-{random.randint(0, 100)}'
    
    __client: mqtt_client.Client

    def connect(self) -> mqtt_client.Client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        # Prepare
        client = mqtt_client.Client(self.__client_id)
        client.tls_set(os.path.join(os.path.dirname(__file__), '../../', str(dotenv_values(".env")["MQTT_CA_CERT"])))
        client.username_pw_set(self.__username, self.__password)

        # Set Callback
        client.on_connect = on_connect

        client.connect(self.__broker, self.__port)
        return client

    def subscribe(self, callback: Callable):

        def on_message(client, userdata, msg: mqtt_client.MQTTMessage):
            callback(msg.payload.decode())

        self.__client.subscribe(self.__pub_topic)
        self.__client.on_message = on_message

    def publish(self, msg):
        result = self.__client.publish(self.__sub_topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{self.__sub_topic}`")
        else:
            print(f"Failed to send message to topic {self.__sub_topic}")

    def run(self, callback: Callable):
        self.__client = self.connect()
        self.subscribe(callback=callback)
        self.__client.loop_forever()
