import socket
import numpy as np

class tcpServer():
  def __init__(self, verbose = False):
    self.verbose = verbose
    self.host = ''    # Symbolic name meaning all available interfaces
    self.port = 12345   # Arbitrary non-privileged port
    # Connection Parameters
    self.kOn = False
    self.conn = -1
    self.addr = ''
    #
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.settimeout(0.2)
    self.s.bind((self.host, self.port))
    print("Server Host: ", self.host, ", Port: ", self.port)
  
  def __del__(self):
    if self.conn != -1:
      self.conn.close()
    self.host = ''
    self.kOn = False
    self.conn = -1
    self.addr = ''
    if (self.verbose): print('Server Socket deleted.')
  
  def newConnection(self):
    #New connection
    self.s.listen(1)
    print('\nWaiting for connections...')
    
    while self.conn == -1:
      try:
        self.conn, self.addr = self.s.accept()
      except socket.timeout:
        pass
      except:
        raise
    print('Connected to ', self.addr, '\n')
    self.kOn = True
  
  def connClosed(self, lenData):
    if lenData == 0:
      self.kOn = False
      print("Client closed the connection")
      #Reset connections, if any
      if self.conn != -1:
        self.conn.close()
        self.conn = -1
  
  def rx(self, msgLen):
    try:
      dataRx = self.conn.recv(msgLen)
    except socket.error:
      print("Error occurred: "+str(socket.error))
    self.connClosed(len(dataRx)) #Should it be an argument?
    return dataRx

  def myreceive(self, msgLen):
    chunks = []
    bytes_recd = 0
    while bytes_recd < msgLen:
      try:
        chunk = self.conn.recv(min(msgLen - bytes_recd, 2048))
      except socket.error:
        print("Error occurred: "+str(socket.error))
      
      if chunk == b'':
        self.connClosed(0)
        return
        #raise RuntimeError("Server Socket connection broken")
      else:
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    if (self.verbose): print('Received '+str(bytes_recd)+' byte(s)')
    return b''.join(chunks)
  
  def tx(self, msg):
    try:
      for i in range(len(msg)):
        self.conn.sendall(msg[i].tobytes("C"))
    except:
      print("Error occurred: "+str(socket.error))
      return -1
    return 0
  
  def mysend(self, msg):
    totalsent = 0
    while totalsent < len(msg):
      sent = self.conn.send(msg[totalsent:])
      if sent == 0:
        raise RuntimeError("Server Socket connection broken")
      totalsent = totalsent + sent
    if (self.verbose): print('Transmitted '+str(totalsent)+' byte(s)')
    return totalsent
  
  def listen(self):
    pktLen = 0
    while True:
      self.newConnection()
      while self.kOn:
        #Read Sync
        data = self.myreceive(5) # 5 chars word, "Hello"
        if data.decode() != "Hello": break

        #Read Length
        data = self.myreceive(1) # 1 bytes for the lenght
        pktLen = int(data.decode())
        print('Packet Length: '+str(pktLen))
        
        #Read time stamp
        data = self.myreceive(1) # 1 bytes timestamp
        print(data.decode())
        print()

        #Read data
        arr = np.ndarray(shape=(pktLen,1), dtype=int)
        #arr = self.myreceive(4)
        for i in range (pktLen):  #Receive data byte by byte
           arrElByte = self.rx(4)
           print(arrElByte)
           arrEl = np.frombuffer(arrElByte)
           arr[i] = arrEl
        print(len(arr))
        print(arr)
      self.conn.close()