"""
Read a log file from the DAQ970A configured for the AMS-L0 TVAC tests and plot the variables. 
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt

if(len(sys.argv) != 2):
  print('Usage:')
  print('\tTEMP_reader.py <log file (including path)>')
  sys.exit()
csvFile = sys.argv[1]

try:
  rawCsvData = pd.read_csv(csvFile, header=0, parse_dates=True, comment='#')
except FileNotFoundError:
    print(f'{csvFile} file not found.')
    sys.exit()
except pd.errors.EmptyDataError:
    print(f'No data in {csvFile}')
    sys.exit()
except pd.errors.ParserError:
    print(f'Parse error in {csvFile}')
    sys.exit()
except Exception:
    print('Error in opening {csvFile}.')
    print(Exception)
    sys.exit()

#Interpret timestamp as date/time and set it as index
rawCsvData['Timestamp'] = pd.to_datetime(rawCsvData['Timestamp'],unit='s')
rawCsvData = rawCsvData.set_index('Timestamp')
print(rawCsvData.head())

#Reorganize dataframe in strains, temperatures, and others
strains = [col for col in rawCsvData if col.startswith('strain')]
temperatures = [col for col in rawCsvData if col.startswith('pt')]
voltages = [col for col in rawCsvData if col.startswith('V')]
currents = [col for col in rawCsvData if col.startswith('I')]
powers = [col for col in rawCsvData if col.startswith('P')]

data = {
  'strain':rawCsvData[strains],
  'temperature':rawCsvData[temperatures],
  'voltage':rawCsvData[voltages],
  'current':rawCsvData[currents],
  'power':rawCsvData[powers]
}

#Plots
for key,df in data.items():
  try:
    ax = df.plot()
  except Exception:
    print(Exception)
    exit()
  ax.grid(True, axis='both', which='both', alpha=0.8, linestyle='dotted')
  ax.set_title(key+' values')
  ax.legend(ncols=15 , bbox_to_anchor=(1.1,1.2))
  if key == 'strain':
    plt.ylabel('eps')
  elif key == 'temperature':
    plt.ylabel('degC')
  elif key == 'voltage':
    plt.ylabel('V')
  elif key == 'current':
    plt.ylabel('A')
  elif key == 'power':
    plt.ylabel('W')
  plt.tight_layout()

plt.show()