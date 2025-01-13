# demandResponseController

Hardware and software for gathering data and controlling a power station for demand response aggregation

Both the aggregator and participant act as clients, sending and receiving data from the MQTT server.

## Installation Notes

Install this version of bluetti_mqtt (should be done in venv): https://www.github.com/alexnathanson/bluetti_mqtt
1) clone repository to RPi
2) From inside the repository directory run `pip install .`

## Running

### Participant

`source venv\bin\activate`
from outside the demandResponseController directory: `python demandResponseController`

### Aggregator

`venv\Scripts\activate`
`python mqtt_aggregator`

## Docs

Paho MQTT
https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
https://github.com/eclipse-paho/paho.mqtt.python?tab=readme-ov-file#usage-and-api