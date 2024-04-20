import paho.mqtt.client as mqtt
import asyncio
from datetime import datetime
from pytz import timezone
import time

BROKER = "test.mosquitto.org"
CLIENT_ID = ""

timezone = timezone('US/Eastern')

class EnergyController:
    def __init__(self, serial_number):
        self.pi_number = str(serial_number)
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1,client_id=CLIENT_ID, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.username_pw_set(None, password=None)
        self.records = {}
    
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected to ", client._host, "port: ", client._port)
        print("Flags: ", flags, "returned code: ", rc)
        client.subscribe("OpenDemandResponse/Event/BoroughHall", qos=0)
        
    # The callback for when a message is published.
    def on_publish(self, client, userdata, mid):
        pass
    
    # The callback for when a message is received.
    def on_message(self, client, userdata, msg):
        message = str(msg.payload.decode("utf-8"))
        if msg.topic == "OpenDemandResponse/Event/BoroughHall":
            print(message)
            event, event_type, start_time,timestamp = message.split("#")
            if event_type == 'immediate':
                #self.records[name] = uid
                print("{} {} event, starting at {}".format(event, event_type, start_time))
    
    def run(self):
        self.client.connect(THE_BROKER, port=1883, keepalive=60)
        self.client.loop_start()
        while True:
            #id_, name = self.reader.read()
            dc_voltage = str(4.99)
            dc_current = str(.51)
            update = True
            if update:
                #name = name.strip()
                timestamp = datetime.now(eastern).strftime("%Y-%m-%d %H:%M:%S")
                self.client.publish("OpenDemandResponse/Participant/AlexN", payload="#".join([dc_voltage, dc_current, timestamp]), qos=0, retain=False)
            time.sleep(3)
    
    def stop_tracking(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == '__main__':
    controller = EnergyController(1)
    controller.run()
