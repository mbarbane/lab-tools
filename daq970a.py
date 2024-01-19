import pyvisa
import re
import os, sys
import errno
from utils import timestamp
import numpy as np

class daq970a:
  """
  Wrapper low-level interface for the [keysight DAQ970A SCPI commands](https://www.keysight.com/us/en/assets/9018-04756/programming-guides/9018-04756.pdf).
  The config used here is very specific for the TVAC tests for the AMS-L0 upgrade.
  Update the configuration before other usage.
  
  Attributes
  ----------
  instr_string: str
    string containing the USB name or IP address of the instrument
  usb: bool
    '1': instrument connected with USB, '0': instrument connected with IP address
  resource: Resource
    handle to the instrument, when connection open; None otherwise
  logger: file
    handle of the file log
  no_err: Pattern[str]
    String returned from the instrument when reading errors and buffer is empty
  timeout: int
    timeout of the instrument, in milliseconds
  """
  
  def __init__(self, instr_string: str, usb: bool, timestr: str= ''):
    """
    Parameters
    ----------
    instr_string: str
      string containing the USB name or IP address of the instrument
    usb: bool
      '1': instrument connected with USB, '0': instrument connected with IP address
    timestr: str, optional
      Timestamp to append to the log file; default: ''
    """
    self.no_err = re.compile(r'^\+?0')
    self.instr_string = instr_string
    self.usb = usb
    self.resource = None
    self.timeout = 55000 #5 seconds less than the readout period, to have enough time to start a new readout
    
    self.logger = None
    #Make directory (if not already existing)
    #os.makedirs(os.path.dirname('log'), exist_ok=True)
    try:
      self.logger = open('log/daq970a_tc_' + timestr + '.txt', 'w')
    except OSError:
      print("Could not open log file")
      sys.exit()
  
  def __del__(self):
    self.disconnect()
  
  def updateConnection(self, instr_string: str, usb: bool):
    """
    Update the parameters for the connection and try to re-connect
    
    Parameters
    ----------
    instr_string : str
      IP Address or SCPI string to connect to the daq
    usb : bool
      '1': USB connection; '0': IP connection
    
    Raises
    ------
    Re-raise the exceptions from sub-functions
    """
    self.instr_string = instr_string
    self.usb = usb

    try:
      self.connect()
      self.config()
    except:
      raise
  
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
        self.resource = rm.open_resource(f"{self.instr_string}")
    except pyvisa.errors.VisaIOError as e:
      print(f"Failed to connect to Keysight DAQ970A: {e}")
      self.resource = None
      raise e
    except:
      raise
    
    if self.resource != None:
      self.reset()
      self.emptyErrorBuffer()
      print('\n'.join(self.resource.query('*IDN?').split(',')))
      self.log('\n'.join(self.resource.query('*IDN?').split(',')))
  
  def disconnect(self):
    """
    Safely disconnect from instrument
    """
    if self.resource:
      self.emptyErrorBuffer()
      self.resource.close()
      self.resource = None
      self.log('Disconnected from Keysight DAQ970A')
      print("Disconnected from Keysight DAQ970A")
  
  def emptyErrorBuffer(self):
    """
    Read and print all the errors from the buffer.
    Errors can occur during the acquisitions or at the startup.
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      err = True
      while(err):
        ret_err = self.resource.query('SYST:ERROR?')
        if re.match(self.no_err, ret_err):
          print('No (more) errors: '+ret_err)
          err = False
        else:
          print('Error: '+ret_err)
      self.stop_query()
    else:
      raise pyvisa.errors.VisaIOError('DAQ970A not connected')
  
  def config(self):
    """
    Configure the instrument with the predefined configuration.
    FIXME: Pass the configuration
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      self.resource.write('CONF:TEMP:RTD 1000,(@101:120)')
      self.resource.write('CONF:TEMP:RTD 1000,(@201:205,207:220)')
      self.resource.write('CONF:TEMP:RTD 1000,(@315:319)')
      self.resource.write('CONF:STR:DIR 120,2,(@301:309,311:314)')
      
      self.resource.write('TEMP:APER 200E-3')
      self.resource.write('STR:APER 200E-3')

      self.resource.write('ROUT:SCAN (@101:120,201:205,207:220,301:309,311:314,315:319)')
      self.resource.write('TRIG:COUN 1')
      
      self.resource.timeout = self.timeout
      
      #self.resource.write('INIT')
    else:
      raise pyvisa.errors.VisaIOError('DAQ970A not connected')
  
  def customCommand(self, cmdStr: str):
    """
    Send a SCPI command to the instrument
    
    Parameters
    ----------
    cmdStr : str
      SCPI string of the command
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      self.resource.write(cmdStr)
    else:
      raise pyvisa.errors.VisaIOError('DAQ970A not connected')
  
  def query(self):
    """
    Read all the data from the instrument
    
    Returns
    -------
    dataRead: float array
      Numpy array with the answer of the instrument
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      dataRead = self.resource.query('READ?').split(',')
      dataRead = np.asarray(dataRead, dtype=float)
      return dataRead
    else:
      raise pyvisa.errors.VisaIOError('DAQ970A not connected')
    
  def customQuery(self, queryStr: str):
    """
    Read a generic data from the instrument
    
    Parameters
    ----------
    queryStr : str
      SCPI string of the query
    
    Returns
    -------
    dataRead: str
      Answer of the instrument to the query
    
    Raises
    ------
    pyvisa.errors.VisaIOError
      Instrument unavailable or not connected
    """
    if self.resource:
      dataRead = self.resource.query(queryStr)
      return dataRead
    else:
      raise pyvisa.errors.VisaIOError('DAQ970A not connected')
  
  def stop_query(self):
    """
    Abort the query in progress
    """
    self.resource.write('ABOR')

  def reset(self):
    """
    Abort the query in progress and reset the instrument
    """
    print('Resetting...')
    self.resource.write('RST')

  def close(self):
    """
    Disconnect from the instrument after stopping query in progress (if any)
    """
    self.stop_query()
    self.disconnect()
  
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


