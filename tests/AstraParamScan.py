import time
from statistics import mean
import argparse
import itertools

from lowLevelDrivers.dso import dsoClass
from lowLevelDrivers.psu import psuClass

parser = argparse.ArgumentParser(description='Use R&S PSUs and HD6104 oscilloscope to perform a parameter scan')
parser.add_argument('traceName',
                    help='Trace name: added to the file name string')
parser.add_argument('--path', dest='filePath', action='store',
                    default='D:\\Waveforms\\ASTRA\\extBiasScan\\Vtp0700_BLH_L_AVG',
                    help='Path where to store files in the oscilloscope. Default: D:\\Waveforms\\')
parser.add_argument('--meas_path', dest='measPath', action='store',
                    default='C:\\Users\\pgdaq04\\Python\\lab-tools\\',
                    help='Path where to store measurements in the PC. Default: C:\\Users\\pgdaq04\\Python\\lab-tools\\')
parser.add_argument('--src', action='store',
                    default='C1',
                    help='DSO source to store. Default: C1')
args = parser.parse_args()

print('Storing waveforms in:\t'+args.filePath)
print('Storing measurements in:\t'+args.measPath)
print('Waveform to store:\t'+args.src)
print('Trace name:\t\t'+args.traceName)

def log(f, psu2030, psu4040, meas):
  f.write(str(int(time.time())))
  f.write(', '+str(psu2030.get_voltage(1)[:-1]))
  f.write(', '+str(psu2030.get_voltage(2)[:-1]))
  f.write(', '+str(psu2030.get_voltage(3)[:-1]))
  f.write(', '+str(psu4040.get_voltage(1)[:-1]))
  f.write(', '+str(psu4040.get_voltage(2)[:-1]))
  
  for m in meas:
    f.write(', %f, %f, %f' % (m[0],m[1],m[2]))
  f.write('\n')
  f.flush()

dso = dsoClass()

#TODO Oscilloscope setup: for the moment, load the settings by hand

#PSU setup
psu2030 = psuClass('ASRL3::INSTR') # 3CH power supply
psu4040 = psuClass('ASRL4::INSTR') # 4CH power supply

# List of voltages to test for each parameter (LOW, NOMINAL, HIGH) in Volts
CSA_Vcasn2 = [1.0, 0.5, 0.3, 0.1]
#CSA_Vcasp  = [0.48, 0.7, 0.715, 0.730, 0.1, 0.04, 0.02]
CSA_Vcasp  = [0.465, 0.734, 0.754, 0.774, 0.083, 0.044, 0.0] #0.48, 0.7, 0.715, 0.730, 0.15, 0.1, 0.06
SH1_Vcasn  = [0.6, 0.25, 0.22, 0.20]
SH2_Vcasn  = [0.8, 0.4, 0.39, 0.387]
SH1_Vcasp  = [0.45, 0.75, 0.77, 0.79]

# List of all combinations of the parameters
combinations = list(itertools.product(CSA_Vcasn2, CSA_Vcasp, SH1_Vcasn, SH2_Vcasn, SH1_Vcasp))

readMeas = False

# Create file and then append
f = open(args.traceName+'.csv', 'w')
f.close()
f = open(args.traceName+'.csv', 'a')
f.write('#time,CSA_Vcasn2,CSA_Vcasp,SH1_Vcasn,SH2_Vcasn,SH1_Vcasp')
if (readMeas):
  for ch in range(8):
    eq = dso.readMeasurementName(ch+1)
    f.write(f',mean ({eq}),sdev ({eq}),status ({eq})')
f.write('\n')

dso.setTriggerMode('Stopped')
dso.dso.write_vbs("app.ClearSweeps")

# Loop over all combinations
for i in combinations:
    # Set the parameters
    print('Combination '+str(combinations.index(i)+1)+'/'+str(len(combinations)))
    print('\tSetting voltages: \n\tCH1: '+str(i[0])+' CH2: '+str(i[1])+' CH3: '+str(i[2])+' CH4: '+str(i[3])+' CH5: '+str(i[4])+':', end=' ')
    psu2030.set_voltage(1, i[0])
    psu2030.set_voltage(2, i[1])
    psu2030.set_voltage(3, i[2])

    psu4040.set_voltage(1, i[3])
    psu4040.set_voltage(2, i[4])

    # Wait for the voltages to settle
    time.sleep(1)

    if (readMeas):
      # Number of sweeps to average
      num = 10
      # Array of all the measurements
      measurements = []
      
      # Clear previous sweeps
      dso.dso.write_vbs("app.ClearSweeps")
      # Trigger the oscilloscope
      dso.setTriggerMode('Normal')

      # Wait for all measurements to have enough sweeps
      while dso.readMinSweep(1,5) < num:
        print(dso.readMinSweep(1,8), end=" ", flush=True)
      print(" ")

      # Stop triggering
      dso.setTriggerMode('Stopped')

      # Query the oscilloscope for the average of the measurements
      for it in range(8):
        try:
          mean = dso.readMeasurementMean(it+1)
          sdev = dso.readMeasurementSdev(it+1)
          status = dso.readMeasurementStatus(it+1)
          measurements.append([mean, sdev, status])
        except Exception as e:
          print(str(e)+str(it))
          continue

      # Save the waveform
      dso.saveWaveformToFile(args.filePath, args.traceName, args.src)

      # Save the measurements
      log(f, psu2030, psu4040, measurements)
    
    else:
      # Trigger the oscilloscope
      dso.setTriggerMode('Normal')
      
      # Wait for the average curve
      # 100 Hz trigger -> 1 s; 2 s for contingency
      time.sleep(2)
      
      # Save the waveform and log the number
      dso.saveWaveformToFile(args.filePath, args.traceName, args.src)
      log(f, psu2030, psu4040, '')
      
  
f.close()
del dso, psu2030, psu4040