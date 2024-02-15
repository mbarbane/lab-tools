# lab-tools
Wrappers for all the laboratory instruments tools that I've came across, divided in packages

## Low-Level Drivers
Low-level drivers (mostly, SCPI interfaces) and utilities for the instruments

FIXME: create a basic class, inherited from all the actual instruments?

- Tektronix AFG3101 Pulser
- Lecroy HDO6104A Digital Signal Oscilloscope
- Keysight DAQ970A Data Acquisition System
- Generic PSU
- TTi QL355TP PSU

## Tests
Scripts and utilities to use the instruments and conduct tests
- Test-Pulse Scan
- Show DSO tracks
- TVAC temperature reader

## Graphical Interfaces
GUIs for the instruments and for specific tests
- TVAC temperature plotter and controller
- PSU GUI