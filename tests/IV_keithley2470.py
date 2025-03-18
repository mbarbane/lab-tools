#!/usr/bin/env python3
import pyvisa
from datetime import datetime
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import sys
import signal

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
 
signal.signal(signal.SIGINT, handler)

# add help on running the script without arguments
if len(sys.argv) < 5:
    print("Usage: python3 IV_keithley2470.py <minV> <maxV> <stepV> <delay>")
    print("\tminV\tfloat\t minimum voltage in volts")
    print("\tmaxV\tfloat\t maximum voltage in volts (can be negative)")
    print("\tstepV\tfloat\t step voltage in volts")
    print("\tdelay\tfloat\t delay in seconds to stabilize the current after each step")
    sys.exit(1)

# Constants
REPETITIONS = 100   # number of repetitions to measure the current
VISA_RESOURCE = 'USB0::1510::9328::04539779::0::INSTR' # Keithley2470 from lab

# Arguments
minV = float(sys.argv[1])
maxV = float(sys.argv[2])
stepV = float(sys.argv[3])
delay = int(sys.argv[4])

if maxV < 0:
    V = np.arange(minV, maxV-0.1, -1*stepV)
else:
    V = np.arange(minV, maxV+0.1, stepV)
print(f'Performing {len(V)} steps - > {len(V)*delay} seconds')

# Open the resource and configure it
rm = pyvisa.ResourceManager()
keithley = rm.open_resource(VISA_RESOURCE)
keithley.write(':SOUR:FUNC VOLT')
keithley.write(':SOUR:VOLT:RANG 210')
keithley.write(':OUTP ON')

volt_arr = []
curr_arr = []
curr_e_arr = []

time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
with open('IV_'+ time +'.csv', 'w') as f:
    f.write('Voltage_set(V),Voltage_read(V),Current_avg(A),Current_std(A)\n')

    #open plot window
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel('Voltage (V)')
    ax.set_ylabel('Current (A)')
    #ax.set_yscale('log')
    ax.set_title('IV Curve ' + time)
    ax.grid()
    fig.set_figwidth(20)
    fig.set_figheight(15)

    for v in V:
        command = ':SOUR:VOLT '+str(v)
        print('Setting new voltage at ' + str(v) + ' V ...')
        keithley.write(command)

        # wait for current to stabilize
        for i in range(delay, 0, -1):
            print(f"\twaiting {i} s to stabilize current ...",
                  end="\r", flush=True)
            current = keithley.query(':MEAS:CURR?')
            sleep(1)
        print('\n')

        mean_curr_arr = []
        print('Measuring mean current...\n')
        for measure in range(0, REPETITIONS):
            current = keithley.query(':MEAS:CURR?')
            mean_curr_arr.append(float(current))

        mean_curr = np.mean(mean_curr_arr)
        std_curr = np.std(mean_curr_arr)
        read_volt = float(keithley.query(':MEAS:VOLT?'))

        print('Voltage: ', read_volt, ' V (Set: ', v, ' V) - Avg current ', mean_curr, ' A')
        volt_arr.append(read_volt)
        curr_arr.append(mean_curr)
        curr_e_arr.append(std_curr)

        f.write(str(v)+','+str(read_volt)+','+str(mean_curr)+','+str(std_curr)+'\n')

        # plot the IV curve
        ax.errorbar(volt_arr, curr_arr, yerr=curr_e_arr,fmt='ro')
        fig.canvas.draw()
        fig.canvas.flush_events()

    fig.savefig('IV_'+time+".png")

    #Ramp down to 0
    print('\nRAMP DOWN\n')
    for v in np.array(list(reversed(V))):
        command = ':SOUR:VOLT '+str(v)
        print('Setting ' + str(v) +'...')
        keithley.write(command)
        sleep(5)
        current = keithley.query(':MEAS:CURR?')

input('\nPress any key to exit ...')
