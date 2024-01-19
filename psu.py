import pyvisa
from utils import timestamp

class PowerSupply:
  """
  Partial wrapper for the low-level interface for a SCPI-controlled power supply, with multiple channels.
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
  
  def __init__(self, instr_string: str, usb: bool, ch: int= 4, timestr: str= ''):
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
    self.logger = open('log/psu_tc_'+ str(ch) + 'ch_' + timestr + '.txt', 'w')
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
        self.resource = rm.open_resource(f"TCPIP::{self.instr_string}::INSTR")
      else:
        self.resource = rm.open_resource(f"{self.instr_string}") # FIXME: not sure this is the right syntax when using USB
      print(f"Connected to power supply at {self.instr_string}")
      self.log(f"Connected to TCPIP::{self.instr_string}::INSTR")
    except pyvisa.errors.VisaIOError as e:
      print(f"Failed to connect to power supply: {e}")
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
      print("Disconnected from power supply")
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')
  
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
      raise pyvisa.errors.VisaIOError('PSU not connected')
 
  def set_voltage(self, ch:int, voltage:float):
    """
    Set voltage of a single channel
    
    Parameters
    ----------
    ch : int
      Addressed channel
    voltage : float
      Voltage value to set
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      #self.resource.write(f'INST:SEL {ch}')
      self.resource.write(f'INST OUT{ch}')
      self.resource.write(f"VOLT {voltage}")
      #self.log(f'INST:SEL {ch} VOLT {voltage}')
      self.log(f'INST OUT{ch} VOLT {voltage}')
      print(f"Set voltage to {voltage} V for channel {ch}")
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')
 
  def set_current(self, ch: int, current: float):
    """
    Set current of a single channel
    
    Parameters
    ----------
    ch : int
      Addressed channel
    current : float
      Current value to set
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      #self.resource.write(f'INST:SEL {ch}')
      self.resource.write(f'INST OUT{ch}')
      self.resource.write(f"CURR {current}")
      #self.log(f'INST:SEL {ch} CURR {current}')
      self.log(f'INST OUT{ch} CURR {current}')
      print(f"Set current to {current} A")
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')

  def output_on(self, ch: int):
    """
    Enable the output of a single channel
    
    Parameters
    ----------
    ch : int
      Addressed channel
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      #self.resource.write(f'INST:SEL {ch}')
      self.resource.write(f'INST OUT{ch}')
      self.resource.write("OUTP ON")
      #self.log(f'INST:SEL {ch} OUTP ON')
      self.log(f'INST OUT{ch} OUTP ON')
      print("Output turned ON")
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')
  
  def output_off(self, ch: int):
    """
    Disable the output of a single channel
    
    Parameters
    ----------
    ch : int
      Addressed channel
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      #self.resource.write(f'INST:SEL {ch}')
      self.resource.write(f'INST OUT{ch}')
      self.resource.write("OUTP OFF")
      #self.log(f'INST:SEL {ch} OUTP OFF')
      self.log(f'INST OUT{ch} OUTP OFF')
      print("Output turned OFF")
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')

  def output_all_on(self):
    """
    Enable the output of all the channels
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      for ch in range(1, self.channels+1):
        self.set_voltage(ch, 0)
        self.output_on(ch)
      print("All Channels Output ON")
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')

  def output_all_off(self):
    """
    Disable the output of all the channels
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      for ch in range(1, self.channels+1):
        self.output_off(ch)
      print("All Channels Output OFF")
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')

  def get_current(self, ch: int):
    """
    Read current value of a single channel
    
    Parameters
    ----------
    ch : int
      Addressed channel
    
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
      #self.resource.write(f'INST:SEL {ch}')
      self.resource.write(f'INST OUT{ch}')
      #self.log(f'INST:SEL {ch} query(:meas:curr?)')
      self.log(f'INST OUT{ch} query(MEAS:CURR?)')
      return float(self.resource.query("MEAS:CURR?"))
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')

  def get_voltage(self, ch):
    """
    Read voltage value of a single channel
    
    Parameters
    ----------
    ch : int
      Addressed channel
    
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
      #self.resource.write(f'INST:SEL {ch}')
      self.resource.write(f'INST OUT{ch}')
      voltage = self.resource.query("MEAS:VOLT?")
      #self.log(f'INST:SEL {ch} query(MEAS:VOLT?)')
      self.log(f'INST OUT{ch} query(MEAS:VOLT?)')
      return float(voltage)
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')
 
  def get_power(self, ch):
    """
    Read power value of a single channel.
    Not all the PSUs support this: if not, use the compute_power function
    
    Parameters
    ----------
    ch : int
      Addressed channel
    
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
      #self.resource.write(f'INST:SEL {ch}')
      self.resource.write(f'INST OUT{ch}')
      current = self.resource.query("MEAS:POW?")
      #self.log(f'INST:SEL {ch} query(MEAS:POW?)')
      self.log(f'INST OUT{ch} query(MEAS:POW?)')
      return float(current)
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')
  
  def compute_power(self, ch):
    """
    Compute power value of a single channel from the current and voltage readings
    
    Parameters
    ----------
    ch : int
      Addressed channel
    
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
      curr = self.get_current(ch)
      volt = self.get_voltage(ch)
      return curr * volt
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')
  
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
    for it in range(self.channels):
      retStr += (',V'+str(it))
      retStr += (',I'+str(it))
      retStr += (',P'+str(it))
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
    for it in range(self.channels):
      unitStr += (',V')
      unitStr += (',A')
      unitStr += (',W')
    return unitStr