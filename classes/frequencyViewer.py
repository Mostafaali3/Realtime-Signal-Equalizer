from classes.CustomSignal import CustomSignal
import pyqtgraph as pg
import numpy as np

class FrequencyViewer(pg.PlotWidget):
    def __init__(self , current_signal:CustomSignal = None, scale = 'linear'):
        super().__init__()
        self.current_signal = current_signal
        self.showGrid(x= True, y= True , alpha = 0.25)
        self.view_scale = scale
        self.frequency_boundaries = []

    def plot_freq_domain(self):
        self.clear()
        signal_rfft_result_magnitudes = np.abs(self.current_signal.new_linear_frequency[1])
        if(self.view_scale == "Linear"):
            self.setLogMode(x=False, y=False)
            self.invertY(False)
            self.plot(self.current_signal.new_linear_frequency[0] , list(signal_rfft_result_magnitudes), pen=pg.mkPen(color = 'w' , width=3))
            for x_value in self.frequency_boundaries:
                self.addItem(pg.InfiniteLine(pos=x_value, angle=90, pen=pg.mkPen(color='g', width=2)))
            # self.setYRange(min(self.current_signal.new_linear_frequency[1]),max(self.current_signal.new_linear_frequency[1]))
        elif(self.view_scale == "Audiogram"):
            signal_rfft_result_magnitudes_after_clipping = np.clip(signal_rfft_result_magnitudes, a_min=1e-10, a_max=None)
            signal_rfft_result_magnitudes_db_scale = 20 * np.log10(signal_rfft_result_magnitudes_after_clipping)
            # self.setRange(xRange = [min(self.frequency_boundaries) , max(self.frequency_boundaries)] , yRange =[min(signal_rfft_result_magnitudes_db_scale) , max(signal_rfft_result_magnitudes_db_scale)] )
            self.setLogMode(x=True, y=False)
            self.invertY(True)
            self.plot(self.current_signal.new_linear_frequency[0] , signal_rfft_result_magnitudes_db_scale, pen=pg.mkPen(color = 'w' , width=3))
            for x_value in self.frequency_boundaries:
                self.addItem(pg.PlotDataItem([x_value, x_value], [0, 300], pen=pg.mkPen(color='g', width=2)))
            # self.setYRange(min(self.current_signal.new_linear_frequency[1]),max(self.current_signal.new_linear_frequency[1]))
            
    @property
    def current_signal(self):
        return self.__current_signal
    
    @current_signal.setter
    def current_signal(self, new_signal):
        self.__current_signal = new_signal
    