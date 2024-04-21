
'''
# MCP3008 code sourced  https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx
# Irms calculation function based on:
# EmonLib's calcIrms() function sources:
* https://github.com/openenergymonitor/EmonLib/blob/master/EmonLib.cpp)
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

'''
# MCP
mcp3008_bits = 10
#while the mcp3008 is 10 bit, this library returns data in 16 bit when calling value!
mcp3008_resolution = 2**10 #1024
value_resolution = 2 ** 16
mcp3008_voltage = 3.3 #operating voltage

#CT & circuit
# CT data sheet: https://cdn.sparkfun.com/datasheets/Sensors/Current/ECS1030-L72-SPEC.pdf
burden_ohms = 78 #burden resistor ohms
ct_Irating = 30.0 # CT rated amps
ct_turns = 2000
ct_output =  .015 # A output of CT @ 30amps
ct_maxV = ct_output * burden_ohms
ct_supplyV = mcp3008_voltage / 2
ct_offset   = ct_supplyV
ct_ratio = ct_Irating / ct_output
ct_cal =  ct_ratio / burden_ohms # callibration = ratio / burden ohms
print('current callibation constant:')
print(ct_cal)

mains_V = 110 # voltage of mains

adc_samples  = 6000    # kinda arbitrary - figure out what doesn't bog down the RPi

ref_voltage  = 3.3    # 3300=3.3v 5000=5.0v i.e. operating V * 1000
ref_I     = 30.0    #clamp sensor rating
ref_Iratio = ref_I / .015 
ref_sampleI  = value_resolution / 2


values = [0]*number_of_ct
ct     = [0]*number_of_ct
array  = [0]*adc_samples
rms    = [0]*number_of_ct
'''

#################################
# sampleNum = 1000
# supplyV = 3.3
# burder = 75
# primaryCoil = 30
# secondaryCoil = .015
# offsetI = supplyV / 2

# =======================================================================================================
# source https://community.openenergymonitor.org/t/raspberry-pi-zero-current-energy-monitor-issues/6560/5
# auth: Maxwell (Bm2016) 
# adapted for MCP3008 library by Alex Nathanson 
def maxwellsIrms(adc_samples = 6000, ref_voltage = 3300, ref_ical=15):
    NUMBER_OF_SAMPLES = adc_samples
    SUPPLYVOLTAGE = ref_voltage ## 3300=3.3v 5000=5.0v
    ICAL = ref_ical
    sumI = 0
    resolution = 2 ** 16
    sampleI = resolution / 2 
    filteredI = 0
    zOffset = .057
    for n in range (0, NUMBER_OF_SAMPLES):
        lastSampleI = sampleI
        sampleI = chan0.value
        ## for debug only, print all 6000 values read from MCP3008 ch0
        # if i == 0:
        #      print(sampleI, end='') 
        #      print(' ',end='')
        ## end of debug
        lastFilteredI = filteredI
        filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI)
        sqI = filteredI * filteredI
        sumI += sqI           
        sampleI_old = sampleI    

    I_RATIO = ICAL * ((SUPPLYVOLTAGE/1000.0) / resolution)
    Irms = I_RATIO * math.sqrt(sumI / NUMBER_OF_SAMPLES)
    #sumI = 0
    return Irms - zOffset
# end of Maxwell's RMS calculation
# =======================================================================================================

#built-in burden resistor
def calcIrms_blueCT():
    print('BLUE CT')
    sampleNum = 6000
    supplyV = 3.3
    #burden = 78
    maxI = 15
    Iratio = maxI/.015
    ICAL = maxI
    maxV = (1/15) * 61 #.015 * burden
    ampsToV = maxV / maxI
    sumI =0
    #print('raw: ' + str(chan0.voltage))
    offsetI = supplyV / 2
    sampleI =offsetI
    filteredI = 0
    for n in range (0, sampleNum):
        lastSampleI = sampleI
        lastFilteredI = filteredI

        sampleI = chan0.voltage

        if(n==0):
            print('raw: ' + str(sampleI))

        offsetI = (offsetI + ((sampleI - offsetI) / supplyV))
        filteredI = sampleI - offsetI
        #filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI)
        sqI = filteredI * filteredI
        sumI += sqI
    I_RATIO = ICAL * ampsToV
    Irms = I_RATIO * math.sqrt(sumI/sampleNum)
    #sumI = 0
    return Irms

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
    vOff = 0
    for i in range(0,sampleNum):
       vOff += abs(offsetI - chan0.voltage)

    vOff = vOff/sampleNum

    print("Voltage offset when reading at 0 amps:")
    print(vOff)
    print("%")
    perOff = vOff / offsetI
    print(1 - perOff)

#calibrate()

while True:
    #for i in range(number_of_ct):
        #ct[i] = round(calcIrms(values[i]),2)
        #print(round(calcIrms(ct_offset,ct_supplyV,ct_cal,value_resolution),4))

        # print('Raw | {0:>4} | {1:>4} |'.format(*values), end='')
        # print('AMP | {0:>4} | {1:>4} |'.format(*rms))
    print("Irms: " + str(calcIrms_blueCT()))
    time.sleep(2)
