# demandResponseController

Hardware and software for gathering data and controlling a power station for demand response aggregation

Both the aggregator and participant act as clients, sending and receiving data from the MQTT server.

## Installation Notes

Install this version of bluetti_mqtt (should be done in venv): https://www.github.com/alexnathanson/bluetti_mqtt
1) clone repository to RPi
2) From inside the repository directory run `pip install .`

## Running

### Participant on Linux

#### Automating at startup

Open rc.local `sudo nano /etc/rc.local`
    * add this line above "exit 0" `sudo -H -u USER_NAME /bin/bash /home/USER_NAME/demandResponseController/start.sh > /home/USER_NAME/demandResponseController/start.log 2>&1 &``

Can be good to restart daily, sometimes. Open the root crontab with `sudo crontab -e`
    * add this line to the bottom to restart the server at midnight `@midnight sudo reboot`

#### Running Manually
`source venv\bin\activate`
from outside the demandResponseController directory: `python demandResponseController`

### Aggregator on Windows

`venv\Scripts\activate`
`python mqtt_aggregator`

## Docs

Paho MQTT
https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
https://github.com/eclipse-paho/paho.mqtt.python?tab=readme-ov-file#usage-and-api