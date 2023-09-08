from dso import dsoClass
from pulser import pulserClass
from time import sleep
import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Use Tektronix pulser and HD6104 oscilloscope to perform a test-pulse scan')
parser.add_argument('traceName',
                    help='Trace name: added to the file name string')
parser.add_argument('--path', dest='filePath', action='store',
                    default='D:\\Waveforms\\',
                    help='Path where to store files in the oscilloscope. Default: D:\\Waveforms\\')
parser.add_argument('--src', action='store',
                    default='Z1',
                    help='DSO source to store. Default: Z1')
args = parser.parse_args()

print('Storing waveforms in:\t'+args.filePath)
print('Waveform to store:\t'+args.src)
print('Trace name:\t\t'+args.traceName)

dso = dsoClass()
pulser = pulserClass()

#Pulser setup: 100 Hz, 1 ms wide, starting from -2V
pulser.setShape('PULS')
pulser.setFreq(100, 'Hz')
pulser.setPulseWidth(1, 'ms')

#Voltage sequence for the High value
pulseHighEnd = np.append(np.linspace(-1.980,-1.8,19), np.linspace(-1.7, 0, 18))
pulseHighEnd = np.append(pulseHighEnd, np.linspace(0.1, 1.5, 15))
pulser.setVoltageHigh(-1.980)

#Voltage for the Low value (fixed)
pulseLowEnd=-2
print('Setting Low End to '+f'{pulseLowEnd:1.3f}'+' V')
pulser.setVoltageLow(pulseLowEnd)

#TODO Oscilloscope setup: for the moment, load the settings by hand


#Test loop

##Set first voltage in the list
pulser.setVoltageHigh(pulseHighEnd[0])
pulser.outEn('ON')

for it in pulseHighEnd:
  #Set and apply voltage
  pulser.setVoltageHigh(it)
  print('High End: '+f'{it:1.3f}'+' V - Pulse height: '+f'{(it-pulseLowEnd):1.3f}'+' V')
  
  #DSO acquisition
  dso.setTriggerMode('Normal')
  
  #Wait the DSO to be ready
  sleep(10)
  
  #Stop DSO and save waveform
  dso.setTriggerMode('Stopped')
  dso.saveWaveformToFile(args.filePath, args.traceName, args.src)


#Turn off everything
pulser.outEn('OFF')
dso.setTriggerMode('Stopped')

del dso, pulser
