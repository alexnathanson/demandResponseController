
'''
# MCP3008 code sourced  https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx
# EmonLib's calcIrms() function sources:https://github.com/openenergymonitor/EmonLib/blob/master/EmonLib.cpp)
* https://community.openenergymonitor.org/t/raspberry-pi-zero-current-energy-monitor-issues/6560/5
* https://www.engineersgarage.com/non-invasive-current-sensor-with-arduino/
'''
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import math

#create SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO,MOSI=board.MOSI)

#create the chip select
cs = digitalio.DigitalInOut(board.D5)

# create mcp object
mcp = MCP.MCP3008(spi,cs)

# create analog input channel
number_of_ct = 1  # the number of sensors (they should start at pin 0)
chan0 = AnalogIn(mcp, MCP.P0)
#chan1 = AnalogIn(mcp, MCP.P1)

RESOLUTION = 2 ** 16 #the mcp3008 is 10 bit, but the Adafruit libary is 16 bit
SUPPLYVOLTAGE = 3.3
# =======================================================================================================
# source https://community.openenergymonitor.org/t/raspberry-pi-zero-current-energy-monitor-issues/6560/5
# auth: Maxwell (Bm2016) 
# adapted for Adafruit MCP3008 library by Alex Nathanson 
#built-in burden resistor
def maxwellsIrms(adc_samples = 6000, ref_ical=15, ref_vcal = 1):
    NUMBER_OF_SAMPLES = adc_samples
    #Vsupply = SUPPLYVOLTAGE * 1000 ## 3300=3.3v 5000=5.0v
    IVratio = ref_ical / ref_vcal #max rated current/ output voltage at that current
    ICAL = ref_ical #the max current of the sensor
    sumI = 0
    sampleI = RESOLUTION / 2 
    filteredI = 0
    zOffset = .057
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
    #sumI = 0
    return Irms - zOffset
# end of Maxwell's RMS calculation
# =======================================================================================================

def calcIrms_greyCT():
    sampleNum = 6000
    supplyV = 3.3
    burden = 78
    maxI = 30
    Iratio = maxI/.015
    ICAL = Iratio/burden
    maxV = .015 * burden
    #print(maxV)
    ampsToV = maxV / maxI
    sumI =0
    sixteenbit = 2 ** 16
    print('raw: ' + str(chan0.voltage))
    offsetI = supplyV / 2
    for n in range (0, sampleNum):
        #lastSampleI = sampleI
        sampleI = chan0.voltage
        #print(sampleI)
        #lastFilteredI = filteredI
        offsetI = (offsetI + ((sampleI - offsetI) / supplyV))
        filteredI = sampleI - offsetI
        #filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI)
        sqI = filteredI * filteredI
        sumI += sqI
    I_RATIO = 100* ICAL * ampsToV
    Irms = I_RATIO * math.sqrt(sumI/sampleNum)
    #sumI = 0
    return Irms

#run this when CT isn't attached to anything and should read as 0
def calibrate():
    vIdeal = SUPPLYVOLTAGE / 2
    vOff = 0
    samples = 6000
    for i in range(0,samples):
       vD = vIdeal - chan0.voltage
       vOff += (vD * vD)

    vOff = math.sqrt(vOff)/samples

    print("Offset when reading at 0 amps: {}V".format(vOff))
    # print("%")
    # perOff = vOff / offsetI
    # print(1 - perOff)


def main():
    while True:
        print("Irms: {} Amps".format(str(maxwellsIrms())))
        time.sleep(2)


if __name__ == "__main__":
    main()