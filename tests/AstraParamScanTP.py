import time
import argparse

from lowLevelDrivers.dso import dsoClass
from lowLevelDrivers.psu import psuClass

parser = argparse.ArgumentParser(description='Use R&S PSUs and HD6104 oscilloscope to perform a parameter scan')
parser.add_argument('traceName',
                    help='Trace name: added to the file name string')
parser.add_argument('--path', dest='filePath', action='store',
                    default='D:\\Waveforms\\ASTRA\\extBiasScan\\VtpSCAN',
                    help='Path where to store files in the oscilloscope. Default: D:\\Waveforms\\')
parser.add_argument('--src', action='store',
                    default='C1',
                    help='DSO source to store. Default: C1')
args = parser.parse_args()

print('Storing waveforms in:\t'+args.filePath)
print('Waveform to store:\t'+args.src)
print('Trace name:\t\t'+args.traceName)

dso = dsoClass()

#TODO Oscilloscope setup: for the moment, load the settings by hand

#PSU setup
psu2030 = psuClass('ASRL3::INSTR') # 3CH power supply
psu4040 = psuClass('ASRL4::INSTR') # 4CH power supply

# List of all combinations of the parameters
combinations = [ [1, 0.044, 0.6, 0.8, 0.45], 
                 [1, 0, 0.6, 0.8, 0.45], 
                 [0.5, 0.083, 0.6, 0.8, 0.45], 
                 [0.5, 0.083, 0.6, 0.8, 0.77], 
                 [0.5, 0.083, 0.6, 0.4, 0.77], 
                 [0.5, 0.044, 0.6, 0.8, 0.45], 
                 [0.5, 0.044, 0.25, 0.8, 0.75], 
                 [0.5, 0.044, 0.25, 0.8, 0.77], 
                 [0.5, 0, 0.25, 0.8, 0.75], 
                 [0.5, 0, 0.22, 0.8, 0.45], 
                 [0.3, 0.465, 0.6, 0.39, 0.45], 
                 [0.3, 0.044, 0.6, 0.8, 0.77], 
                 [0.3, 0.044, 0.25, 0.8, 0.75], 
                 [0.3, 0.044, 0.25, 0.8, 0.77], 
                 [0.3, 0.044, 0.25, 0.8, 0.79], 
                 [0.3, 0, 0.6, 0.8, 0.75], 
                 [0.3, 0, 0.25, 0.8, 0.45], 
                 [0.3, 0, 0.25, 0.8, 0.79], 
                 [0.3, 0, 0.22, 0.8, 0.45], 
                 [0.3, 0, 0.22, 0.4, 0.77]
              ]

dso.setTriggerMode('Stopped')

# Loop over all combinations
for i in combinations:
    # Array of all the measurements
    measurements = []
    # Clear previous sweeps
    dso.dso.write_vbs("app.ClearSweeps")

    # Set the parameters
    print('Setting voltages: \n\tCH1: '+str(i[0])+' CH2: '+str(i[1])+' CH3: '+str(i[2])+' CH4: '+str(i[3])+' CH5: '+str(i[4])+':', end=' ')
    psu2030.set_voltage(1, i[0])
    psu2030.set_voltage(2, i[1])
    psu2030.set_voltage(3, i[2])

    psu4040.set_voltage(1, i[3])
    psu4040.set_voltage(2, i[4])

    # Wait for the voltages to settle
    time.sleep(1)

    for trig in range(10):
      # Trigger the oscilloscope
      dso.setTriggerMode('Single')
  
    # Stop triggering
    dso.setTriggerMode('Stopped')
    
    # Save the waveform
    dso.saveWaveformToFile(args.filePath, args.traceName, args.src)
    
del dso, psu2030, psu4040