import tcp.tcpClient as tC
import numpy as np

tcpClt = tC.tcpClient("localhost", 12345, True)

bytessent = tcpClt.tx('Hello'.encode())

data = [0, 1, 2, 3]
#data = 'ciao'

#Lenght
tcpClt.tx(str(len(data)).encode())

#Timestamp
tcpClt.tx(str(len(data)).encode())

#Data
dataStr = ''.join(str(it) for it in data)
tcpClt.tx(dataStr.encode())
#for i in range(len(data)):
#    tcpClt.tx(data)

del tcpClt
