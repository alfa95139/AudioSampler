#Recording w Buttons, pyqtgraph app
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,QLineEdit, QGridLayout,QLabel)
from PyQt5.QtGui import QIcon #Do not remove, it may be needed for QGestureManager::deliverEvent
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyaudio
import wave


class WinApp(QWidget):
    def __init__(self):
        super().__init__()  #Equivalent: QWidget.__init__(self)

        # pyaudio stuff
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024

        # for graph
        self.MAX_PLOT_SIZE = 2 * self.CHUNK

        # graphical stuff
        self.setGeometry(10,10, self.MAX_PLOT_SIZE + 200, 300)
        self.setWindowTitle("PyQt example")
        self.setStyleSheet("background-color: black;")

        #Recording variables
        self.timeDomain=[]
        self.tDataRecord=np.array
        self.tDataBufferPlot=np.zeros(self.MAX_PLOT_SIZE, dtype=np.int16)

        #Define the Buttons
        buttonRecord = QPushButton("REC",self)        #buttonRecord.move(80,70)
        buttonRecord.setStyleSheet("background-color: darkred")
        buttonRecord.clicked.connect(self.on_buttonRecord)
        self.Record = False
        buttonPlay = QPushButton("PLAY",self)         #buttonPlay.move(150,70)
        buttonPlay.setStyleSheet("background-color: green")
        buttonPlay.clicked.connect(self.on_buttonPlay)
        self.Play = False
        buttonStop = QPushButton("STOP",self)         #buttonPlay.move(150,70)
        buttonStop.setStyleSheet("background-color: grey")
        buttonStop.clicked.connect(self.on_buttonStop)
        self.Stop = False
        buttonSave = QPushButton("Save", self)
        buttonSave.setStyleSheet("background-color: grey")
        buttonButton1 = QPushButton("Button1", self)
        buttonButton1.setStyleSheet("background-color: grey")
        buttonButton2 = QPushButton("Button2", self)
        buttonButton2.setStyleSheet("background-color: grey")

        #Define the grid, place the buttons accordingly
        layout = QGridLayout(self)
        layout.addWidget(buttonRecord, 0, 0)
        layout.addWidget(buttonStop, 0, 1)
        layout.addWidget(buttonPlay, 0, 2)
        layout.addWidget(buttonSave, 0, 3)
        layout.addWidget(buttonButton1, 2, 3)
        layout.addWidget(buttonButton2, 3, 3)

        #Time Domain Window
        self.guiTimePlot = pg.PlotWidget()
        self.guiTimePlot.setYRange(-1024,+1023)
        self.guiTimePlot.setXRange(0,self.MAX_PLOT_SIZE)

        #Place the Time Domain Window here
        layout.addWidget(self.guiTimePlot, 2, 0, 3, 3)  #THIS IS KEY



    def on_buttonRecord(self):
        if self.Record == False and self.Play == False: #Only Record when no recording nor playing
            print("Recording Start")
            self.Record = True
            #This is faster if done 1) when the object is created, and 2) soon after other operations - such as save file - are completed
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK)
        return self

    def on_buttonPlay(self):
        if self.Play == False and self.Record == False: #Only Pay when no playing nor recording
            print("Playing Start")
            self.Play = True
        return self

    def on_buttonStop(self):
        print("STOP")
        #get the data for plotting
        print("Length of timeDomain frames = ", len(self.timeDomain)) # len returns the number of frames per buffer aka self.CHUNK
        self.tDataRecord = np.array(self.timeDomain)
        self.guiTimePlot.enableAutoRange()
        self.guiTimePlot.plot(np.reshape(self.tDataRecord, len(self.timeDomain)*self.CHUNK), pen='g', clear=True)

        if self.Record == True:
            wf = wave.open("Ale.wav", 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.timeDomain))
            wf.close()
            #Graciously close audio stream
            self.stream.stop_stream()
            self.stream.close()
            #self.stream.()
        self.Play = False
        self.Record = False

        return self

    def dosomethinghere(self):
        #do something here
        #self.update()
        return self

    def update(self):
        if self.Record == True:
            raw_tData = self.stream.read(self.CHUNK, exception_on_overflow = False)

            #get the data for plotting
            tData_int16 = np.frombuffer(raw_tData, dtype=np.int16)
            self.tDataBufferPlot = np.concatenate([self.tDataBufferPlot, tData_int16])
            #append to wf_data for complete graphic at the end
            #self.timeDomain.append(raw_tData)
            self.timeDomain.append(tData_int16)
            if len(self.tDataBufferPlot)>self.MAX_PLOT_SIZE:
                self.tDataBufferPlot = self.tDataBufferPlot[self.CHUNK:]
            self.guiTimePlot.plot(self.tDataBufferPlot, pen='g', clear=True)
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex=WinApp()
    ex.show()
    #The following is to set up the regular "update" using the timer
    timer = QtCore.QTimer()
    timer.timeout.connect(ex.update)
    timer.start(20)
    #exit after execution
    sys.exit(app.exec_())
