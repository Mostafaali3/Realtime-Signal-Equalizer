from customSignal import CustomSignal
import numpy as np 
import pyqtgraph as pg 
from scipy.signal import spectrogram
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QtGui
import sys

class spectogram(pg.PlotWidget):
    def __init__(self, signal:CustomSignal, id:int):
        self.__current_signal = signal
        self.id = id
        
    def plot(self):
        if self.__current_signal:
            self.clear()
            frequencies, time, intensities = 0, 0, 0
            if self.id == 1:
                signal_y = self.__current_signal.original_signal[1]
                frequencies, time, intensities = spectogram(signal_y, self.__current_signal.signal_sampling_rate)
            else:
                signal_y = self.__current_signal.reconstructed_signal[1]
                frequencies, time, intensities = spectogram(signal_y, self.__current_signal.signal_sampling_rate)
                
            pg.setConfigOption(imageAxisOrder='row-major')
            image = pg.ImageItem()
            self.addItem(image)
            image.setImage(intensities)
            transform = QtGui.QTransform()
            transform.scale(time[-1] / np.size(intensities, axis=1),
                            frequencies[-1] / np.size(intensities, axis=0))
            image.setTransform(transform)
        
    
    def clear(self):
        self.clear()
        self.__current_signal = None

# from scipy import signal
# import numpy as np
# import pyqtgraph
# from pyqtgraph.Qt import QtGui
# # Create the data
# fs = 10e3
# N = 1e5
# amp = 2 * np.sqrt(2)
# noise_power = 0.01 * fs / 2
# time = np.arange(N) / float(fs)
# mod = 500*np.cos(2*np.pi*0.25*time)
# carrier = amp * np.sin(2*np.pi*3e3*time + mod)
# noise = np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
# noise *= np.exp(-time/5)
# x = carrier + noise
# f, t, Sxx = signal.spectrogram(x, fs)

# # Interpret image data as row-major instead of col-major
# pyqtgraph.setConfigOptions(imageAxisOrder='row-major')

# pyqtgraph.mkQApp()
# win = pyqtgraph.GraphicsLayoutWidget()
# # A plot area (ViewBox + axes) for displaying the image
# p1 = win.addPlot()

# # Item for displaying image data
# img = pyqtgraph.ImageItem()
# p1.addItem(img)
# # Add a histogram with which to control the gradient of the image
# hist = pyqtgraph.HistogramLUTItem()
# # Link the histogram to the image
# hist.setImageItem(img)
# # If you don't add the histogram to the window, it stays invisible, but I find it useful.
# win.addItem(hist)
# # Show the window
# win.show()
# # Fit the min and max levels of the histogram to the data available
# hist.setLevels(np.min(Sxx), np.max(Sxx))
# # This gradient is roughly comparable to the gradient used by Matplotlib
# # You can adjust it and then save it using hist.gradient.saveState()
# hist.gradient.restoreState(
#         {'mode': 'rgb',
#          'ticks': [(0.5, (0, 182, 188, 255)),
#                    (1.0, (246, 111, 0, 255)),
#                    (0.0, (75, 0, 113, 255))]})
# # Sxx contains the amplitude for each pixel
# img.setImage(Sxx)
# # Scale the X and Y Axis to time and frequency (standard is pixels)
# transform = QtGui.QTransform()
# transform.scale(t[-1] / np.size(Sxx, axis=1),
#                 f[-1] / np.size(Sxx, axis=0))
# img.setTransform(transform)
# # Limit panning/zooming to the spectrogram
# p1.setLimits(xMin=0, xMax=t[-1], yMin=0, yMax=f[-1])
# # Add labels to the axis
# p1.setLabel('bottom', "Time", units='s')
# # If you include the units, Pyqtgraph automatically scales the axis and adjusts the SI prefix (in this case kHz)
# p1.setLabel('left', "Frequency", units='Hz')

# # Plotting with Matplotlib in comparison
# plt.pcolormesh(t, f, Sxx)
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.colorbar()
# plt.show()

# pyqtgraph.Qt.QtGui.QApplication.instance().exec_()