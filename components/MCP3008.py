# A script for reading a CT sensor (with built in burden resistor) via MCP3008 ADC for Raspberry Pi

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import math

# ===========================================================================================================
# MCP3008 code source: https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx
#create SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO,MOSI=board.MOSI)
#create the chip select
cs = digitalio.DigitalInOut(board.D5)
# create mcp object
mcp = MCP.MCP3008(spi,cs)
# ===========================================================================================================

# create analog input channel
chan0 = AnalogIn(mcp, MCP.P0) #pin 0
#chan1 = AnalogIn(mcp, MCP.P1)

RESOLUTION = 2 ** 16 #the mcp3008 is 10 bit, but the Adafruit libary is 16 bit
SUPPLYVOLTAGE = 3.3

# =======================================================================================================
'''
This Irms function comes from Open Energy Monitor user Bm2016 who based it on  EmonLib's calcIrms().
I have simplified it a little and adapted it for use with Adafruit's MCP3008 library. 
sources:
* https://community.openenergymonitor.org/t/raspberry-pi-zero-current-energy-monitor-issues/6560/5
* https://github.com/openenergymonitor/EmonLib/blob/master/EmonLib.cpp
'''
# Note that this function uses a CT with a built-in burden resistor
def maxwellsIrms(adc_samples = 6000, ref_ical=15, ref_vcal = 1):
    NUMBER_OF_SAMPLES = adc_samples
    #Vsupply = SUPPLYVOLTAGE * 1000 ## 3300=3.3v 5000=5.0v
    VCAL = ref_vcal        
    IVratio = ref_ical / VCAL #max rated current/ output voltage at that current
    ICAL = ref_ical #the max current of the sensor
    sumI = 0
    sampleI = RESOLUTION / 2 
    filteredI = 0
    zOffset = 0.059 #to determine zOffset, set to 0.0 and run program with no load. Change this to what the Irms reports when it should be 0A
    for n in range (0, NUMBER_OF_SAMPLES):
        lastSampleI = sampleI
        sampleI = chan0.value
        lastFilteredI = filteredI
        filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI) #not sure where this 0.996 comes from...
        sqI = filteredI * filteredI
        sumI += sqI           
        sampleI_old = sampleI    

    I_RATIO = ICAL * (SUPPLYVOLTAGE / RESOLUTION)
    Irms = I_RATIO * math.sqrt(sumI / NUMBER_OF_SAMPLES)
    return Irms - zOffset
# end of Maxwell's RMS calculation
# =======================================================================================================

def main():
    while True:
        print("Irms: {} Amps".format(str(maxwellsIrms())))
        time.sleep(2)

if __name__ == "__main__":
    main()