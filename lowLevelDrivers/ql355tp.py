import pyvisa
from lowLevelDrivers.psu import PowerSupply

class ql355tpPsu(PowerSupply):
  """
  Wrapper for QL355TP PSU Serial instructions.
  Inherits from the generic class and overrides a subset of the commands.
  """
  
  def __init__(self, instr_string: str, usb: bool= True, ch: int= 2, timestr: str= ''):
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
    super().__init__(instr_string, usb, ch, timestr)
    self.logger = open('log/ql355_tc_'+ str(ch) + 'ch_' + timestr + '.txt', 'w')
  
  def get_voltage(self, ch:int):
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
      self.resource.write('V'+str(ch)+'O?')
      self.log('V'+str(ch)+'O?')
      out_str = self.resource.read()
      return float(out_str.rstrip()[:-1])
      #voltage = self.resource.query('V'+str(ch)+'O?')
      #self.log('V'+str(ch)+'O?')
      #return float(voltage)
    else:
      raise pyvisa.errors.VisaIOError('QL355TP not connected')

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
      self.resource.write('I'+str(ch)+'O?')
      self.log('I'+str(ch)+'O?')
      out_str = self.resource.read()
      return float(out_str.rstrip()[:-1])
      #self.resource.write(f'INST OUT{ch}')
      #self.log(f'INST OUT{ch} query(MEAS:CURR?)')
      #return float(self.resource.query("MEAS:CURR?"))
    else:
      raise pyvisa.errors.VisaIOError('PSU not connected')
