# Tests
Scripts and utilities to use the instruments and conduct tests

## `testPulseScan.py`
Performs a test pulse scan with `pulser.py` and `dso.py`

Requirements: `pulser`, `dso`, `argparse`, `numpy`, `time`

## `TEMP_reader.py`
Read a log file from the DAQ970A configured for the AMS-L0 TVAC tests and plot the variables. 

Requirements: `sys`, `pandas`, `matplotlib.pyplot`

## `dsoShowTrack.py`
Show a track acquired with the dso class.

Requirements: `numpy`, `matplotlib.pyplot`, `lecroyparses`, `sys`

## ASTRA tests

### `AstraParamScan.py`
Scan voltage parameters for the ASTRA characterization

Requirements: `psu`, `dso`, `time`, `statistics`, `argparse`, `itertools`

### `AstraParamScanTP.py`
Scan voltage parameters for the ASTRA characterization + test-pulse

Requirements: `psu`, `dso`, `time`, `argparse`

### `AstraParamScanVtpFineScan.py`
Scan voltage parameters for the ASTRA characterization + test-pulse with fine steps

Requirements: `psu`, `dso`, `numpy`, `time`, `argparse`, `os`