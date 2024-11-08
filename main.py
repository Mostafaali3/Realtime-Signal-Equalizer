import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QFrame, QVBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from helper_function.compile_qrc import compile_qrc
from icons_setup.compiledIcons import *
from classes.controller import Controller
from classes.customSignal import CustomSignal
from classes.frequencyViewer import FrequencyViewer
from scipy.io import wavfile
import numpy as np


compile_qrc()
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.setWindowTitle('Equalizer')
        self.setWindowIcon(QIcon('icons_setup\icons\logo.png'))
        
        self.current_signal = None
        
        
        ## browsing signal button
        self.browse_button = self.findChild(QPushButton, 'browseButton')
        self.browse_button.clicked.connect(self.upload_signal)
        
        ## initializing the viewers
        self.frequency_viewer = FrequencyViewer(scale="Audiogram")
        self.frequency_viewer.setBackground((30, 41, 59))
        self.frequency_viewer.getAxis('bottom').setPen('w')
        self.frequency_viewer.getAxis('left').setPen('w') 
        
        ## adding the frequency viwer 
        self.frequency_frame = self.findChild(QFrame, 'frequencyFrame')
        self.frequency_frame_layout = QVBoxLayout()
        self.frequency_frame.setLayout(self.frequency_frame_layout)
        self.frequency_frame_layout.addWidget(self.frequency_viewer)
            
        self.controller = Controller(self.frequency_viewer)
        
        
    def upload_signal(self):
        '''
        handles loading the signal
        '''
        file_path, _ = QFileDialog.getOpenFileName(self,'Open File','', 'CSV Files (*.csv);;WAV Files (*.wav);;MP3 Files (*.mp3);;All Files (*)')
        if file_path.endswith('.csv'):
            pass
        elif file_path.endswith('.wav'):
            sample_rate, data_y = wavfile.read(file_path)
            data_x = np.linspace(0, len(data_y)/sample_rate, len(data_y))
            new_signal = CustomSignal(data_x, data_y)
            new_signal.signal_sampling_rate = sample_rate
            self.current_signal = new_signal
            self.controller.set_current_signal(new_signal)
            print(sample_rate)
        elif file_path.endswith('.mp3'):
            pass

        else:
            self.show_error("the file extention must be a csv file")
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())