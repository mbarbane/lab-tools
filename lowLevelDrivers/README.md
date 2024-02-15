# Low-Level Drivers
Low-level drivers (mostly, SCPI interfaces) and utilities for the instruments

## `utils.py`
Container for utilities needed around the code.

Requirements: `time`, `datetime`, `pyqtgraph`

## `pulser.py`
Partial wrapper for SCPI instructions for the Tektronix [AFG3000](https://download.tek.com/manual/AFG3000-Series-Arbitrary-Function-Generator-Programmer-EN_077074301.pdf) pulser.

Requirements: `pyvisa`, `numpy`, `time`

## `dso.py`
Partial wrapper for the [lecroyDso](https://lecroydso.readthedocs.io/en/latest/api/lecroydso.html) class.

Requirements: [`lecroydso`](https://github.com/TeledyneLeCroy/lecroydso), `time`

## `daq970a.py`
Partial wrapper for the  low-level interface for the [keysight DAQ970A SCPI commands](https://www.keysight.com/us/en/assets/9018-04756/programming-guides/9018-04756.pdf).
The config used here is very specific for the TVAC tests for the AMS-L0 upgrade. Update the configuration before other usage.

Includes the generic class `daq970a`, and a AMSL0-TVAC specific class `qlcsTvacDaq970`

Requirements: `pyvisa`, `re`, `os`, `sys`, `errno`, `numpy`, `utils`

## `psu.py`
Partial wrapper for the low-level interface for a SCPI-controlled power supply, with multiple channels.

Requirements: `pyvisa`, `utils`

## `ql355tp.py`
Wrapper for QL355TP PSU serial instructions. Inherits from the generic class and overrides a subset of the commands.

Requirements: `pyvisa`, `utils`