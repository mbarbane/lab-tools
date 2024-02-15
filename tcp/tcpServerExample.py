import tcp.tcpServer as tS
import numpy as np
import signal
import sys

tcpSrv = tS.tcpServer(True)
#tcpSrv.listen()

#Catch Ctrl+C to stop listening
def sig_handler(sig, frame):
  run = False
  sys.exit(0)
signal.signal(signal.SIGINT, sig_handler)

pktLen = 0
run = True
while run:
  tcpSrv.newConnection()
  while tcpSrv.kOn:
    #Read Sync
    data = tcpSrv.myreceive(5) # 5 chars word, "Hello"
    if data == None:
      continue
    if data.decode() != "Hello": break
    
    #Read Length
    data = tcpSrv.myreceive(1) # 1 bytes for the lenght
    pktLen = int(data.decode())
    print('Packet Length: '+str(pktLen))
  
    #Read time stamp
    data = tcpSrv.myreceive(1) # 1 bytes timestamp
    print(data.decode())

    #Read data
    arr = np.ndarray(shape=(pktLen,1), dtype=int)
    arr = tcpSrv.myreceive(4)
    #for i in range (pktLen):  #Receive data byte by byte
    #  arrElByte = tcpSrv.rx(4)
    #  print(arrElByte)
    #  arrEl = np.frombuffer(arrElByte)
    #  arr[i] = arrEl
    print('Length '+str(len(arr)))
    print('Array:')
    print(arr)

del tcpSrv