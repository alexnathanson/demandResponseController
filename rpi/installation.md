#Installation

## Hardware

### Calculating burden resistor for current transformers (CT) sensor
source: https://docs.openenergymonitor.org/electricity-monitoring/ct-sensors/interface-with-arduino.html

#### 30A CT
sensor datasheet: https://cdn.sparkfun.com/datasheets/Sensors/Current/ECS1030-L72-SPEC.pdf
Primary peak-current = RMS current × √2 = 30 A × 1.414 = 42.42A
Secondary peak-current = Primary peak-current / no. of turns = 42.42 A / 2000 = 0.02121A
Ideal burden resistance = (AREF/2) / Secondary peak-current = 1.65 V / 0.02121A = 77.8 Ω (@3.3V)

## Software
### Install the required libraries
`sudo pip install adafruit-circuit-python-ina219`
