import sys
import pyqtgraph as pg
import time
import datetime

from psu import *
from utils import *
from daq970a import *

from pyqtgraph import GraphicsLayoutWidget
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class PlotTempWidget(QtWidgets.QMainWindow):
    def __init__(self, title, xlabel, ylabel, channel, psu):
        self.psu = psu
        self.init_single_plot()
        self.name = "PlotTempWidget"
    
    #Plot several channels in the same plot
    def init_single_plot(self):
        super().__init__()

        psu_channelsU = self.psu.lenDict['u']
        psu_channelsY = self.psu.lenDict['y']
        psu_channelsEXT = self.psu.lenDict['ext']
        psu_channelsP1S = self.psu.lenDict['p1s']

        # Dynamic plot for temperatures U
        self.temp_U_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.temp_plot_graph.setBackground("w")
        self.temp_U_plot_graph.setTitle('Temperatures U')
        self.temp_U_plot_graph.setLabel("left", 'Temperatures (°C)')
        self.temp_U_plot_graph.setLabel("bottom", 'Time')
        self.temp_U_plot_graph.addLegend(offset=(1,1)) 
        self.temp_U_plot_graph.showGrid(x=True, y=True)

        # Dynamic plot for temperatures Y
        self.temp_Y_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.temp_plot_graph.setBackground("w")
        self.temp_Y_plot_graph.setTitle('Temperatures Y')
        self.temp_Y_plot_graph.setLabel("left", 'Temperatures (°C)')
        self.temp_Y_plot_graph.setLabel("bottom", 'Time')
        self.temp_Y_plot_graph.addLegend(offset=(1,1))
        self.temp_Y_plot_graph.showGrid(x=True, y=True)

        # Dynamic plot for temperatures EXT
        self.temp_EXT_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.temp_plot_graph.setBackground("w")
        self.temp_EXT_plot_graph.setTitle('Temperatures EXT')
        self.temp_EXT_plot_graph.setLabel("left", 'Temperatures (°C)')
        self.temp_EXT_plot_graph.setLabel("bottom", 'Time')
        self.temp_EXT_plot_graph.addLegend(offset=(1,1))
        self.temp_EXT_plot_graph.showGrid(x=True, y=True)

        # Dynamic plot for temperatures P1S
        self.temp_P1S_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.temp_plot_graph.setBackground("w")
        self.temp_P1S_plot_graph.setTitle('Temperatures P1S')
        self.temp_P1S_plot_graph.setLabel("left", 'Temperatures (°C)')
        self.temp_P1S_plot_graph.setLabel("bottom", 'Time')
        self.temp_P1S_plot_graph.addLegend(offset=(1,1))
        self.temp_P1S_plot_graph.showGrid(x=True, y=True)

        self.time = []
        
        # Empty list of lists for temperatures
        self.temperaturesU = []
        self.temperaturesY = []
        self.temperaturesEXT = []
        self.temperaturesP1S = []

        for it in range(0, psu_channelsU):
            self.temperaturesU.append([])

        for it in range(0, psu_channelsY):
            self.temperaturesY.append([])

        for it in range(0, psu_channelsEXT):
            self.temperaturesEXT.append([])

        for it in range(0, psu_channelsP1S):
            self.temperaturesP1S.append([])


        # Plot line reference for currents
        colormap = plt.colormaps['tab20']

        self.temp_U_plots = []
        self.temp_Y_plots = []
        self.temp_EXT_plots = []
        self.temp_P1S_plots = []

        for it in range(0, psu_channelsU):
            temp_Uline = self.temp_U_plot_graph.plot(
                self.time,
                self.temperaturesU[it],
                #name = f"Temperature ch.{it}",
                name = self.psu.nameDict[self.psu.planeDict['u'][it]],
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.temp_U_plots.append(temp_Uline)
            
        for it in range(0, psu_channelsY):
            temp_Yline = self.temp_Y_plot_graph.plot(
                self.time,
                self.temperaturesY[it],
                #name=f"Temperature ch.{it}",
                name = self.psu.nameDict[self.psu.planeDict['y'][it]],
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.temp_Y_plots.append(temp_Yline)

        for it in range(0, psu_channelsEXT):
            temp_EXTline = self.temp_EXT_plot_graph.plot(
                self.time,
                self.temperaturesEXT[it],
                #name=f"Temperature ch.{it}",
                name = self.psu.nameDict[self.psu.planeDict['ext'][it]],
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.temp_EXT_plots.append(temp_EXTline)

        for it in range(0, psu_channelsP1S):
            temp_P1Sline = self.temp_P1S_plot_graph.plot(
                self.time,
                self.temperaturesP1S[it],
                #name=f"Temperature ch.{it}",
                name = self.psu.nameDict[self.psu.planeDict['p1s'][it]],
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.temp_P1S_plots.append(temp_P1Sline)
    
    def update_temps(self, ts, tempsU, tempsY, tempsEXT, tempsP1S):
        #Discard data older than 2 hours and append time
        if len(self.time) > 120:
            self.time = self.time[1:]
            for channel in range(0, len(tempsU)):
                self.temperaturesU[channel] = self.temperaturesU[channel][1:]
            for channel in range(0, len(tempsY)):
                self.temperaturesY[channel] = self.temperaturesY[channel][1:]
            for channel in range(0, len(tempsEXT)):
                self.temperaturesEXT[channel] = self.temperaturesEXT[channel][1:]
            for channel in range(0, len(tempsP1S)):
                self.temperaturesP1S[channel] = self.temperaturesP1S[channel][1:]
        self.time.append(ts)
        #Plot all temperatures
        for channel in range(0, len(tempsU)):
            self.temperaturesU[channel].append(tempsU[channel])
            self.temp_U_plots[channel].setData(self.time, self.temperaturesU[channel])

        for channel in range(0, len(tempsY)):
            self.temperaturesY[channel].append(tempsY[channel])
            self.temp_Y_plots[channel].setData(self.time, self.temperaturesY[channel])
            self.temp_Y_plots[channel].setData(self.time, self.temperaturesY[channel])

        for channel in range(0, len(tempsEXT)):
            self.temperaturesEXT[channel].append(tempsEXT[channel])
            self.temp_EXT_plots[channel].setData(self.time, self.temperaturesEXT[channel])

        for channel in range(0, len(tempsP1S)):
            self.temperaturesP1S[channel].append(tempsP1S[channel])
            self.temp_P1S_plots[channel].setData(self.time, self.temperaturesP1S[channel])
    
    def update_currs_volts_pwrs(self, ts, currs, volts, pwrs):
        pass
    
            
class PlotPSUWidget(QtWidgets.QMainWindow):
    def __init__(self, title, xlabel, ylabel, channel, psu):
        self.psu = psu
        self.init_single_plot(psuChannels=4)
        self.name = "PsuTempWidget"
    
    #Plot several channels in the same plot
    def init_single_plot(self, psuChannels=3):
        super().__init__()

        # Dynamic plot for voltages
        self.volt_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.temp_plot_graph.setBackground("w")
        self.volt_plot_graph.setTitle('Voltages')
        self.volt_plot_graph.setLabel("left", 'Volt (V)')
        self.volt_plot_graph.setLabel("bottom", 'Time')
        self.volt_plot_graph.addLegend(offset=(1,1))
        self.volt_plot_graph.showGrid(x=True, y=True)

        # Dynamic plot for currents
        self.curr_plot_graph = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        #self.temp_plot_graph.setBackground("w")
        self.curr_plot_graph.setTitle('Currents')
        self.curr_plot_graph.setLabel("left", 'Current (A)')
        self.curr_plot_graph.setLabel("bottom", 'Time')
        self.curr_plot_graph.addLegend(offset=(1,1))
        self.curr_plot_graph.showGrid(x=True, y=True)

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
        
        # Empty list of lists
        self.voltages = []
        self.currents = []
        self.powers = []

        for it in range(0, psuChannels):
            self.voltages.append([])
            self.currents.append([])
            self.powers.append([])

        # Plot line reference for currents
        colormap = plt.colormaps['tab20'] 

        self.volt_plots = []
        self.curr_plots = []
        self.power_plots = []

        for it in range(0, psuChannels):
            volt_line = self.volt_plot_graph.plot(
                self.time,
                self.voltages[it],
                name=f"Voltage ch.{it}",
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.volt_plots.append(volt_line)
            
            curr_line = self.curr_plot_graph.plot(
                self.time,
                self.currents[it],
                name=f"Current ch.{it}",
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.curr_plots.append(curr_line)

            power_line = self.power_plot_graph.plot(
                self.time,
                self.powers[it],
                name=f"Power ch.{it}",
                pen = (colormap(it)[0] * 255, colormap(it)[1] * 255, colormap(it)[2] * 255),
                #symbol = 'x',
                #symbolBrush=colormap(it),
            )
            self.power_plots.append(power_line)
    
    def update_currs_volts_pwrs(self, ts, currs, volts, pwrs):
        #Discard data older than 2 hours and append time
        if len(self.time) > 120:
            self.time = self.time[1:]
            for channel in range(0, len(currs)):
                self.currents[channel] = self.currents[channel][1:]
                self.voltages[channel] = self.voltages[channel][1:]
                self.powers[channel] = self.powers[channel][1:]
        self.time.append(ts)
        #Plot currents, voltages and powers
        for channel in range(0, len(currs)):
            self.currents[channel].append(currs[channel])
            self.voltages[channel].append(volts[channel])
            self.powers[channel].append(pwrs[channel])
            self.curr_plots[channel].setData(self.time, self.currents[channel])
            self.volt_plots[channel].setData(self.time, self.voltages[channel])
            self.power_plots[channel].setData(self.time, self.powers[channel])
    
    def update_temps(self, ts, tempsU, tempsY, tempsEXT, tempsP1S):
        pass

def update_measure(psu, widgets, logfile, qlcs_data):
    ts = timestamp()

    # Heaters power supply channels
    psu_channels = psu.channels

    # Data from DAQ970A
    tempsU = qlcs_data['u']
    tempsY = qlcs_data['y']
    tempsEXT = qlcs_data['ext']
    tempsP1S = qlcs_data['p1s']
    strain = qlcs_data['strain']

    # Data from power supply
    currents = []
    voltages = []
    powers = []
    # Acquire values
    for it in range(psu_channels):
        currents.append(psu.get_current(it))
        voltages.append(psu.get_voltage(it))
        powers.append(psu.compute_power(it))

    # Write to file
    logfile.write(str(ts))
    for it in range(len(tempsU)):
        logfile.write(','+str(tempsU[it]))
    for it in range(len(tempsY)):
        logfile.write(','+str(tempsY[it]))
    for it in range(len(tempsEXT)):
        logfile.write(','+str(tempsEXT[it]))
    for it in range(len(tempsP1S)):
        logfile.write(','+str(tempsP1S[it]))
    for it in range(len(strain)):
        logfile.write(','+str(strain[it]))
    for it in range(psu_channels):
        logfile.write(','+str(voltages[it]))
        logfile.write(','+str(currents[it]))
        logfile.write(','+str(powers[it]))

    logfile.write('\n')
    logfile.flush()
    
    #Update plots
    for widget in widgets:
        widget.update_temps(ts, tempsU, tempsY, tempsEXT, tempsP1S)
        widget.update_currs_volts_pwrs(ts, currents, voltages, powers)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, logfile, psu_channels, timestr, alim, daq970a):
        super().__init__()
        self.setWindowTitle('TEMP PSU')
        self.resize(800, 600)

        self.alim = alim
        self.daq970a = daq970a
        
        self.low_temp_UP = 0.0
        self.high_temp_UP = 0.0
        self.low_temp_P1S = 0.0
        self.high_temp_P1S = 0.0

        # Create a tab widget
        tab_widget = QtWidgets.QTabWidget()

        #Tab for controls
        ctrls_tab = QtWidgets.QWidget()
        ctrlsLayout = QtWidgets.QGridLayout(ctrls_tab)
        tab_widget.addTab(ctrls_tab, "Controls")

        # Tab for the U and Y temperatures
        temp_UY_plot_tab = QtWidgets.QWidget()
        plotLayoutUY = QtWidgets.QVBoxLayout(temp_UY_plot_tab)
        tab_widget.addTab(temp_UY_plot_tab, "U and Y")

        # Tab for the EXT and P1S temperatures
        temp_EXT_P1S_plot_tab = QtWidgets.QWidget()
        plotLayoutEP = QtWidgets.QVBoxLayout(temp_EXT_P1S_plot_tab)
        tab_widget.addTab(temp_EXT_P1S_plot_tab, "EXT and P1S")

        # Tab for Voltages, Currents and Powers
        psu_plot_tab = QtWidgets.QWidget()
        plotLayout = QtWidgets.QVBoxLayout(psu_plot_tab)
        tab_widget.addTab(psu_plot_tab, "Voltages, Currents and Powers")

        # Control widgets declarations
        # DAQ970A connection
        daq970_conn_lbl = QtWidgets.QLabel("Address:")
        daq970_conn_box = QtWidgets.QLineEdit()
        daq970_conn_box.setPlaceholderText("IP/USB address ...")
        daq970_conn_box.setText('USB0::0x2A8D::0x5101::MY58010842::0::INSTR')
        daq970_conn_btn = QtWidgets.QPushButton("Connect")

        # DAQ970A connection type: switch to select USB or IP
        daq970_conn_type_lbl = QtWidgets.QLabel("Type:")
        #daq970_conn_type_lbl.setAlignment(Qt.AlignRight)
        daq970_conn_type_box = QtWidgets.QComboBox()
        daq970_conn_type_box.addItem("USB")
        daq970_conn_type_box.addItem("IP")
        daq970_conn_type_box.setCurrentIndex(0)

        # PSU connection
        psu_conn_lbl = QtWidgets.QLabel("Address:")
        #psu_conn_lbl.setAlignment(Qt.AlignRight)
        psu_conn_box = QtWidgets.QLineEdit()
        psu_conn_box.setPlaceholderText("IP/USB address ...")
        psu_conn_box.setText('192.168.1.90')
        psu_conn_btn = QtWidgets.QPushButton("Connect")

        # PSU connection type: switch to select USB or IP
        psu_conn_type_lbl = QtWidgets.QLabel("Type:")
        #psu_conn_type_lbl.setAlignment(Qt.AlignRight)
        psu_conn_type_box = QtWidgets.QComboBox()
        psu_conn_type_box.addItem("USB")
        psu_conn_type_box.addItem("IP")
        psu_conn_type_box.setCurrentIndex(1)

        # Logger commands
        start_btn = QtWidgets.QPushButton("Start logging")
        start_btn.setDisabled(True)
        stop_btn = QtWidgets.QPushButton("Stop logging")

        def connect_daq970a(inst_string, usb=False):
            try:
                self.daq970a.updateConnection(inst_string, usb)
                daq970_conn_btn.setDisabled(True)
            except pyvisa.errors.VisaIOError:
                print("Error connecting to the DAQ970A")
                self.daq970a = None

        def connect_power_supply(inst_string, usb=False):
            try:
                self.alim = PowerSupply(inst_string, usb, psu_channels, 'temps_'+timestr)
                self.alim.output_all_off()
                self.alim.set_voltage(1, 14.02) #change to 14.5 V
                self.alim.set_voltage(2, 26.9) #change to 27.6 V
                self.alim.set_voltage(3, 50)
                self.alim.set_voltage(4, 50)
                psu_conn_btn.setDisabled(True)
                start_btn.setEnabled(True)
            except pyvisa.errors.VisaIOError:
                print("Error connecting to the power supply")
                self.alim = None
        
        def start_query():
            #Update threshold temperatures
            self.updateBoxLowUpTemp(low_temp_UP_box)
            self.updateBoxHighUpTemp(high_temp_UP_box)
            self.updateBoxLowP1STemp(low_temp_P1S_box)
            self.updateBoxHighP1STemp(high_temp_P1S_box)

            write_header(logfile)
            timer.start()
            start_btn.setDisabled(True)
        
        def stop_query():
            # Stop timer
            timer.stop()
            # Stop DAQ970A
            self.daq970a.stop_query()
            # Enable Start button
            start_btn.setEnabled(True)
            # Disable Stop button
            stop_btn.setDisabled(True) 

        # List of all widgets
        widgets = []
        plot_widget = PlotTempWidget(f"Temp", "Time", "Temp (°C)", 0, self.daq970a)
        widgets.append(plot_widget.temp_U_plot_graph)
        plotLayoutUY.addWidget(widgets[0])
        widgets.append(plot_widget.temp_Y_plot_graph)
        plotLayoutUY.addWidget(widgets[1])
        
        widgets.append(plot_widget.temp_EXT_plot_graph)
        plotLayoutEP.addWidget(widgets[2])
        widgets.append(plot_widget.temp_P1S_plot_graph)
        plotLayoutEP.addWidget(widgets[3])

        plot_widget2 = PlotPSUWidget(f"PSU", "Time", "PSU", 0, self.alim)
        widgets.append(plot_widget2.volt_plot_graph)
        plotLayout.addWidget(widgets[4])
        widgets.append(plot_widget2.curr_plot_graph)
        plotLayout.addWidget(widgets[5])
        widgets.append(plot_widget2.power_plot_graph)
        plotLayout.addWidget(widgets[6])

        daq970_conn_btn.clicked.connect(lambda: connect_daq970a(daq970_conn_box.text(), daq970_conn_type_box.currentText() == "USB"))
        psu_conn_btn.clicked.connect(lambda: connect_power_supply((psu_conn_box.text()),psu_conn_type_box.currentText() == "USB"))
        start_btn.clicked.connect(lambda: start_query())
        stop_btn.clicked.connect(lambda: stop_query())

        # DAQ970A group box
        daqConnBox = QtWidgets.QGroupBox("DAQ970A Connection");
        ConnLayout = QtWidgets.QGridLayout()
        daqConnBox.setLayout(ConnLayout)
        ConnLayout.addWidget(daq970_conn_lbl, 0, 0)
        ConnLayout.addWidget(daq970_conn_box, 0, 1)
        ConnLayout.addWidget(daq970_conn_type_lbl, 0,2)
        ConnLayout.addWidget(daq970_conn_type_box, 0, 3)
        ConnLayout.addWidget(daq970_conn_btn, 0, 4)
        ctrlsLayout.addWidget(daqConnBox, 0, 0)

        # PSU group box
        psuConnBox = QtWidgets.QGroupBox("Power-Supply Connection");
        ConnLayout = QtWidgets.QGridLayout()
        psuConnBox.setLayout(ConnLayout)
        ConnLayout.addWidget(psu_conn_lbl, 1, 0)
        ConnLayout.addWidget(psu_conn_box, 1, 1)
        ConnLayout.addWidget(psu_conn_type_lbl, 1, 2)
        ConnLayout.addWidget(psu_conn_type_box, 1, 3)
        ConnLayout.addWidget(psu_conn_btn, 1, 4)
        ctrlsLayout.addWidget(psuConnBox, 1, 0)

        # Temperature reference values
        low_temp_UP_lbl = QtWidgets.QLabel("Low Threshold:")
        #low_temp_UP_lbl.setAlignment(Qt.AlignCenter)
        low_temp_UP_box = QtWidgets.QLineEdit()
        low_temp_UP_box.setText("-20.0")
        #low_temp_UP_box.setValidator(QDoubleValidator())
        low_temp_UP_box.editingFinished.connect(lambda: self.updateBoxLowUpTemp(low_temp_UP_box)) #Alternatives: textChanged, returnPressed
        
        high_temp_UP_lbl = QtWidgets.QLabel("High Threshold:")
        #high_temp_UP_lbl.setAlignment(Qt.AlignCenter)
        high_temp_UP_box = QtWidgets.QLineEdit()
        high_temp_UP_box.setText("30.0")
        high_temp_UP_box.editingFinished.connect(lambda: self.updateBoxHighUpTemp(high_temp_UP_box))

        low_temp_P1S_lbl = QtWidgets.QLabel("Low Threshold:")
        #low_temp_P1S_lbl.setAlignment(Qt.AlignCenter)
        low_temp_P1S_box = QtWidgets.QLineEdit()
        low_temp_P1S_box.setText("58.0")
        low_temp_P1S_box.editingFinished.connect(lambda: self.updateBoxLowP1STemp(low_temp_P1S_box))
        
        high_temp_P1S_label = QtWidgets.QLabel("High Threshold")
        #high_temp_P1S_label.setAlignment(Qt.AlignCenter)
        high_temp_P1S_box = QtWidgets.QLineEdit()
        high_temp_P1S_box.setText("60.0")
        high_temp_P1S_box.editingFinished.connect(lambda: self.updateBoxHighP1STemp(high_temp_P1S_box))
        
        # U Plane group box
        upConnBox = QtWidgets.QGroupBox("U Plane Temperature Settings (°C)");
        ConnLayout = QtWidgets.QGridLayout()
        upConnBox.setLayout(ConnLayout)
        ConnLayout.addWidget(low_temp_UP_lbl, 2, 0)
        ConnLayout.addWidget(low_temp_UP_box, 2, 1)
        ConnLayout.addWidget(high_temp_UP_lbl, 2, 2)
        ConnLayout.addWidget(high_temp_UP_box, 2, 3)
        ctrlsLayout.addWidget(upConnBox, 2, 0)

        # P1S group box
        p1sConnBox = QtWidgets.QGroupBox("P1S Temperature Settings (°C)");
        ConnLayout = QtWidgets.QGridLayout()
        p1sConnBox.setLayout(ConnLayout)
        ConnLayout.addWidget(low_temp_P1S_lbl, 3, 0)
        ConnLayout.addWidget(low_temp_P1S_box, 3, 1)
        ConnLayout.addWidget(high_temp_P1S_label, 3, 2)
        ConnLayout.addWidget(high_temp_P1S_box, 3, 3)
        ctrlsLayout.addWidget(p1sConnBox, 3, 0)

        #Start/Stop buttons
        ctrlsLayout.addWidget(start_btn, 4, 0)
        ctrlsLayout.addWidget(stop_btn, 5, 0)
        
        #QGridLayout stretches
        ctrlsLayout.setRowStretch(ctrlsLayout.rowCount(), 1)
        #ctrlsLayout.setColumnStretch(ctrlsLayout.columnCount(), 1)

        timer = QtCore.QTimer()
        timer.setInterval(self.daq970a.timeout+5000)

        self.previous_status = [False, False]

        def check_temp(psu, temp, low_temp, high_temp, previous):
            if temp > low_temp and temp < high_temp:
                # Maintain the previous state
                return previous
            elif temp > high_temp:
                # Turn off the heater
                return False
            else:
                # Turn on the heater
                return True
            
        def heater_control(psu, istempU, temp, low_temp, high_temp):
            if istempU:
                self.previous_status[0] = check_temp(psu, temp, low_temp, high_temp, self.previous_status[0])
                print(f'U Plane: Temp.: {temp:.2f} - low thr: {low_temp} - high thr: {high_temp} - previous state: {self.previous_status[0]}')
                if self.previous_status[0]:
                    psu.output_on(1)
                    psu.output_on(2)
                else:
                    psu.output_off(1)
                    psu.output_off(2)
            else:
                self.previous_status[1] = check_temp(psu, temp, low_temp, high_temp, self.previous_status[1])
                print(f'P1NS: Temp.: {temp:.2f} - low thr: {low_temp} - high thr: {high_temp} - previous state: {self.previous_status[1]}')
                if self.previous_status[1]:
                    psu.output_on(3)
                    psu.output_on(4)
                else:
                    psu.output_off(3)
                    psu.output_off(4)

        def write_header(logfile):
            # Write reference temperatures in the header
            logfile.write('#Initial Reference temperatures: ' + str(self.low_temp_UP) + 'degC < U-Plane < ' + str(self.high_temp_UP) + 'degC, ' + str(self.low_temp_P1S) + 'degC < P1NS < ' + str(self.high_temp_P1S) + 'degC\n')

            #logfile.write('#s')
            #logfile.write(self.daq970a.csvUnits())
            #logfile.write(self.alim.csvUnits())
            #logfile.write('\n')

            logfile.write('Timestamp')
            logfile.write(self.daq970a.csvHeader())
            logfile.write(self.alim.csvHeader())
            logfile.write('\n')

            logfile.flush()

        def timer_callback(psu, widgets, logfile, psu_channels):
            qlcs_data = self.daq970a.query()
            
            update_measure(psu, widgets, logfile, qlcs_data)

            #Compute reference temperatures
            ref_UP = np.mean([qlcs_data['u'][8], qlcs_data['u'][10]])
            ref_p1s = np.mean(np.asarray(qlcs_data['p1s']))

            # Check if the temperatures are within the limits and control the heaters for U and P1S
            heater_control(psu, True, ref_UP, self.low_temp_UP, self.high_temp_UP)
            heater_control(psu, False, ref_p1s, self.low_temp_P1S, self.high_temp_P1S)
        

        timer.timeout.connect(lambda: timer_callback(self.alim, [plot_widget, plot_widget2], logfile, psu_channels))

        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QVBoxLayout(central_widget)
        central_layout.addWidget(tab_widget)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        # Override the closeEvent method to ask the user if they want to exit
        reply = QtWidgets.QMessageBox.question(
            self,
            'Exit',
            'Are you sure you want to exit?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.daq970a.stop_query()
            event.accept()  # Allow the window to close
        else:
            event.ignore()  # Ignore the close event

    def __del__(self):
        del self.alim
        del self.daq970a
    
    def updateBoxLowUpTemp(self, box):
        try:
            self.low_temp_UP = float(box.text())
        except:
            print(f'{box.text()} not a float')
            box.undo()
    
    def updateBoxHighUpTemp(self, box):
        try:
            self.high_temp_UP = float(box.text())
        except:
            print(f'{box.text()} not a float')
            box.undo()
    
    def updateBoxLowP1STemp(self, box):
        try:
            self.low_temp_P1S = float(box.text())
        except:
            print(f'{box.text()} not a float')
            box.undo()
    
    def updateBoxHighP1STemp(self, box):
        try:
            self.high_temp_P1S = float(box.text())
        except:
            print(f'{box.text()} not a float')
            box.undo()

def main():
    timestr = time.strftime("%Y%m%d_%H%M%S")
    psu_channels = 4

    # # Check if the log directory exists
    # if not os.path.exists('log'):
    #     os.makedirs('log')

    with open('log/temp_plotter_' + timestr + '.txt', 'w') as logfile:
        # Write header
        logfile.write('#DAQ970A and PSU data\n')
        logfile.write('#Date: ' + timestr + '\n')

        alim = None
        daq970a = qlcsTvacDaq970('', False, timestr)
                      
        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindow(logfile, psu_channels, timestr, alim, daq970a)
        main_window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()