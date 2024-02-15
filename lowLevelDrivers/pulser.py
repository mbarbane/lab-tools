import pyvisa
from time import sleep
import numpy as np

class pulserClass:
  """
  Wrapper for SCPI instructions for the Tektronix AFG3000 pulser.
  [Programmer Manual](https://download.tek.com/manual/AFG3000-Series-Arbitrary-Function-Generator-Programmer-EN_077074301.pdf)
  """
  
  def __init__(self):
    self.connectionStr = 'USB0::0x0699::0x0342::C021577::INSTR'
    self.connection()

  def __del__(self):
    self.p.close()
    print('Connection to the pulser closed.')

  def connection(self):
    """
    Connect to instrument
    """
    rm = pyvisa.ResourceManager()
    self.p = rm.open_resource(self.connectionStr)
    print('Connected to: '+self.p.query('*IDN?'))
  
  def setFreq(self, freq:float, unit:str):
    """
    Parameters
    ----------
    freq : float
      Frequency value
    unit : str
      Units of the frequency: Hz, kHz, MHz, ...
    """
    self.p.write(":SOUR:FREQ "+str(freq)+unit)
  
  def outEn(self, en:str):
    """
    Parameters
    ----------
    en : str
      Enable for the output: ON/OFF
    """
    self.p.write(":OUTP "+en)

  def setShape(self, shape:str):
    """
    Parameters
    ----------
    shape : str
      Shape Function: SIN, SQU, RAMP, PULS, ...
    """
    self.p.write(':SOUR:FUNC:SHAPE '+shape)
  
  def setPulseWidth(self, width:float, unit:str):
    """
    Parameters
    ----------
    width : float
      Pulse width
    unit : str
      Units of width: s, ms, ...
    """
    self.p.write(':SOUR:PULS:WIDTH '+str(width)+unit)
  
  def setVoltageHigh(self, volt:float):
    """
    Parameters
    ----------
    volt : float
      Output voltage in volts, high value
    """
    self.p.write(':SOUR:VOLT:HIGH '+str(volt))
  
  def setVoltageLow(self, volt:float):
    """
    Parameters
    ----------
    volt : float
      Output voltage in volts, low value
    """
    self.p.write(':SOUR:VOLT:LOW '+str(volt))

if __name__ == '__main__':
  tek = pulserClass()
  
  tek.setShape('PULS')
  tek.setFreq(100, 'Hz')
  tek.setPulseWidth(1, 'ms')
  
  tek.setVoltageLow(-2)
  tek.setVoltageHigh(-1.980)
  
  volts = np.linspace(-1.980,-1.8,19)
  for i in volts:
    sleep(1)
    tek.outEn('OFF')
    tek.setVoltageHigh(i)
    tek.outEn('ON')
  del tek