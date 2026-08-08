import socket
import time
import tkinter as tk

HOST = "amspgdaq04.dyndns.cern.ch" # ip or hostname of DAQ PC
PORT = 10000

def startC():
    date = int(time.time() + time.localtime().tm_gmtoff)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = bytes.fromhex('FF800008'+'00150000'+'EE000001'+hex(date)[2:])
        s.sendall(msg)

def startM():
    date = int(time.time() + time.localtime().tm_gmtoff)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = bytes.fromhex('FF800008'+'00150001'+'EE000001'+hex(date)[2:])
        s.sendall(msg)

def startB():
    date = int(time.time() + time.localtime().tm_gmtoff)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = bytes.fromhex('FF800008'+'00150002'+'EE000001'+hex(date)[2:])
        s.sendall(msg)

def stop():
    date = int(time.time() + time.localtime().tm_gmtoff)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = bytes.fromhex('FF800008'+'00150001'+'EE000000'+hex(date)[2:])
        s.sendall(msg)

window = tk.Tk()
window.title('PAPERO DAQ')
window.columnconfigure(0, minsize=250)
window.rowconfigure([0, 1, 2, 3], minsize=150)

btn_startC = tk.Button(text="startOCA CALIB", command=startC)
btn_startM = tk.Button(text="startOCA MIX", command=startM)
btn_startB = tk.Button(text="startOCA BEAM", command=startB)
btn_stop = tk.Button(text="stopOCA", command=stop)

btn_startC.grid(row=0, column=0, sticky="nsew")
btn_startM.grid(row=1, column=0, sticky="nsew")
btn_startB.grid(row=2, column=0, sticky="nsew")
btn_stop.grid(row=3, column=0, sticky="nsew")

window.mainloop()
