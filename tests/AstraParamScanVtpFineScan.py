import time
import numpy as np
import argparse
import os

from lowLevelDrivers.dso import dsoClass
from lowLevelDrivers.psu import psuClass

parser = argparse.ArgumentParser(description='Use R&S PSUs and HD6104 oscilloscope to perform a fine Vtp scan')
parser.add_argument('traceName',
                    help='Trace name: added to the file name string')
parser.add_argument('--path', dest='filePath', action='store',
                    default='D:\\Waveforms\\ASTRA\\extBiasScan\\',
                    help='Path where to store files in the oscilloscope. Default: D:\\Waveforms\\')
parser.add_argument('--src', dest='src', action='store',
                    default='C1',
                    help='DSO source to store. Default: C1')
parser.add_argument('--sweeps', dest='sweeps', action='store',
                    default = 1,
                    help='Number of sweeps to average')
args = parser.parse_args()

print('Storing waveforms in:\t'+args.filePath[:-1]+args.traceName)
print('Waveform to store:\t'+args.src)
print('Trace name:\t\t'+args.traceName)

out_folder = 'C:\\Users\\pgdaq04\\Python\\lab-tools\\DATA\\' + args.traceName +'\\'

if not os.path.exists(out_folder):
  os.mkdir(out_folder)
print('Out folder:\t'+out_folder)

dso = dsoClass()

#TODO Oscilloscope setup: for the moment, load the settings by hand
dso.setTriggerMode('Stopped')
dso.set_sweeps(args.src, int(args.sweeps))
dso.dso.write_vbs("app.ClearSweeps")
dso.setTriggerMode('Single')

#PSU setup
psu2030 = psuClass('ASRL3::INSTR') # 3CH power supply
psu4040 = psuClass('ASRL4::INSTR') # 4CH power supply

# List of all combinations of the parameters
stdcfg = [1, 0.465, 0.6, 0.8, 0.45] 
cfg9999 = [1, 0.085, 0.6, 0.41, 0.45]
# Vtp scan values

vtp =  np.linspace(3.6, 280, 100)/240

dso.setTriggerMode('Stopped')

# Set the parameters

psu2030.set_voltage(1, stdcfg[0])
psu2030.set_voltage(2, stdcfg[1])
psu2030.set_voltage(3, stdcfg[2])

psu4040.set_voltage(1, stdcfg[3])
psu4040.set_voltage(2, stdcfg[4])

# Wait for the voltages to settle
time.sleep(1)

for voltage in vtp:
    
  print('Voltage:\t ' + str(voltage))
  
  psu4040.set_voltage(3,voltage)
    
  # Trigger the oscilloscope
  dso.setTriggerMode('Normal')
  while dso.read_acquired_sweeps(args.src) <= int(args.sweeps):
    print('Acquiring sweep number ' + str(dso.read_acquired_sweeps(args.src)), flush=True, end="\r")
  
  # Stop triggering
  dso.setTriggerMode('Stopped')

  # Save the waveform
  saved_file = dso.saveWaveformToFile(args.filePath[:-1]+args.traceName, args.traceName, args.src)  
  #dso.fileDsoToPc(saved_file.split('"')[0], out_folder + saved_file.split('"')[0].split('\\')[-1])

  # Clear previous sweeps
  print('Clearing sweeps')
  while dso.read_acquired_sweeps(args.src) != 1:
    dso.dso.write_vbs("app.Acquisition.C1.ClearSweeps")
    dso.setTriggerMode('Single')
         
del dso, psu2030, psu4040