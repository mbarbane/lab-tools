# lab-tools

### `pulser.py`
Partial wrapper for SCPI instructions for the Tektronix [AFG3000](https://download.tek.com/manual/AFG3000-Series-Arbitrary-Function-Generator-Programmer-EN_077074301.pdf) pulser.

Requirements: `pyvisa`, `numpy`, `time`

### `dso.py`
Partial wrapper for the [lecroyDso](https://lecroydso.readthedocs.io/en/latest/api/lecroydso.html) class.

Requirements: [`lecroydso`](https://github.com/TeledyneLeCroy/lecroydso), `time`

### `testPulseScan.py`
Performs a test pulse scan with `pulser.py` and `dso.py`

Requirements: `pulser`, `dso`, `argparse`, `numpy`, `time`