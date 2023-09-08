from lecroydso import LeCroyDSO, LeCroyVISA
from lecroydso.errors import DSOConnectionError, DSOIOError
from time import sleep

class dsoClass:
  """
  Wrapper for the [lecroyDso](https://lecroydso.readthedocs.io/en/latest/api/lecroydso.html) class.
  
  For VBS strings, check the `XStream Browser` software in the oscilloscope.
  `get_automation_cvar_names`, `get_automation_items`, `get_cvars_info` could help too
  """
  
  def __init__(self):
    self.connectionStr = 'USB0::0x05FF::0x1023::3566N50986::INSTR'
    self.connection()
    
  def __del__(self):
    self.dso.disconnect()
    print('Connection to the oscilloscope closed.')

  def connection(self):
    """
    Connect to instrument
    """
    try:
      self.transport = LeCroyVISA(self.connectionStr)
      self.dso = LeCroyDSO(self.transport)
      print('Connected to: '+self.dso.query('*IDN?'))
    
    except DSOConnectionError as e:
      print('ERROR: Unable to make a connection to ', self.connectionStr)
      print(e.message)
      exit(-1)

    except DSOIOError:
      print('ERROR: Failed to communicate to the instrument')
      exit(-1)

  def setTriggerMode(self,mode:str):
    """
    Parameters
    ----------
    mode : str
      Auto, Normal, Single, Stopped
    """
    self.dso.write_vbs('app.Acquisition.TriggerMode="'+mode+'"') #Auto,Normal,Single,Stopped
  
  def saveWaveformToFile(self, dir:str, title:str, source:str):
    """
    Save the waveform in binary format
    
    Parameters
    ----------
    dir : str
      Directory in which to save the files
    title : str
      Trace Title
    source : str
      Source to save: C1..C4 - F1..F8 - Z1..Z8 - M1..M4 - AllDisplayed - ...
      
    Returns
    -------
    str
      Last saved file details
    """
    #Format
    self.dso.write_vbs('app.SaveRecall.Waveform.WaveFormat="Binary"')
    self.dso.write_vbs('app.SaveRecall.Waveform.BinarySubFormat="Word"')
    #File Path+Name
    self.dso.write_vbs('app.SaveRecall.Waveform.WaveformDir="'+dir+'"')
    self.dso.write_vbs('app.SaveRecall.Waveform.TraceTitle="'+title+'"')
    #Source
    self.dso.write_vbs('app.SaveRecall.Waveform.SaveSource="'+source+'"')
    
    self.dso.write_vbs('app.SaveRecall.Waveform.SaveFile')
    self.dso.wait_opc()
    dsoAns = self.dso.query_vbs('app.SaveRecall.Waveform.LastSavedFileDetails')
    print('File written: '+dsoAns)
    return dsoAns
  
  def fileDsoToPc(self, remoteFile:str, localFile:str):
    """
    Transfer a file from the oscilloscope to the PC
    
    Parameters
    ----------
    remoteFile : str
      path+name of the source file in the oscilloscope
    localFile : str
      path+name of the destination file in the PC
      
    Returns
    -------
    bool
      True on success, False on failure
    """
    if (self.dso.transfer_file_to_pc('HDD', remoteFile, localFile)):
      return True
    else:
      print('Could not copy '+remoteFile+' to '+localFile)
      return False
 
if __name__ == '__main__':
  hd6 = dsoClass()
  hd6.setTriggerMode('Normal')
  sleep(3)
  hd6.setTriggerMode('Stopped')
  
  #hd6.saveWaveformToFile('D:\\Waveforms\\20230907\\', 'temp', 'Z1')
  del hd6