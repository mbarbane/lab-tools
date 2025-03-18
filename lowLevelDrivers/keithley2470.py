#!/usr/bin/env python3
import pyvisa
from lowLevelDrivers.utils import timestamp

class keithley2470:
  """
  Partial wrapper for the low-level interface for a SCPI-controlled Keithley 2470.
  FIXME: create a basic class, inherited from all the actual instruments?
  
  Attributes
  ----------
  channels: int
    number of channels of the power-supply unit
  instr_string: str
    string containing the USB name or IP address of the instrument
  usb: bool
    '1': instrument connected with USB, '0': instrument connected with IP address
  resource: Resource
    handle to the instrument, when connection open; None otherwise
  logger: file
    handle of the file log
  """
  
  def __init__(self, instr_string: str='USB0::1510::9328::04539779::0::INSTR',
               usb: bool=True, ch: int= 1, timestr: str= ''):
    """
    Parameters
    ----------
    instr_string: str
      string containing the USB name or IP address of the instrument
    usb: bool
      '1': instrument connected with USB, '0': instrument connected with IP address
    ch: int, optional
      number of channels of the power-supply unit; default: 4
    timestr: str, optional
      Timestamp to append to the log file; default: ''
    """
    self.channels = ch
    self.instr_string = instr_string
    self.usb = usb
    self.resource = None
    self.logger = open('log/k2470_tc_'+ timestr + '.txt', 'w')
    self.connect()
  
  def __del__(self):
    self.disconnect()
    self.logger.close()

  def connect(self):
    """
    Connect to instrument
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Failed the connection to the instrument
    Re-raise other exceptions
    """
    try:
      rm = pyvisa.ResourceManager()
      if not self.usb:
        self.resource = rm.open_resource(f"TCPIP::{self.instr_string}::INSTR") # FIXME: never used with TCPIP
      else:
        self.resource = rm.open_resource(f"{self.instr_string}")
      print(f"Connected to Keithley 2470  at {self.instr_string}")
      self.log(f"Connected to {self.instr_string}")
    except pyvisa.errors.VisaIOError as e:
      print(f"Failed to connect to Keithley 2470: {e}")
      self.resource = None
      raise e
  
  def initialize(self):
    """
    Initialize to most common function and limits
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Failed the connection to the instrument
    Re-raise other exceptions
    """
    try:
      self.resource.write(':SOUR:FUNC VOLT')
      self.resource.write(':SOUR:VOLT:RANG 210')
      self.log(f"Set to :SOUR:FUNC VOLT and :SOUR:VOLT:RANG 210")
    except pyvisa.errors.VisaIOError as e:
      print(f"Failed to connect to Keithley 2470: {e}")
      self.resource = None
      raise e
 
  def disconnect(self):
    """
    Safely disconnect from instrument
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument already disconnected
    """
    if self.resource:
      self.resource.close()
      self.resource = None
      print("Disconnected from Keithley 2470")
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')
  
  def close(self):
    """
    Disconnect from the instrument after stopping query in progress (if any)
    """
    self.disconnect()

  def idn(self):
    """
    Return the identity string of the instrument
    
    Returns
    -------
    str
      Identification string of the instrument
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      return self.resource.query("*IDN?")
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')
 
  def set_voltage(self, voltage:float):
    """
    Set voltage in output
    
    Parameters
    ----------
    voltage : float
      Voltage value to set
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      self.resource.write(f":SOUR:VOLT {voltage}")
      self.log(f':SOUR:VOLT {voltage}')
      print(f"Set voltage to {voltage} V")
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')
 
  def set_current(self, current: float):
    """
    Set current of a single channel
    
    Parameters
    ----------
    current : float
      Current value to set
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      self.resource.write(f":SOUR:CURR {current}")
      self.log(f':SOUR:CURR {current}')
      print(f"Set current to {current} A")
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')

  def output_on(self):
    """
    Enable the output of a single channel
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      self.resource.write("OUTP ON")
      self.log('OUTP ON')
      print("Output turned ON")
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')
  
  def output_off(self):
    """
    Disable the output of a single channel
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      self.resource.write("OUTP OFF")
      self.log('OUTP OFF')
      print("Output turned OFF")
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')

  def get_current(self):
    """
    Read current value
    
    Returns
    -------
    float
      Measured current
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      curr = self.resource.query(':MEAS:CURR?')
      self.log('query(:MEAS:CURR?)')
      return float(curr)
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')

  def get_voltage(self):
    """
    Read voltage value
    
    Returns
    -------
    float
      Measured voltage
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      volt = self.resource.query(':MEAS:VOLT?')
      self.log('query(:MEAS:VOLT?)')
      return float(volt)
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')
 
  def get_power(self):
    """
    Read power value.
    Not sure if 2470 supports this: if not, use the compute_power function
    
    Returns
    -------
    float
      Measured power
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      pow = self.resource.query(':MEAS:POW?')
      self.log('query(:MEAS:POW?)')
      return float(pow)
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')
  
  def compute_power(self):
    """
    Compute power value of a single channel from the current and voltage readings
    
    Returns
    -------
    float
      Computed power (current x voltage)
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      curr = self.get_current()
      volt = self.get_voltage()
      return curr * volt
    else:
      raise pyvisa.errors.VisaIOError('Keithley 2470 not connected')
  
  def log(self, txt: str):
    """
    Append a time-stamped line to the log
    
    Parameters
    ----------
    txt : str
      Line to append after the timestamp
    """
    ts = timestamp()
    self.logger.write(str(ts)+','+txt+'\n')
    self.logger.flush()

  def csvHeader(self):
    """
    Write the header to the CSV file to match the log lines that will come after
    
    Returns
    -------
    str
      Header string of the CSV file
    """
    retStr = ""
    return retStr
  
  def csvUnits(self):
    """
    Define the units of each measurement
    
    Returns
    -------
    str
      String of the units of the measurements, ordered as read from the instrument
    """
    unitStr = ''
    return unitStr