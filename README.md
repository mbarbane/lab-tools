# lab-tools

---
## Low-Level Interfaces (SCPI)
FIXME: create a basic class, inherited from all the actual instruments?

### `utils.py`
Container for utilities needed around the code.

Requirements: `time`, `datetime`, `pyqtgraph`

### `pulser.py`
Partial wrapper for SCPI instructions for the Tektronix [AFG3000](https://download.tek.com/manual/AFG3000-Series-Arbitrary-Function-Generator-Programmer-EN_077074301.pdf) pulser.

Requirements: `pyvisa`, `numpy`, `time`

### `dso.py`
Partial wrapper for the [lecroyDso](https://lecroydso.readthedocs.io/en/latest/api/lecroydso.html) class.

Requirements: [`lecroydso`](https://github.com/TeledyneLeCroy/lecroydso), `time`

### `daq970a.py`
Partial wrapper for the  low-level interface for the [keysight DAQ970A SCPI commands](https://www.keysight.com/us/en/assets/9018-04756/programming-guides/9018-04756.pdf).
The config used here is very specific for the TVAC tests for the AMS-L0 upgrade. Update the configuration before other usage.

Includes the generic class `daq970a`, and a AMSL0-TVAC specific class `qlcsTvacDaq970`

Requirements: `pyvisa`, `re`, `os`, `sys`, `errno`, `numpy`, `utils`

### `psu.py`
Partial wrapper for the low-level interface for a SCPI-controlled power supply, with multiple channels.

Requirements: `pyvisa`, `utils`


---
## Tests and Graphical Interfaces


### `testPulseScan.py`
Performs a test pulse scan with `pulser.py` and `dso.py`

Requirements: `pulser`, `dso`, `argparse`, `numpy`, `time`

### `TEMP_reader.py`
Read a log file from the DAQ970A configured for the AMS-L0 TVAC tests and plot the variables. 

Requirements: `sys`, `pandas`, `matplotlib.pyplot`

### `TEMP_plotter.py`
GUI for the PSU and DAQ970A for the AMS-L0 TVAC tests.
Includes also the temperature control with a two-thresholds algorithm.

Requirements: `sys`, `pyqtgraph`, `time`, `datetime`, `psu`, `utils`, `daq970a`, `PyQt5`, `matplotlib`

### `psuInterface.py`
GUI for a generic PSU.

Requirements: `sys`, `pyqtgraph`, `time`, `datetime`, `os`, `psu`, `utils`, `PyQt5`, `matplotlib`