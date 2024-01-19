import time
import datetime
import pyqtgraph as pg

class TimeAxisItem(pg.AxisItem):
    """
    Class to have time in the x axis of the plots
    https://stackoverflow.com/questions/29385868/plotting-datetime-objects-with-pyqtgraph - 2023 Nov 9
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime("%H:%M:%S") for value in values]

def timestamp():
    """
    Timestamp in local unix time
    """
    return int(time.mktime(datetime.datetime.now().timetuple()))

def tsToStr(ts):
    """
    Local unix time in readabe format
    """
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y%m%d-%H%M%S")