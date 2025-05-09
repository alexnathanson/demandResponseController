# this script is for testing aggregator commands

import paho.mqtt.client as mqtt
import asyncio
from datetime import datetime
from pytz import timezone
import time
import random
import ssl

BROKER = "test.mosquitto.org"
CLIENT_ID = ""

timezone = timezone('US/Eastern')


eventNames = ['DLRP','CSRP']
eventTypes = ['contingency','immediate']
eventTimes = [11,14, 16, 17, 19]

class EnergyController:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1,client_id=CLIENT_ID, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.username_pw_set(None, password=None)
        #self.client.tls_set(ca_certs="keys/mosquitto.org.crt", certfile="keys/client.crt",keyfile="keys/client.key", #tls_version=ssl.PROTOCOL_TLSv1_2) #needed for ports 8883 and 8884
        self.records = {}
    
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected to ", client._host, "port: ", client._port)
        print("Flags: ", flags, "returned code: ", rc)
        client.subscribe("OpenDemandResponse/Participant/AlexN", qos=0)
        
    # The callback for when a message is published.
    def on_publish(self, client, userdata, mid):
        pass
    
    # The callback for when a message is received.
    def on_message(self, client, userdata, msg):
        message = str(msg.payload.decode("utf-8"))
        if msg.topic == "OpenDemandResponse/Participant/AlexN":
            print('')
            battery, ac_out, ac_in, dc_out, dc_in, r1, pv, rpi, load, timestamp = message.split("#")
            print("Data at {}".format(timestamp))
            print("Battery: {}% \nload: {}\nAC Out: {}W, AC In: {}W, DC Out: {}W, DC In: {}W\nRelay State: {}\nPV: {}W\nRaspberry Pi: {}W".format(battery, load, ac_out, ac_in,dc_out, dc_in,r1,pv, rpi))
    
    # returns some key
    def auth(self):
        return gfdgsdfhsdfsjdf

    def run(self, freq):
        self.client.connect(BROKER, port=1883, keepalive=60)
        self.client.loop_start()
        authUpdate = False
        while True:
            event = eventNames[random.randint(0,len(eventNames)-1)]
            event_type = eventTypes[random.randint(0,len(eventTypes)-1)]
            start_time = eventTimes[random.randint(0,len(eventTimes)-1)]

            # update key when first connected
            if authUpdate:
                a = self.auth()
                self.client.publish("OpenDemandResponse/Auth", payload=a, qos=0, retain=False)
                authUpdate = False
            update = True
            if update:
                timestamp = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
                self.client.publish("OpenDemandResponse/Event/BoroughHall", payload="#".join([event, event_type, str(start_time), timestamp]), qos=0, retain=False)

            time.sleep(freq)
    
    def stop_tracking(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == '__main__':
    controller = EnergyController()
    controller.run(90)
