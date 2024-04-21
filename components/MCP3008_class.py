# A class for reading a CT sensor (with built in burden resistor) via MCP3008 ADC for Raspberry Pi
# MCP3008 code source: https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import math


class Current_Transformer:
    def __init__(self):
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO,MOSI=board.MOSI) # create SPI bus
        self.cs = digitalio.DigitalInOut(board.D5) # create the chip select
        self.mcp = MCP.MCP3008(self.spi,self.cs) # create mcp object
        self.chan0 = AnalogIn(mcp, MCP.P0) # create analog input channel on pin 0
        #self.chan1 = AnalogIn(mcp, MCP.P1)
        self.resolution = 2 ** 16 #the mcp3008 is 10 bit, but the Adafruit libary is 16 bit
        self.supplyV = 3.3
        self.adc_samples = 6000
        self.ref_ical=15
        self.ref_vcal = 1

    '''
    This Irms function comes from Open Energy Monitor user Bm2016 who based it on  EmonLib's calcIrms().
    I have simplified it a little and adapted it for use with Adafruit's MCP3008 library. 
    sources:
    * https://community.openenergymonitor.org/t/raspberry-pi-zero-current-energy-monitor-issues/6560/5
    * https://github.com/openenergymonitor/EmonLib/blob/master/EmonLib.cpp
    '''
    # Note that this function uses a CT with a built-in burden resistor
    def maxwellsIrms(self):
        NUMBER_OF_SAMPLES = self.adc_samples
        VCAL = self.ref_vcal        
        IVratio = self.ref_ical / VCAL #max rated current/ output voltage at that current
        ICAL = ref_ical #the max current of the sensor
        sumI = 0
        sampleI = self.resolution / 2 
        filteredI = 0
        #zOffset should be integrated into the filtering line in the future, not tacked on at the end...
        zOffset = 0.0215 #to determine zOffset, set to 0.0 and run program with no load. Change this to what the Irms reports when it should be 0A
        for n in range (0, self.adc_samples):
            lastSampleI = sampleI
            sampleI = self.chan0.value
            lastFilteredI = filteredI
            filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI) #not sure where this 0.996 comes from...
            sqI = filteredI * filteredI
            sumI += sqI           
            sampleI_old = sampleI    

    I_RATIO = ICAL * (self.supplyV / self.resolution)
    Irms = I_RATIO * math.sqrt(sumI / self.adc_samples)
    return Irms - zOffset

def main():
    ct = Current_Transformer()
    while True:
        print("Irms: {} Amps".format(str(ct.maxwellsIrms())))
        time.sleep(2)

if __name__ == "__main__":
    main()