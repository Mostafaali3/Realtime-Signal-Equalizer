import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QFrame, QVBoxLayout , QSlider ,QComboBox, QStackedWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from helper_function.compile_qrc import compile_qrc
from icons_setup.compiledIcons import *
from classes.controller import Controller
from classes.CustomSignal import CustomSignal
from classes.frequencyViewer import FrequencyViewer
from classes.spectrogram import Spectrogram
from classes.viewer import Viewer
import pandas as pd
from scipy.io import wavfile
import numpy as np
import sounddevice as sd
from classes.modesEnum import Mode
from pyqtgraph import LinearRegionItem


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

        self.playIcon = QIcon('icons_setup\icons\play.png')
        self.pauseIcon = QIcon('icons_setup\icons\pause.png')

        self.soundFrame = self.findChild(QFrame, 'soundFrame')
        self.soundFrame.hide()

        self.logoLabel = self.findChild(QLabel, 'logoLabel')
        pixmap = QPixmap('icons_setup\icons\logo.png')
        self.logoLabel.setPixmap(pixmap)
        self.logoLabel.setAlignment(Qt.AlignHCenter)
        self.logoLabel.setScaledContents(True)

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
        self.speed_up_button = self.findChild(QPushButton, 'pushButton_4')
        self.slow_down_button = self.findChild(QPushButton, 'pushButton_3')
        
        self.zoomin_button = self.findChildren(QPushButton, 'zoomInButton')
        self.zoomin_button[0].clicked.connect(self.old_signal_viewer.zoom_in)
        
        self.zoomout_button = self.findChildren(QPushButton, 'zoomOutButton')
        self.zoomout_button[0].clicked.connect(self.old_signal_viewer.zoom_out)
        
        self.play_pause_button.clicked.connect(self.old_signal_viewer.play)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        
        self.replay_button.clicked.connect(self.old_signal_viewer.replay)
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
        self.old_signal_spectrogram.plot_widget.setBackground((30, 41, 59))
        self.old_signal_spectrogram.plot_widget.getAxis('bottom').setPen('w')
        self.old_signal_spectrogram.plot_widget.getAxis('left').setPen('w') 
        
        self.new_signal_spectrogram = Spectrogram(id = 2)
        self.new_signal_spectrogram.plot_widget.setBackground((30, 41, 59))
        self.new_signal_spectrogram.plot_widget.getAxis('bottom').setPen('w')
        self.new_signal_spectrogram.plot_widget.getAxis('left').setPen('w') 
        
        
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
        
        self.slider_values_map = [0, 0.125/4,0.125/2,0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
        self.all_freq_ranges = dict()
        self.all_freq_ranges['dolphin'] = [(10,300) , (1000,1700) , (1800,3400)]
        self.all_freq_ranges['eagle'] = [(2400,4500)] 
        self.all_freq_ranges['owl'] = [(300,600)] 
        self.all_freq_ranges['mouse'] = [(6000,16000)]
        
          
        # self.all_freq_ranges['dolphin'] = [(9000,10000) , (11500,15500)]  #cricket
        # self.all_freq_ranges['eagle'] = [(50,1300), (1600,2000)] #crow
        # self.all_freq_ranges['owl'] = [(560,760),(2900,3500),(3800,6000)] #peacock
        # self.all_freq_ranges['mouse'] = [ (1320,1410), (1450,1690), (2200,2400), (2500,2600), (2700,2820) ,(2850,3000) ] #Raccon
        # animals piano ranges : (300, 600), (730,1100),  (1300, 1680),(1920, 2250)
        # animals flute ranges :  (600,700),(1100,1500),(1720, 2250),(3000, 3450),(3900,4150),(4500, 4700)
        
        self.all_freq_ranges['vowel_2'] = [(435,625), (850, 1105), (1380, 1700), (1995, 2120),(2450, 2720), (2950, 3200), (3500, 5000)] #weee /i:/ - "ee" 
        # self.all_freq_ranges['vowel_2'] = [(200, 290), (450, 570), (980, 1070 ), (1490,1600), (1950, 2160), (3000, 3200),  (3600, 3700), (4070, 4220), (4600, 4850)]  #اييييي 
        self.all_freq_ranges['vowel_1'] = [(200, 300), (500, 600), (1020, 1180), (1560, 1750), (2120, 2300), (2600, 2820), (3250, 3390),  (3700, 3950),(4220, 4500) ,(4850, 5090)] #اعععععع /ɑ:/ - "ah" 
        self.all_freq_ranges['vowel_3'] = [(300,400), (600,750), (1300,1500), (2000,2250), (2700,3100), (3500,3800)] #eeuu number 2 /ɔ:/ - "aw" 
        self.all_freq_ranges['vowels_violin'] =[ (350, 650), (860, 960), (1050,1200),(1300, 1700), (2000, 2400), (2700, 2900), (3200, 3400), (3600,3800),(4200,4600),(4850, 5300)]
        self.all_freq_ranges['vowels_flute'] = [ (650, 1200), (2000, 2500) ,(3050, 3550)]

        # vowels violin ranges:  (350, 650), (860, 960), (1050,1200),(1300, 1700), (2000, 2400), (2700, 2900), (3200, 3400), (3600,3800),(4200,4600),(4850, 5300)
        # vowels flute ranges: (650, 1200), (2000, 2500) ,(3050, 3550)
        
        # add uniform frequency ranges
        start = 0
        for i in range(10):
            self.all_freq_ranges['uniform' + str(i+1)] = [(start, start + 2205)]
            start += 2205
        
        # full ranges: ,(3.2,4), (4.4,5), (5.6,6),(6.11, 6.4),(6.61,7.2),(7.8,8.6),(9.01,9.8), (10.2, 11),(11.2,11.8)]
        
        self.all_freq_ranges["Crow"] =[(30,1300), (1600,2100)]
        self.all_freq_ranges["Raccon"] =[ (1310,1450), (1490,1800), (2100,2450), (2460,2630), (2670,3000) ]
        self.all_freq_ranges["Peacock"] =[(560,760),(2900,3500),(3800,6000)]  #Peacock
        self.all_freq_ranges["animal_flute"] =[(600,700),(1100,1500),(1720, 2250),(3000, 3450),(3900,4150),(4500, 4700)]
        self.all_freq_ranges["animal_piano"] =[(300, 600), (730,1100),  (1300, 1680),(1920, 2250)]

        
        self.sliders_list = []
        
        # Animals
        self.crow_slider = self.findChild(QSlider , "verticalSlider_15") #animal 1 crow
        self.sliders_list.append(self.crow_slider)
        
        self.raccon_slider = self.findChild(QSlider , "verticalSlider_23") #animal 2 Raccon
        self.sliders_list.append(self.raccon_slider)
        
        self.peacock_slider = self.findChild(QSlider , "verticalSlider_16") #animal 3 peacock
        self.sliders_list.append(self.peacock_slider)
        
        self.animal_flute_slider = self.findChild(QSlider , "verticalSlider_17") # animal mode music 1 flute
        self.sliders_list.append(self.animal_flute_slider)
        
        self.animal_piano_slider = self.findChild(QSlider , "verticalSlider_18") # animal mode music 2 piano
        self.sliders_list.append(self.animal_piano_slider)

        
        
    
        # add uniform sliders
        self.uniform_1_slider = self.findChild(QSlider , "verticalSlider")
        self.sliders_list.append(self.uniform_1_slider)

        self.uniform_2_slider = self.findChild(QSlider , "verticalSlider_2")
        self.sliders_list.append(self.uniform_2_slider)

        self.uniform_3_slider = self.findChild(QSlider , "verticalSlider_3")
        self.sliders_list.append(self.uniform_3_slider)

        self.uniform_4_slider = self.findChild(QSlider , "verticalSlider_4")
        self.sliders_list.append(self.uniform_4_slider)

        self.uniform_5_slider = self.findChild(QSlider , "verticalSlider_5")
        self.sliders_list.append(self.uniform_5_slider)

        self.uniform_6_slider = self.findChild(QSlider , "verticalSlider_6")
        self.sliders_list.append(self.uniform_6_slider)

        self.uniform_7_slider = self.findChild(QSlider , "verticalSlider_7")
        self.sliders_list.append(self.uniform_7_slider)

        self.uniform_8_slider = self.findChild(QSlider , "verticalSlider_8")
        self.sliders_list.append(self.uniform_8_slider)

        self.uniform_9_slider = self.findChild(QSlider , "verticalSlider_9")
        self.sliders_list.append(self.uniform_9_slider)

        self.uniform_10_slider = self.findChild(QSlider , "verticalSlider_10")
        self.sliders_list.append(self.uniform_10_slider)

        self.wiener_noise_level_slider = self.findChild(QSlider , "horizontalSlider")
        self.wiener_noise_level_slider.setMinimum(1)
        self.wiener_noise_level_slider.setMaximum(5)
        self.wiener_noise_level_slider.setPageStep(1)
        
        self.vowel_1 = self.findChild(QSlider , "verticalSlider_11") #Vowel 1 /ɑ:/ - "ah" 
        self.sliders_list.append(self.vowel_1)

        self.vowel_2 = self.findChild(QSlider , "verticalSlider_19") #vowel 2 weee /i:/ - "ee" 
        self.sliders_list.append(self.vowel_2)
        
        self.vowel_3 = self.findChild(QSlider , "verticalSlider_12") #vowel 3 /ɔ:/ - "aw" 
        self.sliders_list.append(self.vowel_3)
        
        self.vowel_flute = self.findChild(QSlider , "verticalSlider_13") 
        self.sliders_list.append(self.vowel_flute)
        
        self.vowel_violin = self.findChild(QSlider , "verticalSlider_14")
        self.sliders_list.append(self.vowel_violin)
        
        for slider in self.sliders_list:
            slider.setMaximum(10)
            slider.setMinimum(0)
            slider.setPageStep(1)        
            slider.setValue(5)
        
        self.crow_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'Crow'))
        self.raccon_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'Raccon'))
        self.peacock_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'Peacock'))
        self.animal_flute_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'animal_flute'))
        self.animal_piano_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'animal_piano'))

        
        self.uniform_1_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform1'))
        self.uniform_2_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform2'))
        self.uniform_3_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform3'))
        self.uniform_4_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform4'))
        self.uniform_5_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform5'))
        self.uniform_6_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform6'))
        self.uniform_7_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform7'))
        self.uniform_8_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform8'))
        self.uniform_9_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform9'))
        self.uniform_10_slider.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'uniform10'))
        
        self.vowel_1.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'vowel_1'))
        self.vowel_2.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'vowel_2'))
        self.vowel_3.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'vowel_3'))

        self.vowel_flute.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'vowels_flute'))
        self.vowel_violin.valueChanged.connect(lambda slider_value: self.sound_level_slider_effect(slider_value, 'vowels_violin'))
        
        self.wiener_noise_level_slider.valueChanged.connect(lambda slider_value: self.wiener_noise_slider_effect(slider_value))
        self.linear_region = False
        self.linear_region_boundaries = [6,11]
        
        # Initializing the frequency ranges labels
        # self.freq_range_1 = self.findChild(QLabel , "label_21")
        # self.freq_range_2 = self.findChild(QLabel , "label_24")
        # self.freq_range_3 = self.findChild(QLabel , "label_23")
        # self.freq_range_4 = self.findChild(QLabel , "label_25")
        # self.freq_range_5 = self.findChild(QLabel , "label_26")
        # self.freq_range_6 = self.findChild(QLabel , "label_27")
        # self.freq_range_7 = self.findChild(QLabel , "label_28")
        # self.freq_range_8 = self.findChild(QLabel , "label_29")
        # self.freq_range_9 = self.findChild(QLabel , "label_30")
        # self.freq_range_10 = self.findChild(QLabel , "label_32")
        
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
            "Vowels": 1,
            "Wiener Filter": 2,
            "Music and Animals": 3
        }

        self.selected_mode_combo_box.currentIndexChanged.connect(self.change_page)

    
        # Initialize scale type in frequency viewer
        self.frequency_viewer_scale = self.findChild(QComboBox , "comboBox")
        self.frequency_viewer_scale.currentIndexChanged.connect(self.changed_frequency_viewer_scale_effect)
        self.toggle_play_pause()
        
    def toggle_play_pause(self):
        if not self.old_signal_viewer.play_state:
            self.play_pause_button.setIcon(self.playIcon)
        else:
            self.play_pause_button.setIcon(self.pauseIcon)

    def change_page(self):
        mode = self.selected_mode_combo_box.currentText()
        page_index = self.mode_to_page.get(mode, 0)
        self.stacked_widget.setCurrentIndex(page_index)
        self.show_hide_sound_frame()

    
    def show_hide_sound_frame(self):
        if self.selected_mode_combo_box.currentText() == 'Wiener Filter' or self.selected_mode_combo_box.currentText() == 'Vowels' or self.selected_mode_combo_box.currentText() == 'Music and Animals':
            self.soundFrame.show()
        else:
            self.soundFrame.hide()
        
    def upload_signal(self):
        '''
        handles loading the signal
        '''
        file_path, _ = QFileDialog.getOpenFileName(self,'Open File','', 'CSV Files (*.csv);;WAV Files (*.wav);;MP3 Files (*.mp3);;All Files (*)')
        
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
            columns = data.columns
            data_x = np.array(data[columns[0]].tolist())
            data_y = np.array(data[columns[1]].tolist())
            sample_rate = 1/(data_x[1] - data_x[0])
            new_signal = CustomSignal(data_y= data_y, data_x=data_x, linear_frequency=[[], []]) 
            new_signal.signal_sampling_rate = sample_rate
            self.current_signal = new_signal
            self.controller.set_current_signal(new_signal)
            self.old_signal_viewer.play()
            self.toggle_play_pause()
            print(sample_rate)
        
        elif file_path.endswith('.dat'):
            data = pd.read_csv(file_path, delimiter='\t')
            columns = data.columns
            data_x = np.array(data[columns[1]].tolist())
            data_y = np.array(data[columns[2]].tolist())
            sample_rate = 1/(data_x[1] - data_x[0])
            new_signal = CustomSignal(data_y= data_y, data_x=data_x, linear_frequency=[[], []]) 
            new_signal.signal_sampling_rate = sample_rate
            self.current_signal = new_signal
            self.controller.set_current_signal(new_signal)
            self.old_signal_viewer.play()
            self.toggle_play_pause()
            print(sample_rate)   
        
        elif file_path.endswith('.wav'):
            sample_rate, data_y = wavfile.read(file_path)
            data_x = np.linspace(0, len(data_y)/sample_rate, len(data_y))
            new_signal = CustomSignal(data_x, data_y , linear_frequency=[[], []])
            new_signal.signal_sampling_rate = sample_rate
            self.current_signal = new_signal
            self.controller.set_current_signal(new_signal)
            self.old_signal_viewer.play()
            self.toggle_play_pause()
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
        
    def wiener_noise_slider_effect(self, slider_value):
        slider_values_mapping = [0,0.0001,0.01,0.25,0.5,1]
        self.linear_region_boundaries = self.linear_region.getRegion()
        self.controller.equalizer.wiener_filter(self.linear_region_boundaries,slider_values_mapping[slider_value])
        self.controller.set_current_signal(self.current_signal)
        self.linear_region = False
        self.check_linear_region()
        
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
        # sd.wait()
    
    def play_sound_after_modify(self):
        if(self.selected_mode_combo_box.currentText() != "Wiener Filter"):
            self.controller.equalizer.inverse()
        normalized_result_sound = self.current_signal.reconstructed_signal[1] / np.max(np.abs(self.current_signal.reconstructed_signal[1]))
        sd.play(normalized_result_sound , self.current_signal.signal_sampling_rate)
        # sd.wait()

    def changed_mode_effect(self):
        self.controller.mode = self.selected_mode_combo_box.currentText()
        for slider in self.sliders_list:        
            slider.setValue(5)
        self.check_linear_region()
            
    def check_linear_region(self):
        if self.controller.mode == "Wiener Filter":
            if not self.linear_region:
                self.linear_region = LinearRegionItem([self.linear_region_boundaries[0] , self.linear_region_boundaries[1]], movable=True) 
                self.old_signal_viewer.addItem(self.linear_region)
        else:
            if self.linear_region:
                self.old_signal_viewer.removeItem(self.linear_region)
                self.linear_region = None
                
    def changed_frequency_viewer_scale_effect(self):
        self.controller.frequency_viewer.view_scale = self.frequency_viewer_scale.currentText()
        # if(self.frequency_viewer_scale.currentText() == "Audiogram"):
        #     self.freq_range_1.setText(f'{np.log10(0.0000001):.2f} - {np.log10(2205):.2f}')
        #     self.freq_range_2.setText(f'{np.log10(2205):.2f} - {np.log10(4410):.2f}')
        #     self.freq_range_3.setText(f'{np.log10(4410):.2f} - {np.log10(6615):.2f}')
        #     self.freq_range_4.setText(f'{np.log10(6615):.2f} - {np.log10(8820):.2f}')
        #     self.freq_range_5.setText(f'{np.log10(8820):.2f} - {np.log10(11025):.2f}')
        #     self.freq_range_6.setText(f'{np.log10(11025):.2f} - {np.log10(13230):.2f}')
        #     self.freq_range_7.setText(f'{np.log10(13230):.2f} - {np.log10(15435):.2f}')
        #     self.freq_range_8.setText(f'{np.log10(15435):.2f} - {np.log10(17640):.2f}')
        #     self.freq_range_9.setText(f'{np.log10(17640):.2f} - {np.log10(19845):.2f}')
        #     self.freq_range_10.setText(f'{np.log10(19845):.2f} - {np.log10(22050):.2f}')
        # else:
        #     self.freq_range_1.setText('0 - 2205')
        #     self.freq_range_2.setText('2205 - 4410')
        #     self.freq_range_3.setText('4410 - 6615')
        #     self.freq_range_4.setText('6615 - 8820')
        #     self.freq_range_5.setText('8820 - 11025')
        #     self.freq_range_6.setText('11025 - 13230')
        #     self.freq_range_7.setText('13230 - 15435')
        #     self.freq_range_8.setText('15435 - 17640')
        #     self.freq_range_9.setText('17640 - 19845')
        #     self.freq_range_10.setText('19845 - 22050')
        self.controller.set_current_signal(self.current_signal)

    def initialize_signal(self):
        sample_rate, data_y = wavfile.read("data/uniform/Synthetic_2.wav")
        data_x = np.linspace(0, len(data_y)/sample_rate, len(data_y))
        new_signal = CustomSignal(data_x, data_y , linear_frequency=[[], []])
        new_signal.signal_sampling_rate = sample_rate
        self.current_signal = new_signal
        self.controller.set_current_signal(new_signal)
        self.old_signal_viewer.play()
        self.toggle_play_pause()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.initialize_signal()
    sys.exit(app.exec_())