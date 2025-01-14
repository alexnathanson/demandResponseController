# this script is for aggregation participants

import paho.mqtt.client as mqtt
import asyncio
from datetime import datetime
from pytz import timezone
import time
import ssl

BROKER = "test.mosquitto.org"
CLIENT_ID = ""

'''
if true, port 8884 is used (encrypted, client certificate required)
else, port 1883 is used (unencrypted, unauthenticated)
'''
encrypt = False

if encrypt:
    myPort = 8884
else:
    myPort = 1883

timezone = timezone('US/Eastern')

network = "BoroughHall"

class EnergyController:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1,client_id=CLIENT_ID, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_connect_fail = self.on_connect_fail
        #self.client.on_log = self.on_log
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.path = 'demandResponseController/'
        if encrypt:
            self.client.tls_set(ca_certs=self.path +"keys/mosquitto.org.crt", certfile=self.path +"keys/client.crt",keyfile=self.path +"keys/client.key", tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.username_pw_set(None, password=None)
        self.data = {}
    
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected to ", client._host, "port: ", client._port)
        print("Flags: ", flags, "returned code: ", rc)
        client.subscribe("OpenDemandResponse/Event/"+network, qos=0)
    
    def on_connect_fail(self, client, userdata):
        print("Failed to connect")

    def on_log(self, client, userdata, level, buf):
        print(level)
        print(buf)

    # The callback for when a message is published.
    def on_publish(self, client, userdata, mid):
        pass
    
    # The callback for when a message is received.
    def on_message(self, client, userdata, msg):
        message = str(msg.payload.decode("utf-8"))
        if msg.topic == "OpenDemandResponse/Event/"+network:
            event, event_type, start_time,timestamp = message.split("#")
            self.data = {'event':event,'type':event_type,'start_time':start_time,'msg_timestamp':timestamp}
            print('********* RECIEVING *******************')
            print("{} {} event, starting at {}".format(event, event_type, start_time))
            print('***************************************')

    def start(self):
        self.client.connect(BROKER, port=myPort, keepalive=60)
        self.client.loop_start()
    
    def publish(self, data):
        timestamp = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        d = []
        for k, v in data.items():
            d.append(str(v))
        d.append(timestamp)
        print('%%%%%% PUBLISHING %%%%%%')
        print(d)
        print('%%%%%%%%%%%%%%%%%%%')
        self.client.publish("OpenDemandResponse/Participant/AlexN", payload="#".join(d), qos=0, retain=False)
        self.client.publish("OpenDemandResponse/participants", payload="AlexN", qos=0, retain=False)

    
    def stop_tracking(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == '__main__':
    controller = EnergyController()
    controller.start()
