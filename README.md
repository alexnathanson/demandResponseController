# demandResponseController

Hardware and software for gathering data and controlling a power station for demand response aggregation

## Installation Notes

Install this version of bluetti_mqtt (should be done in venv): https://www.github.com/alexnathanson/bluetti_mqtt
1) clone repository to RPi
2) From inside the repository directory run `pip install .`

## Running

### Participant

from outside the demandResponseController directory: `python demandResponseController`

### Aggregator

`python mqtt_aggregator`