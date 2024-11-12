import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QFrame, QVBoxLayout , QSlider ,QComboBox, QStackedWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from helper_function.compile_qrc import compile_qrc
from icons_setup.compiledIcons import *
from classes.controller import Controller
from classes.CustomSignal import CustomSignal
from classes.frequencyViewer import FrequencyViewer
from classes.spectrogram import Spectrogram
from classes.viewer import Viewer

from scipy.io import wavfile
import numpy as np
import sounddevice as sd
from classes.modesEnum import Mode

# compile_qrc()

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
        
        ## browsing signal button
        self.browse_button = self.findChild(QPushButton, 'browseButton')
        self.browse_button.clicked.connect(self.upload_signal)
        
        
        
        ## initializing the viewers
        self.old_signal_viewer = Viewer(id =1)
        self.new_signal_viewer = Viewer(id =2)

        self.old_signal_frame = self.findChild(QFrame, 'timeDomainGraph2Frame')
        self.new_signal_frame = self.findChild(QFrame, 'timeDomainGraph1Frame')
        self.play_pause_button = self.findChild(QPushButton, 'playPauseButton')
        self.replay_button = self.findChild(QPushButton,'replayButton')
        self.rewind_button = self.findChild(QPushButton, 'pushButton_5')
        self.speed_up_button = self.findChild(QPushButton, 'pushButton_4')
        self.slow_down_button = self.findChild(QPushButton, 'pushButton_3')

        self.play_pause_button.clicked.connect(self.old_signal_viewer.play)
        self.replay_button.clicked.connect(self.old_signal_viewer.replay)
        self.rewind_button.clicked.connect(self.old_signal_viewer.rewind)
        self.speed_up_button.clicked.connect(self.old_signal_viewer.cine_speed_up)
        self.slow_down_button.clicked.connect(self.old_signal_viewer.cine_slow_down)
        
        
        self.old_signal_layout = QVBoxLayout()
        self.new_signal_layout = QVBoxLayout()
        
        self.old_signal_frame.setLayout(self.old_signal_layout)
        self.new_signal_frame.setLayout(self.new_signal_layout)

        self.old_signal_layout.addWidget(self.old_signal_viewer)
        self.new_signal_layout.addWidget(self.new_signal_viewer)
        
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

        self.controller = Controller(frequency_viewer=self.frequency_viewer, old_signal_spectrogram=self.old_signal_spectrogram, new_signal_spectrogram=self.new_signal_spectrogram, old_signal_viewer=self.old_signal_viewer, new_signal_viewer=self.new_signal_viewer)
        
        #Initializing Animals Mode Sliders adn dictionary
        
        self.slider_values_map = [0 , 0, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
        self.all_freq_ranges = dict()
        self.all_freq_ranges['dolphin'] = [(10,300) , (1000,1700) , (1800,3400)]
        self.all_freq_ranges['eagle'] = [(2400,4500)] 
        self.all_freq_ranges['owl'] = [(300,600)] 
        self.all_freq_ranges['mouse'] = [(6000,16000)]
        
        # self.music_freq_ranges = dict()
        self.all_freq_ranges['piano'] = [(0,10), (250, 275), (505, 540), (780, 790),(1040, 1060), (1565, 1590), (1840, 1850),(2105, 2120), (2375, 2395), (2650, 2665), (2925, 2940), (3200, 3215), (3487,3491), (3770, 3780), (4345, 4355), (4638, 4656), (4900, 4980)]
        self.all_freq_ranges['violin'] = [(1020, 1060), (1520, 1600), (2560, 2640), (3080, 3180), (3590, 3720),(4110,4230),(4640,4650), (5140,5345)]
        self.all_freq_ranges['triangle'] = [(4600, 5000), (5170, 5250), (5350, 5550), (5600,22000)]
        self.all_freq_ranges['xilaphone'] = [(300,1000)]

        # add uniform frequency ranges
        start = 0
        for i in range(10):
            self.all_freq_ranges['uniform' + str(i+1)] = [(start, start + 2205)]
            start += 2205

        # add uniform sliders
        self.uniform_1_slider = self.findChild(QSlider , "verticalSlider")
        self.uniform_1_slider.setMaximum(9)
        self.uniform_1_slider.setMinimum(1)
        self.uniform_1_slider.setPageStep(1)
        self.uniform_1_slider.setValue(5)
        self.uniform_1_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform1'))

        self.uniform_2_slider = self.findChild(QSlider , "verticalSlider_2")
        self.uniform_2_slider.setMaximum(9)
        self.uniform_2_slider.setMinimum(1)
        self.uniform_2_slider.setPageStep(1)
        self.uniform_2_slider.setValue(5)
        self.uniform_2_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform2'))

        self.uniform_3_slider = self.findChild(QSlider , "verticalSlider_3")
        self.uniform_3_slider.setMaximum(9)
        self.uniform_3_slider.setMinimum(1)
        self.uniform_3_slider.setPageStep(1)
        self.uniform_3_slider.setValue(5)
        self.uniform_3_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform3'))

        self.uniform_4_slider = self.findChild(QSlider , "verticalSlider_4")
        self.uniform_4_slider.setMaximum(9)
        self.uniform_4_slider.setMinimum(1)
        self.uniform_4_slider.setPageStep(1)
        self.uniform_4_slider.setValue(5)
        self.uniform_4_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform4'))

        self.uniform_5_slider = self.findChild(QSlider , "verticalSlider_5")
        self.uniform_5_slider.setMaximum(9)
        self.uniform_5_slider.setMinimum(1)
        self.uniform_5_slider.setPageStep(1)
        self.uniform_5_slider.setValue(5)
        self.uniform_5_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform5'))

        self.uniform_6_slider = self.findChild(QSlider , "verticalSlider_6")
        self.uniform_6_slider.setMaximum(9)
        self.uniform_6_slider.setMinimum(1)
        self.uniform_6_slider.setPageStep(1)
        self.uniform_6_slider.setValue(5)
        self.uniform_6_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform6'))

        self.uniform_7_slider = self.findChild(QSlider , "verticalSlider_7")
        self.uniform_7_slider.setMaximum(9)
        self.uniform_7_slider.setMinimum(1)
        self.uniform_7_slider.setPageStep(1)
        self.uniform_7_slider.setValue(5)
        self.uniform_7_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform7'))

        self.uniform_8_slider = self.findChild(QSlider , "verticalSlider_8")
        self.uniform_8_slider.setMaximum(9)
        self.uniform_8_slider.setMinimum(1)
        self.uniform_8_slider.setPageStep(1)
        self.uniform_8_slider.setValue(5)
        self.uniform_8_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform8'))

        self.uniform_9_slider = self.findChild(QSlider , "verticalSlider_9")
        self.uniform_9_slider.setMaximum(9)
        self.uniform_9_slider.setMinimum(1)
        self.uniform_9_slider.setPageStep(1)
        self.uniform_9_slider.setValue(5)
        self.uniform_9_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform9'))

        self.uniform_10_slider = self.findChild(QSlider , "verticalSlider_10")
        self.uniform_10_slider.setMaximum(9)
        self.uniform_10_slider.setMinimum(1)
        self.uniform_10_slider.setPageStep(1)
        self.uniform_10_slider.setValue(5)
        self.uniform_10_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform10'))

        self.dolphin_sound_level_slider = self.findChild(QSlider , "verticalSlider_19")
        self.dolphin_sound_level_slider.setMaximum(9)
        self.dolphin_sound_level_slider.setMinimum(1)
        self.dolphin_sound_level_slider.setPageStep(1)
        self.dolphin_sound_level_slider.setValue(5)
        self.dolphin_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'dolphin'))
        
        self.eagle_sound_level_slider = self.findChild(QSlider , "verticalSlider_20")
        self.eagle_sound_level_slider.setMaximum(9)
        self.eagle_sound_level_slider.setMinimum(1)
        self.eagle_sound_level_slider.setPageStep(1)
        self.eagle_sound_level_slider.setValue(5)
        self.eagle_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'eagle'))
        
        self.owl_sound_level_slider = self.findChild(QSlider , "verticalSlider_21")
        self.owl_sound_level_slider.setMaximum(9)
        self.owl_sound_level_slider.setMinimum(1)
        self.owl_sound_level_slider.setPageStep(1)
        self.owl_sound_level_slider.setValue(5)
        self.owl_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'owl'))
        
        self.mouse_sound_level_slider = self.findChild(QSlider , "verticalSlider_22")
        self.mouse_sound_level_slider.setMaximum(9)
        self.mouse_sound_level_slider.setMinimum(1)
        self.mouse_sound_level_slider.setPageStep(1)        
        self.mouse_sound_level_slider.setValue(5)
        self.mouse_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'mouse'))
        
        self.piano_sound_level_slider = self.findChild(QSlider , "verticalSlider_11")
        self.piano_sound_level_slider.setMaximum(9)
        self.piano_sound_level_slider.setMinimum(1)
        self.piano_sound_level_slider.setPageStep(1)        
        self.piano_sound_level_slider.setValue(5)
        self.piano_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'piano'))
        
        self.violin_sound_level_slider = self.findChild(QSlider , "verticalSlider_12")
        self.violin_sound_level_slider.setMaximum(9)
        self.violin_sound_level_slider.setMinimum(1)
        self.violin_sound_level_slider.setPageStep(1)        
        self.violin_sound_level_slider.setValue(5)
        self.violin_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'violin'))
        
        self.triangle_sound_level_slider = self.findChild(QSlider , "verticalSlider_13")
        self.triangle_sound_level_slider.setMaximum(9)
        self.triangle_sound_level_slider.setMinimum(1)
        self.triangle_sound_level_slider.setPageStep(1)        
        self.triangle_sound_level_slider.setValue(5)
        self.triangle_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'triangle'))
        
        self.xilaphone_sound_level_slider = self.findChild(QSlider , "verticalSlider_14")
        self.xilaphone_sound_level_slider.setMaximum(9)
        self.xilaphone_sound_level_slider.setMinimum(1)
        self.xilaphone_sound_level_slider.setPageStep(1)        
        self.xilaphone_sound_level_slider.setValue(5)
        self.xilaphone_sound_level_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'xilaphone'))
        
        
        
        # Initializing play button for sound before and after modification
        self.after_modifiy_play_sound_button = self.findChild(QPushButton , "soundAfterButton")
        self.after_modifiy_play_sound_button.pressed.connect(self.play_sound_after_modify)
        
        self.before_modifiy_play_sound_button = self.findChild(QPushButton , "soundBeforeButton")
        self.before_modifiy_play_sound_button.pressed.connect(self.play_sound_before_modify)
        
        # Initialize Selected Mode ComboBox
        self.selected_mode_combo_box = self.findChild(QComboBox, "modeComboBox")
        self.selected_mode_combo_box.currentIndexChanged.connect(self.changed_mode_effect)

        self.stacked_widget = self.findChild(QStackedWidget, "siderModes")
        print(self.stacked_widget)

        self.mode_to_page = {
            "Uniform Range": 0,
            "Musical Instruments": 1,
            "Animal Sounds": 2,
            "ECG Abnormalities": 3
        }

        self.selected_mode_combo_box.currentIndexChanged.connect(self.change_page)

    
        # Initialize scale type in frequency viewer
        self.frequency_viewer_scale = self.findChild(QComboBox , "comboBox")
        self.frequency_viewer_scale.currentIndexChanged.connect(self.changed_frequency_viewer_scale_effect)
        
    def change_page(self):
        mode = self.selected_mode_combo_box.currentText()
        page_index = self.mode_to_page.get(mode, 0)
        self.stacked_widget.setCurrentIndex(page_index)

    def changed_mode_effect(self):
        pass
    
        
    def upload_signal(self):
        '''
        handles loading the signal
        '''
        file_path, _ = QFileDialog.getOpenFileName(self,'Open File','', 'CSV Files (*.csv);;WAV Files (*.wav);;MP3 Files (*.mp3);;All Files (*)')
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
            data_x = np.array(data['X'].tolist())
            data_y = np.array(data['Y'].tolist())
            sample_rate = 1/(data_x[1] - data_x[0])
            new_signal = CustomSignal(data_y= data_y, data_x=data_x, linear_frequency=[[], []]) 
            new_signal.signal_sampling_rate = sample_rate
            self.current_signal = new_signal
            self.controller.set_current_signal(new_signal)
            print(sample_rate)
            
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
        
    def sound_level_slider_effect(self, slider_value, name):
        self.controller.equalizer.equalize( self.all_freq_ranges[name], factor = self.slider_values_map[slider_value])
        self.controller.set_current_signal(self.current_signal)
    
    # def animal_sound_level_slider_effect(self, slider_value, animal_name):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges[animal_name], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)
    

    # def dolphin_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['dolphin'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)
    
    # def eagle_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['eagle'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)

    # def mouse_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['mouse'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)
    
    # def owl_sound_level_slider_effect(self , slider_value):
    #     self.controller.equalizer.equalize( self.animals_freq_ranges['owl'], factor = self.slider_values_map[slider_value])
    #     self.controller.set_current_signal(self.current_signal)


    
    def play_sound_before_modify(self):
        sd.play(self.current_signal.original_signal[1] , self.current_signal.signal_sampling_rate)
        sd.wait()
    
    def play_sound_after_modify(self):
        self.controller.equalizer.inverse()
        normalized_result_sound = self.current_signal.reconstructed_signal[1] / np.max(np.abs(self.current_signal.reconstructed_signal[1]))
        sd.play(normalized_result_sound , self.current_signal.signal_sampling_rate)
        sd.wait()

    def changed_mode_effect(self):
        self.controller.mode = self.selected_mode_combo_box.currentText()
    
    def changed_frequency_viewer_scale_effect(self):
        self.controller.frequency_viewer.view_scale = self.frequency_viewer_scale.currentText()
        self.controller.set_current_signal(self.current_signal)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())