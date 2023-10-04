import random
from paho.mqtt import client as mqtt_client
from typing import Callable

class MQTTService:

    __broker = 'broker.emqx.io'
    __port = 1883
    __topic = "python/mqtt"
    # Generate a Client ID with the subscribe prefix.
    __client_id = f'subscribe-{random.randint(0, 100)}'
    # username = 'emqx'
    # password = 'public'


    def connectMqtt(self) -> mqtt_client.Client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.__client_id)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.__broker, self.__port)
        return client
    
    def subscribe(self, client: mqtt_client.Client, callback: Callable):

        def on_message(client, userdata, msg: mqtt_client.MQTTMessage):
            callback(msg.payload.decode())

        client.subscribe(self.__topic)
        client.on_message = on_message

    def run(self, callback: Callable):
        client = self.connectMqtt()
        self.subscribe(client=client, callback=callback)
        client.loop_forever()