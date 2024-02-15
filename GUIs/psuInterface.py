import sys
import pyqtgraph as pg
import time
import datetime
import os

from lowLevelDrivers.psu import *
from lowLevelDrivers.utils import *

from pyqtgraph import GraphicsLayoutWidget
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
#from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class PlotCurrentWidget(QtWidgets.QMainWindow):
    def __init__(self, title, xlabel, ylabel, channel, psu):
        #self.init_multiple_plots(title, xlabel, ylabel, channel, psu)
        self.init_single_plot(psu)

    def init_multiple_plots(self, title, xlabel, ylabel, channel, psu):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.channel = channel
        self.psu = psu
        super().__init__()

        # Dynamic plot
        self.plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")
        self.plot_graph.setTitle(title, color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", ylabel, **styles)
        self.plot_graph.setLabel("bottom", xlabel, **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        self.time = []
        self.current = []
        # Plot line reference for current
        pen = pg.mkPen(color=(255, 0, 0))
        self.line = self.plot_graph.plot(
            self.time,
            self.current,
            name=f"Current channel {channel}",
            pen=pen,
            symbol="p",
            #symbolSize=15,
            symbolBrush="r",
        )
    
    #Plot all the currents in a single plot; plot all the voltages in a single plot
    def init_single_plot(self, psu, psu_channels=4):
        self.psu = psu
        super().__init__()

        # Dynamic plot for currents
        self.curr_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.curr_plot_graph.setBackground("w")
        self.curr_plot_graph.setTitle('Currents')
        self.curr_plot_graph.setLabel("left", 'Current (A)')
        self.curr_plot_graph.setLabel("bottom", 'Time')
        self.curr_plot_graph.addLegend(offset=(1,1))
        self.curr_plot_graph.showGrid(x=True, y=True)

        # Dynamic plot for voltages
        self.volt_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        self.setCentralWidget(self.volt_plot_graph)
        #self.volt_plot_graph.setBackground("w")
        self.volt_plot_graph.setTitle('Voltages')
        self.volt_plot_graph.setLabel("left", 'Voltage (V)')
        self.volt_plot_graph.setLabel("bottom", 'Time')
        self.volt_plot_graph.addLegend(offset=(1,1))
        self.volt_plot_graph.showGrid(x=True, y=True)

        # Dynamic plot for powers
        self.power_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.temp_plot_graph.setBackground("w")
        self.power_plot_graph.setTitle('Powers')
        self.power_plot_graph.setLabel("left", 'Power (W)')
        self.power_plot_graph.setLabel("bottom", 'Time')
        self.power_plot_graph.addLegend(offset=(1,1))
        self.power_plot_graph.showGrid(x=True, y=True)

        self.time = []
        self.current = [[], [], [], []]
        self.volts = [[], [], [], []]
        self.powers = [[], [], [], []]
        
        # Plot line reference for currents
        colormap = plt.colormaps['tab20']

        self.curr_plots = []
        self.volt_plots = []
        self.power_plots = []

        for it in range(0, psu_channels):
            curr_line = self.curr_plot_graph.plot(
                self.time,
                self.current[it],
                name=f"Current ch.{it}",
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol=symbols[it],
                #symbolBrush=colors[it],
            )
            self.curr_plots.append(curr_line)

            volt_line = self.volt_plot_graph.plot(
                self.time,
                self.volts[it],
                name=f"Voltage ch.{it}",
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol=symbols[it],
                #symbolBrush=colors[it],
            )
            self.volt_plots.append(volt_line)

            power_line = self.power_plot_graph.plot(
                self.time,
                self.powers[it],
                name=f"Power ch.{it}",
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.power_plots.append(power_line)
    
    def update_plot(self, psu, channel, ts):
        if len(self.time)<120:
            self.time.append(ts)
            self.current.append(psu.get_current(int(channel)))
        else:
            self.time = self.time[1:]
            self.time.append(ts)
            self.current = self.current[1:]
            self.current.append(psu.get_current(int(channel)))

        self.line.setData(self.time, self.current)
    
    def update_plots(self, psu, ts):
        #Discard data older than 2 hours and append time
        if len(self.time) > 120:
            self.time = self.time[1:]
        self.time.append(ts)
        #Read and append currents
        for channel in range(0, psu.channels):
            if len(self.time) > 120:
                self.current[channel] = self.current[channel][1:]
            self.current[channel].append(psu.get_current(int(channel+1)))
            self.curr_plots[channel].setData(self.time, self.current[channel])
    
    def update_currs_volts(self, ts, currs, volts):
        #Discard data older than 2 hours and append time
        if len(self.time) > 360:
            self.time = self.time[1:]
            for channel in range(0, len(currs)):
                self.current[channel] = self.current[channel][1:]
                self.volts[channel] = self.volts[channel][1:]
                self.powers[channel] =  self.powers[channel][1:]
        self.time.append(ts)
        #Plot currents and voltages
        for channel in range(0, len(currs)):
            self.current[channel].append(currs[channel])
            self.volts[channel].append(volts[channel])
            self.powers[channel].append(currs[channel]*volts[channel])
            self.curr_plots[channel].setData(self.time, self.current[channel])
            self.volt_plots[channel].setData(self.time, self.volts[channel])
            self.power_plots[channel].setData(self.time, self.powers[channel])

def update_measure(psu, widgets, logfile, psu_channels):
    ts = timestamp()
    #Acquire values
    voltages = []
    currents = []
    for it in range(psu_channels):
        voltages.append(psu.get_voltage(it+1))
        currents.append(psu.get_current(it+1))

    #Write to file
    logfile.write(str(ts))
    for it in range(psu_channels):
        logfile.write(','+str(voltages[it])+','+str(currents[it]))
    logfile.write('\n')
    logfile.flush()
    
    #Update plots
    widgets.update_currs_volts(ts, currents, voltages)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, logfile, psu_channels, timestr):
        super().__init__()
        self.setWindowTitle("Rohde&Schwarz PSU ("+str(psu_channels)+' channels)')
        self.resize(1440, 900)

        #Layouts
        layout = QtWidgets.QVBoxLayout()
        plotLayout = QtWidgets.QVBoxLayout()
        ctrlsLayout = QtWidgets.QGridLayout()
        layout.addLayout(plotLayout)
        layout.addLayout(ctrlsLayout)

        #
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        #Control widgets declarations
        #IP box
        ip_box = QtWidgets.QLineEdit()
        ip_box.setText("192.168.1.90") #FIXME: Default value to be removed?
        ip_box.setPlaceholderText("Enter IP address ...")
        
        # PSU connection type: switch to select USB or IP
        conn_type_lbl = QtWidgets.QLabel("Type:")
        conn_type_box = QtWidgets.QComboBox()
        conn_type_box.addItem("USB")
        conn_type_box.addItem("IP")
        conn_type_box.setCurrentIndex(1)

        #Buttons
        connect_btn = QtWidgets.QPushButton("Connect")
        start_btn = QtWidgets.QPushButton("Start logging")
        start_btn.setDisabled(True)
        stop_btn = QtWidgets.QPushButton("Stop logging")

        #Power supply initialization and declarations
        self.alim = None
        def connect_power_supply(logfile):
            #nonlocal alim
            ip_address = ip_box.text()

            # Try connecting to the power supply
            try:
                self.alim = PowerSupply(ip_address, conn_type_box.currentText() == "USB", psu_channels, timestr)
                self.alim.output_all_on()
                connect_btn.setDisabled(True)
                start_btn.setEnabled(True)

                # Write IDN to log file
                logfile.write('#IDN: ' + self.alim.idn() + '\n')
            except pyvisa.errors.VisaIOError:
                print("Error connecting to the power supply")
                self.alim = None
        
        #Plots widget
        widgets = []
        plot_widget = PlotCurrentWidget(f"Current", "Time", "Current (A)", 0, self.alim)
        #Add current, voltage, power plot
        widgets.append(plot_widget.curr_plot_graph)
        plotLayout.addWidget(widgets[0])
        widgets.append(plot_widget.volt_plot_graph)
        plotLayout.addWidget(widgets[1])
        widgets.append(plot_widget.power_plot_graph)
        plotLayout.addWidget(widgets[2])

        # Write column names to logfile
        logfile.write('#Time Stamp')
        for it in range(psu_channels):
            logfile.write(', Ch.'+str(it+1)+' Voltage (V), Ch.'+str(it+1)+' Current (A)')
        logfile.write('\n')


        #Buttons actions
        connect_btn.clicked.connect(lambda: connect_power_supply(logfile))
        start_btn.clicked.connect(lambda: timer.start())
        stop_btn.clicked.connect(lambda: timer.stop())

        #Controls positioning
        ctrlsLayout.addWidget(ip_box,0,0)
        ctrlsLayout.addWidget(conn_type_box,1,0)
        ctrlsLayout.addWidget(connect_btn,2,0)
        ctrlsLayout.addWidget(start_btn, 3, 0)
        ctrlsLayout.addWidget(stop_btn, 4, 0)

        for btn in range (1, psu_channels+1):
            ctrlsLayout.addLayout(self.add_ch_button(btn , str(btn)), btn-1, 1)

        timer = QtCore.QTimer()
        timer.setInterval(20000)
        timer.timeout.connect(lambda: update_measure(self.alim, plot_widget, logfile, psu_channels))

    def __del__(self):
        del self.alim

    def add_ch_button(self, num, defVal):
        #Widgets
        ch_on_btn = QtWidgets.QPushButton('CH'+str(num)+" ON")
        ch_off_btn = QtWidgets.QPushButton('CH'+str(num)+" OFF")
        ch_volt_box = QtWidgets.QLineEdit()
        ch_volt_box.setText(str(defVal))
        #ch_volt_box.setValidator(QIntValidator())
        #Layout
        chLayout = QtWidgets.QHBoxLayout()
        chLayout.addWidget(ch_on_btn)
        chLayout.addWidget(ch_off_btn)
        chLayout.addWidget(ch_volt_box)
        #Actions
        ch_on_btn.clicked.connect(lambda: self.alim.set_voltage(num, float(ch_volt_box.text())))
        ch_off_btn.clicked.connect(lambda: self.alim.set_voltage(num, 0))
        return chLayout


def main():
    if(len(sys.argv) != 2):
        print('Usage:')
        print('\tPSU_plotter <number of channels>')
        sys.exit()
    timestr = time.strftime("%Y%m%d_%H%M%S")
    psu_channels = int(sys.argv[1])
    print(psu_channels)
    
    # Check if log folder exists
    if not os.path.exists('log'):
        os.makedirs('log')

    with open('log/psu_'+ str(psu_channels) + 'ch_' + timestr + '.txt', 'w') as logfile:

        # Write header
        logfile.write('#Rohde&Schwarz PSU log file\n')
        logfile.write('#Date: ' + timestr + '\n')
        
        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindow(logfile, psu_channels, timestr)
        main_window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()