class qlcsTvacDaq970(daq970a):
  """
  Specific class for the AMS-L0 QLCS TVAC tests that extends the daq970a class.
  
  Attributes
  ----------
  instr_string: str
    string containing the USB name or IP address of the instrument
  usb: bool
    '1': instrument connected with USB, '0': instrument connected with IP address
  resource: Resource
    handle to the instrument, when connection open; None otherwise
  logger: file
    handle of the file log
  no_err: Pattern[str]
    String returned from the instrument when reading errors and buffer is empty
  timeout: int
    timeout of the instrument, in milliseconds
  chDict: dict
    Relates each channel to the type of measure and plane
  map: list
    Used channels with corresponding name
  nameDict: dict
    Relate the channel to the sensor used
  lenDict: dict
    Number of sensors used for each type of measure/plane
  planeDict: dict
    Sensors in each type/plane, in the same order of the readout
  """
  
  def __init__(self, instr_string: str, usb: bool, timestr: str= ''):
    """
    Initializes the super class and defines the specific attributes
    
    Parameters
    ----------
    instr_string: str
      string containing the USB name or IP address of the instrument
    usb: bool
      '1': instrument connected with USB, '0': instrument connected with IP address
    timestr: str, optional
      Timestamp to append to the log file; default: ''
    """
    super().__init__(instr_string, usb, timestr)
    self.connectionDefinition()
  
  def connectionDefinition(self):
    """
    Map the DAQ970A channels to the test sensors.
    """
    self.chDict = {
      '101': 'y',
      '102': 'y',
      '103': 'y',
      '104': 'y',
      '105': 'ext',
      '106': 'y',
      '107': 'y',
      '108': 'y',
      '109': 'y',
      '110': 'y',
      '111': 'y',
      '112': 'y',
      '113': 'y',
      '114': 'y',
      '115': 'y',
      '116': 'y',
      '117': 'y',
      '118': 'y',
      '119': 'y',
      '120': 'y',
      '201': 'u',
      '202': 'u',
      '203': 'u',
      '204': 'u',
      '205': 'u',
      #'206': 'u',
      '207': 'u',
      '208': 'u',
      '209': 'u',
      '210': 'ext',
      '211': 'u',
      '212': 'u',
      '213': 'u',
      '214': 'u',
      '215': 'u',
      '216': 'u',
      '217': 'u',
      '218': 'ext',
      '219': 'u',
      '220': 'ext',
      '301': 'strain',
      '302': 'strain',
      '303': 'strain',
      '304': 'strain',
      '305': 'strain',
      '306': 'strain',
      '307': 'strain',
      '308': 'strain',
      '309': 'strain',
      '311': 'strain',
      '312': 'strain',
      '313': 'strain',
      '314': 'strain',
      '315': 'ext',
      '316': 'ext',
      '317': 'p1s',
      '318': 'p1s',
      '319': 'p1s'
    }
    self.map = [
      '101', '102', '103', '104', '105', '106', '107', '108', '109', '110',
      '111', '112', '113', '114', '115', '116', '117', '118', '119', '120',
      '201', '202', '203', '204', '205',  '207', '208', '209', '210',
      '211', '212', '213', '214', '215', '216', '217', '218', '219', '220',
      '301', '302', '303', '304', '305', '306', '307', '308', '309',
      '311', '312', '313', '314', '315', '316', '317', '318', '319'
    ]
    self.nameDict = {
      '101': 'pt01',
      '102': 'pt02',
      '103': 'pt03',
      '104': 'pt04',
      '105': 'pt05',
      '106': 'pt06',
      '107': 'pt07',
      '108': 'pt08',
      '109': 'pt09',
      '110': 'pt10',
      '111': 'pt11',
      '112': 'pt12',
      '113': 'pt13',
      '114': 'pt14',
      '115': 'pt15',
      '116': 'pt16',
      '117': 'pt17',
      '118': 'pt18',
      '119': 'pt19',
      '120': 'pt20',
      '201': 'pt21',
      '202': 'pt22',
      '203': 'pt23',
      '204': 'pt24',
      '205': 'pt25',
      #'206': 'pt26',
      '207': 'pt27',
      '208': 'pt28',
      '209': 'pt29',
      '210': 'pt30',
      '211': 'pt31',
      '212': 'pt32',
      '213': 'pt33',
      '214': 'pt34',
      '215': 'pt35',
      '216': 'pt36',
      '217': 'pt37',
      '218': 'pt38',
      '219': 'pt39',
      '220': 'pt40',
      '301': 'strain01',
      '302': 'strain02',
      '303': 'strain03',
      '304': 'strain04',
      '305': 'strain05',
      '306': 'strain06',
      '307': 'strain07',
      '308': 'strain08',
      '309': 'strain09',
      '311': 'strain10',
      '312': 'strain11',
      '313': 'strain12',
      '314': 'strain13',
      '315': 'pt41',
      '316': 'pt42',
      '317': 'pt43',
      '318': 'pt44',
      '319': 'pt45'
    }

    self.lenDict = dict(u=0, y=0, ext=0, p1s=0, strain=0)
    self.planeDict = dict(u=[], y=[], ext=[], p1s=[], strain=[])
    for name,val in self.chDict.items():
      self.lenDict[val] += 1
      self.planeDict[val].append(name)

  def csvHeader(self):
    """
    Write the header to the CSV file to match the log lines that will come after
    
    Returns
    -------
    str
      Header string of the CSV file
    """
    retStr = ''
    for it in range(self.lenDict['u']):
      retStr += ','+self.nameDict[self.planeDict['u'][it]]
    for it in range(self.lenDict['y']):
      retStr += ','+self.nameDict[self.planeDict['y'][it]]
    for it in range(self.lenDict['ext']):
      retStr += ','+self.nameDict[self.planeDict['ext'][it]]
    for it in range(self.lenDict['p1s']):
      retStr += ','+self.nameDict[self.planeDict['p1s'][it]]
    for it in range(self.lenDict['strain']):
      retStr += ','+self.nameDict[self.planeDict['strain'][it]]
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
    for idx,val in enumerate(self.map):
      if self.chDict[str(val)] == 'strain':
        unitStr += ',eps'
      else:
        unitStr += ',degC'
    return unitStr
    
  def query(self):
    """
    Overloading query function to read all the measurements and order them as needed
    
    Returns
    -------
    dict
      Instrument readout, ordered in a dictionary
    
    Raises
    ------
    Generic exceptions
    """
    retDict = dict(u=[], y=[], ext=[], p1s=[], strain=[])
    try:
      unorderedData = super().query()
      for idx,val in enumerate(unorderedData):
        retDict[self.chDict[str(self.map[idx])]].append(val)
      return retDict
    except:
      raise