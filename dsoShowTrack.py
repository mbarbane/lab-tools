#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import lecroyparser
import sys


plt.rc('font', size=12)

plt.figure(0, figsize=(11, 7))
filePath = sys.argv[1]
print(filePath)
trk = lecroyparser.ScopeData(filePath)
trk.x = trk.x * 1000000
plt.plot(trk.x, trk.y, label='IDE1140 Out')

plt.legend(loc='upper right')
plt.title('IDE1140 output [V]')
plt.ylabel('IDE1140 output [V]')
plt.xlabel('Time [us]')
#plt.ylim(-.4, 2.5)
#plt.xticks(np.linspace(0,45,10))
#plt.xlim(trk.x[0]-20, trk.x[-1]+20)
plt.grid(True, axis='x', alpha=0.8, linestyle='dotted')
plt.tight_layout()

plt.show()