import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QFrame, QVBoxLayout , QSlider
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from helper_function.compile_qrc import compile_qrc
from icons_setup.compiledIcons import *
from classes.controller import Controller
from classes.customSignal import CustomSignal
from classes.frequencyViewer import FrequencyViewer
from classes.spectrogram import Spectrogram
from scipy.io import wavfile
import numpy as np
from helper_function.compile_qrc import compile_qrc

compile_qrc()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.setWindowTitle('Equalizer')
        self.setWindowIcon(QIcon('icons_setup\icons\logo.png'))
        self.isSpectrogramDisplayed = True

        self.showIcon = QIcon('icons_setup\icons\show.png')
        self.hideIcon = QIcon('icons_setup\icons\hide.png')

        self.spectrogramsFrame = self.findChild(QFrame, 'spectrogramsFrame')
        self.spectrogramDisplayButton = self.findChild(QPushButton, 'spectrogramDisplayButton')
        self.spectrogramDisplayButton.clicked.connect(self.toggleSpectrogramDisplay)
        self.current_signal = None
        
        self.isSpectrogramDisplayed = True

        self.showIcon = QIcon('icons_setup\icons\show.png')
        self.hideIcon = QIcon('icons_setup\icons\hide.png')

        self.spectrogramsFrame = self.findChild(QFrame, 'spectrogramsFrame')
        self.spectrogramDisplayButton = self.findChild(QPushButton, 'spectrogramDisplayButton')
        self.spectrogramDisplayButton.clicked.connect(self.toggleSpectrogramDisplay)
        
        
        ## browsing signal button
        self.browse_button = self.findChild(QPushButton, 'browseButton')
        self.browse_button.clicked.connect(self.upload_signal)
        
        ## initializing the viewers
        self.frequency_viewer = FrequencyViewer(scale="Linear")
        self.frequency_viewer.setBackground((30, 41, 59))
        self.frequency_viewer.getAxis('bottom').setPen('w')
        self.frequency_viewer.getAxis('left').setPen('w') 
        
        self.old_signal_spectrogram = Spectrogram(id = 1)
        self.old_signal_spectrogram.setBackground((30, 41, 59))
        self.old_signal_spectrogram.getAxis('bottom').setPen('w')
        self.old_signal_spectrogram.getAxis('left').setPen('w') 
        
        self.new_signal_spectrogram = Spectrogram(id = 2)
        self.new_signal_spectrogram.setBackground((30, 41, 59))
        self.new_signal_spectrogram.getAxis('bottom').setPen('w')
        self.new_signal_spectrogram.getAxis('left').setPen('w') 
        
        
        ## adding the frequency viwer 
        self.frequency_frame = self.findChild(QFrame, 'frequencyFrame')
        self.frequency_frame_layout = QVBoxLayout()
        self.frequency_frame.setLayout(self.frequency_frame_layout)
        self.frequency_frame_layout.addWidget(self.frequency_viewer)
        
        self.old_spectrogram_frame = self.findChild(QFrame, 'spectrogramGraph1Frame')
        self.old_spectrogram_frame_layout = QVBoxLayout()
        self.old_spectrogram_frame.setLayout(self.old_spectrogram_frame_layout)
        self.old_spectrogram_frame_layout.addWidget(self.old_signal_spectrogram)
        
        self.new_spectrogram_frame = self.findChild(QFrame, 'spectrogramGraph2Frame')
        self.new_spectrogram_frame_layout = QVBoxLayout()
        self.new_spectrogram_frame.setLayout(self.new_spectrogram_frame_layout)
        self.new_spectrogram_frame_layout.addWidget(self.new_signal_spectrogram)
        

        self.controller = Controller(frequency_viewer=self.frequency_viewer, old_signal_spectrogram=self.old_signal_spectrogram, new_signal_spectrogram=self.new_signal_spectrogram)
        
        #Initializing Animals Mode Sliders
        self.dog_sound_level_slider = self.findChild(QSlider , "verticalSlider_19")
        self.dog_sound_level_slider.setMaximum(11)
        self.dog_sound_level_slider.setMinimum(1)
        self.dog_sound_level_slider.setPageStep(1)
        self.dog_sound_level_slider.valueChanged.connect(self.dog_sound_level_slider_effect)
        
        self.crow_sound_level_slider = self.findChild(QSlider , "verticalSlider_20")
        self.elephant_sound_level_slider = self.findChild(QSlider , "verticalSlider_21")
        self.mouse_sound_level_slider = self.findChild(QSlider , "verticalSlider_22")
        
        
        
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
            new_signal = CustomSignal(data_x, data_y , linear_frequency=[[], []])
            new_signal.signal_sampling_rate = sample_rate
            self.current_signal = new_signal
            self.controller.set_current_signal(new_signal)
            print(sample_rate)
        elif file_path.endswith('.mp3'):
            pass

        else:
            self.show_error("the file extention must be a csv file")

    def toggleSpectrogramDisplay(self):
        if self.isSpectrogramDisplayed:
            self.spectrogramsFrame.hide()
            self.spectrogramDisplayButton.setIcon(self.showIcon)
        else:
            self.spectrogramsFrame.show()
            self.spectrogramDisplayButton.setIcon(self.hideIcon)
        self.isSpectrogramDisplayed = not self.isSpectrogramDisplayed

    def dog_sound_level_slider_effect(self , slider_value):
        slider_values_map = [i for i in range(0,12,1)]
        print(slider_values_map)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())