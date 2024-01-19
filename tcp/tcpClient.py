import socket

class tcpClient():
  def __init__(self, host, port, verbose = False):
    self.verbose = verbose
    #self.host = socket.gethostname()
    self.host = "localhost"
    self.port = 12345 # The same port as used by the server
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.newConnection(host, port)
    if (verbose): print('Client Socket '+str(self.s)+' created.')
  
  def __del__(self):
    self.s.close()
    if (self.verbose): print('Client Socket deleted.')

  def newConnection(self, host, port):
    self.s.connect((host, port))
    if (self.verbose): print('Client Socket connected to '+str(host)+' - '+str(port))
  
  def rx(self, msgLen):
    chunks = []
    bytes_recd = 0
    while bytes_recd < msgLen:
      chunk = self.s.recv(min(msgLen - bytes_recd, 2048))
      if chunk == b'':
        raise RuntimeError("Client Socket connection broken")
      chunks.append(chunk)
      bytes_recd = bytes_recd + len(chunk)
    if (self.verbose): print('Received '+str(bytes_recd)+' byte(s)')
    return b''.join(chunks)

  def tx(self, msg):
    totalsent = 0
    while totalsent < len(msg):
      sent = self.s.send(msg[totalsent:])
      if sent == 0:
        raise RuntimeError("Client Socket connection broken")
      totalsent = totalsent + sent
    if (self.verbose): print('Transmitted '+str(totalsent)+' byte(s)')
    return totalsent
