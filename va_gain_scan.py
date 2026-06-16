"""
Move TCT motors (with libximc) and control Tektronix AFG3101 (for trigger) and HEF DAQ (via MAKA/OCA) to scan a detector with laser beam
"""

import time
import os
import sys
import socket
import subprocess

###########################################
# TCT motors control
###########################################

try:
    import libximc.highlevel as ximc # type: ignore
    print("Use libximc {} that has been found among the pip installed packages".format(ximc.ximc_version()))
except ImportError:
    print("Warning! libximc cannot be found among the pip installed packages. Did you forget to install it via pip?\n"
          "Trying to import the library using relative path: ../../../ximc/crossplatform/wrappers/python ...")
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    ximc_dir = os.path.join(cur_dir, "..", "..", "..", "ximc")
    ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
    sys.path.append(ximc_package_dir)
    import libximc.highlevel as ximc # type: ignore
    print("Success!")


def status(axis: ximc.Axis) -> None:
    print("\nGet status")
    status = axis.get_status()
    print("Status.Ipwr: {}".format(status.Ipwr))
    print("Status.Upwr: {}".format(status.Upwr))
    print("Status.Iusb: {}".format(status.Iusb))
    print("Status.Flags: {}".format(status.Flags))

def get_position(axis: ximc.Axis) -> 'tuple':
    print("\nRead position")
    pos = axis.get_position()
    print("Position: {0} steps, {1} microsteps".format(pos.Position, pos.uPosition))
    return pos.Position, pos.uPosition

def move(axis: ximc.Axis, distance: int, udistance: int) -> None:
    print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
    axis.command_move(distance, udistance)

def wait_for_stop(axis: ximc.Axis, interval: int) -> None:
    print("\nWaiting for stop...")
    axis.command_wait_for_stop(interval)

def set_microstep_mode_256(axis: ximc.Axis) -> None:
    print("\nSet microstep mode to 256")
    engine_settings = axis.get_engine_settings()
    engine_settings.MicrostepMode = ximc.MicrostepMode.MICROSTEP_MODE_FRAC_256

    axis.set_engine_settings(engine_settings)

###########################################
# TCT laser driver control
###########################################

API_EXE = r"F:\Downloads\PaLaser-C_API_V1.0\PaLaser.exe"

def set_laser_high_intensity():
    subprocess.run([API_EXE, '-p', '66'], check=True)

def set_laser_low_intensity():
    subprocess.run([API_EXE, '-p', '2904'], check=True)


###########################################
# DAQ control
###########################################

HOST = "192.168.1.22"
PORT = 10000

def startB(runnum):
    print("\tStarting DAQ")
    date = int(time.time())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(bytes.fromhex('FF800008'+(hex(runnum)[2:].zfill(4))+'0002'+'EE000001'+hex(date)[2:]))
        s.close()

def stop():
    print("\tStopping DAQ")
    date = int(time.time())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(bytes.fromhex('FF800008' + '00150001' + 'EE000000' + hex(date)[2:]))
        s.shutdown(socket.SHUT_WR)
        while s.recv(4096): # Blocking, until command is actually processed
            pass
        s.close()


# ******************************************** #
#          libximc device searching            #
# ******************************************** #
enum_flags = ximc.EnumerateFlags.ENUMERATE_PROBE | ximc.EnumerateFlags.ENUMERATE_NETWORK

enum_hints = "addr="
devenum = ximc.enumerate_devices(enum_flags, enum_hints)
print("Device count: {}".format(len(devenum)))
print("Found devices:\n", devenum)

if len(devenum) == 0:
    print("The real controller is not found or busy with another app.")
    exit()


x_axis_uri = r"xi-com:\\.\COM4"
y_axis_uri = r"xi-com:\\.\COM5"

# ******************************************** #
#              Create axis objects             #
# ******************************************** #
x_axis = ximc.Axis(x_axis_uri)
print("\nOpen device " + x_axis.uri)
x_axis.open_device()  # The connection must be opened manually
set_microstep_mode_256(x_axis)

y_axis = ximc.Axis(y_axis_uri)
print("\nOpen device " + y_axis.uri)
y_axis.open_device()  # The connection must be opened manually
set_microstep_mode_256(y_axis)

# ******************************************** #
#                  Points loop                 #
# ******************************************** #
n_VA = 14

# Looking at HEF from connector side ...
#start_pos = -27200 # Left HEF
x_start_pos = 10600 # Right HEF
x_ustart_pos = 0
x_scan_pitch = -200 # 400 steps equal 1mm
status(x_axis)
get_position(x_axis)

y_start_pos_top = 7260 # Top Si
y_start_pos_bot = 32280 # Bottom Si
y_ustart_pos = 0
status(y_axis)
get_position(y_axis)

def points_loop(VAs, high_laser_intensity, silicon):
    if high_laser_intensity:
        set_laser_high_intensity()
    else:
        set_laser_low_intensity()
    
    if silicon == 0:
        move(y_axis, y_start_pos_bot, y_ustart_pos)
        wait_for_stop(y_axis, 2)
    else:
        move(y_axis, y_start_pos_top, y_ustart_pos)
        wait_for_stop(y_axis, 2)

    move(x_axis, x_start_pos, x_ustart_pos)
    wait_for_stop(x_axis, 2)

    for step in range(VAs):
        print("VA: ", step)

        for point in range(6):
            print("\tPoint: ", point)

            if point != 0:
                # Move to next point
                x_current_pos, x_ucurrent_pos = get_position(x_axis)
                move(x_axis, x_current_pos + x_scan_pitch, x_ucurrent_pos)
                wait_for_stop(x_axis, 2)

            startB((6 * step) + point) # Start DAQ with external trigger
            time.sleep(12) # Take some data
            stop() # Stop DAQ
        
        # Move to next VA
        x_current_pos, x_ucurrent_pos = get_position(x_axis)
        move(x_axis, x_current_pos - 1760, x_ucurrent_pos)
        wait_for_stop(x_axis, 2)

# First scan with high intensity laser
stop() # Send stop DAQ command to make sure we are ready
#points_loop(n_VA, True, 0)
points_loop(n_VA, True, 1)

# Second scan with low intensity laser
stop() # Send stop DAQ command to make sure we are ready
points_loop(n_VA, False, 0)
points_loop(n_VA, False, 1)

