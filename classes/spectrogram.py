from classes.CustomSignal import CustomSignal
import numpy as np 
import pyqtgraph as pg 
from scipy.signal import spectrogram
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsView, QWidget

import pyqtgraph as pg
import numpy as np
from scipy.signal import spectrogram
from PyQt5 import QtGui

class Spectrogram(pg.GraphicsLayoutWidget):
    def __init__(self, signal: 'CustomSignal' = None, id: int = 1):
        super().__init__()
        self._current_signal = signal
        self.id = id

        self.plot_widget = pg.PlotWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        # self.graphics_layout = pg.GraphicsLayout()
        self.color_map_plor_widget = pg.GraphicsLayoutWidget()
        
        self.image = pg.ImageItem(axisOrder='row-major')
        self.plot_widget.addItem(self.image)
        
        color_map = pg.colormap.get('viridis')
        self.color_bar = pg.ColorBarItem(colorMap=color_map)
        
        
        self.color_bar.setImageItem(self.image)
        self.color_map_plor_widget.addItem(self.color_bar)
        
        # self.histogram = pg.HistogramLUTItem()
        # self.histogram.setImageItem(self.image)
        # self.addItem(self.histogram)
        # self.histogram_widget = pg.HistogramLUTWidget()
        # self.histogram_widget.addItem(self.histogram)

        # layout.addWidget(self.histogram_widget)
        layout.addWidget(self.color_map_plor_widget)
        self.color_map_plor_widget.setMaximumWidth(50)
        self.color_map_plor_widget.setBackground((30, 41, 59))
        self.setBackground((30, 41, 59))
        # layout.addWidget(self.color_bar)
        # self.addItem(self.color_bar)
        # self.histogram_widget.setImageItem(self.image)
        
        
    def plot(self):
        if self._current_signal:
            self.plot_widget.clear()
            frequencies, time, intensities = 0, 0, 0
            if self.id == 1:
                signal_y = self._current_signal.original_signal[1]
                frequencies, time, intensities = spectrogram(signal_y, self._current_signal.signal_sampling_rate)
            else:
                if np.array_equal(self._current_signal.original_signal[1], self._current_signal.reconstructed_signal[1]):
                    print("no change")
                signal_y = self._current_signal.reconstructed_signal[1]
                frequencies, time, intensities = spectrogram(signal_y, self._current_signal.signal_sampling_rate)

            intensities = np.log1p(intensities)  # Adds 1 to avoid log(0)
            # self.image = pg.ImageItem(axisOrder='row-major')
            self.plot_widget.addItem(self.image)
            self.image.setImage(intensities)
            transform = QtGui.QTransform()
            transform.scale(time[-1] / np.size(intensities, axis=1),
                            frequencies[-1] / np.size(intensities, axis=0))
            self.image.setTransform(transform)
            self.image.setLevels([np.min(intensities), np.max(intensities)])
            self.color_bar.setLevels(low = float(np.min(intensities)), high = float(np.max(intensities)))