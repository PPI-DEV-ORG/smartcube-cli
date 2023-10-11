import random
from paho.mqtt import client as mqtt_client
from typing import Callable

class MQTTService:

    __broker = 'broker.emqx.io'
    __port = 1883
    __topic = "python/mqtt"
    __topic_2 = "smartcube/receivecmd"
    # Generate a Client ID with the subscribe prefix.
    __client_id = f'subscribe-{random.randint(0, 100)}'
    # username = 'emqx'
    # password = 'public'


    client: mqtt_client.Client

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
    
    def subscribe(self, callback: Callable):

        def on_message(client, userdata, msg: mqtt_client.MQTTMessage):
            callback(msg.payload.decode())

        self.client.subscribe(self.__topic)
        self.client.on_message = on_message

    def publish(self, msg):
        result = self.client.publish(self.__topic_2, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{self.__topic_2}`")
        else:
            print(f"Failed to send message to topic {self.__topic_2}")

    def run(self, callback: Callable):
        self.client = self.connectMqtt()
        self.subscribe(callback=callback)
        self.client.loop_forever()