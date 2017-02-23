#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 23:08:23 2017

@author: andreas
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
import cv2
import pypylon as py
import numpy as np
import os.path as path
import os
import pandas as pd
import copy

class CamLabel(QtWidgets.QLabel):
    move = pyqtSignal()
    if not path.exists('.temp'):
        os.mkdir('.temp')
    def __init__(self):
        super().__init__()
        self.setUP()
    
    def setUP(self):
        self.setMouseTracking(True)
        self.mousePos = QtCore.QPoint(0,0)
        
    def mouseMoveEvent(self,e):
        self.mousePos = QtGui.QMouseEvent.pos(e)
        self.move.emit()

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.show()
    
    def setupUi(self):

        self.scaleFactor = 1
        self.gainMax = 400
        self.gainMin = 300
        self.exposureTimeMax = 10**6
        self.exposureTimeMin = 25
        
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.horizontalLayout_1 = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout_1.setContentsMargins(11,11,11,11)
        self.horizontalLayout_1.setSpacing(6)
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(11,11,11,11)
        self.horizontalLayout_2.setSpacing(6)
        self.labelGain = QtWidgets.QLabel('Gain')
        self.sliderGain = QtWidgets.QSlider(enabled=False)
        self.sliderGain.setOrientation(QtCore.Qt.Horizontal)
        self.sliderGain.setMinimum(self.gainMin)
        self.sliderGain.setMaximum(self.gainMax)
        self.spinBoxGain = QtWidgets.QSpinBox(enabled=False)
        self.spinBoxGain.setMinimum(self.gainMin)
        self.spinBoxGain.setMaximum(self.gainMax)
        
        self.sliderGain.valueChanged['int'].connect(self.spinBoxGain.setValue)
        self.spinBoxGain.valueChanged['int'].connect(self.sliderGain.setValue)
        
        
        self.horizontalLayout_2.addWidget(self.labelGain)
        self.horizontalLayout_2.addWidget(self.spinBoxGain)
        self.horizontalLayout_2.addWidget(self.sliderGain)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(11,11,11,11)
        self.horizontalLayout_3.setSpacing(6)

        
        self.labelExposure = QtWidgets.QLabel('ExposureTime [\mu s]')
        self.sliderExposure = QtWidgets.QSlider(enabled=False)
        self.sliderExposure.setOrientation(QtCore.Qt.Horizontal)
        self.sliderExposure.setMinimum(self.exposureTimeMin)
        self.sliderExposure.setMaximum(self.exposureTimeMax)
        self.spinBoxExposure = QtWidgets.QSpinBox(enabled=False)
        self.spinBoxExposure.setMinimum(self.exposureTimeMin)
        self.spinBoxExposure.setMaximum(self.exposureTimeMax)
        
        self.sliderExposure.valueChanged['int'].connect(self.spinBoxExposure.setValue)
        self.spinBoxExposure.valueChanged['int'].connect(self.sliderExposure.setValue)
        
        
        
        self.horizontalLayout_3.addWidget(self.labelExposure)
        self.horizontalLayout_3.addWidget(self.spinBoxExposure)
        self.horizontalLayout_3.addWidget(self.sliderExposure)


        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(11,11,11,11)
        self.horizontalLayout_4.setSpacing(6)
        
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(11,11,11,11)
        self.horizontalLayout_5.setSpacing(6)
        
        self.horizontalLayout_6 =QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setContentsMargins(11,11,11,11)
        self.horizontalLayout_6.setSpacing(6)
        
        
        self.labelPixelFormat = QtWidgets.QLabel('PixelFormat',enabled=False)
        self.comboBoxPixel = QtWidgets.QComboBox(enabled=False)
        self.comboBoxPixel.addItems(['Mono8','Mono12'])

        self.labelcolorTable = QtWidgets.QLabel('Color Table')
        self.boxcolorTable = QtWidgets.QComboBox(enabled=False)
        self.boxcolorTable.addItems(['Smooth Cool Warm',
                                     'Bent Cool Warm','Black Body',
                                     'Extended Black Body',
                                     'KindImann',
                                     'Extended KindImann',
                                     'Grey'])
        
        self.labelTrigger = QtWidgets.QLabel('TriggerMode')
        self.boxTrigger = QtWidgets.QComboBox(enabled=False)
        self.boxTrigger.addItems(['On','Off'])
        
        self.horizontalLayout_4.addWidget(self.labelTrigger)
        self.horizontalLayout_4.addWidget(self.boxTrigger)
        
        self.horizontalLayout_5.addWidget(self.labelPixelFormat)
        self.horizontalLayout_5.addWidget(self.comboBoxPixel)
        
        self.horizontalLayout_6.addWidget(self.labelcolorTable)
        self.horizontalLayout_6.addWidget(self.boxcolorTable)
        
        self.verticalLayout_1 = QtWidgets.QVBoxLayout()
        self.verticalLayout_1.setContentsMargins(11,11,11,11)
        self.verticalLayout_1.setSpacing(6)
        
        
        self.btnRun = QtWidgets.QPushButton('run',enabled=False)
        self.btnSave = QtWidgets.QPushButton('Save a series of pictures',enabled=False)
        self.pbarSave = QtWidgets.QProgressBar(self)
        self.btnZoomIn = QtWidgets.QPushButton('ZoomIn',enabled=False)
        self.btnZoomOut = QtWidgets.QPushButton('ZoomOut',enabled=False)
        
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.setObjectName('comboBox')
        
        
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setGeometry(0,0,1200,1900)
        self.scrollArea.setObjectName("scrollArea")
        self.pic_area = CamLabel()

        self.pic_area.setScaledContents(True)
        self.pic_area.setGeometry(QtCore.QRect(0, 0, 600, 600))

        self.scrollArea.setWidget(self.pic_area)
        
        self.horizontalLayout_1.addWidget(self.scrollArea)
        self.verticalLayout_1.addWidget(self.comboBox)
        self.verticalLayout_1.addWidget(self.btnSave)
        self.verticalLayout_1.addWidget(self.pbarSave)
        self.verticalLayout_1.addWidget(self.btnRun)
        self.verticalLayout_1.addWidget(self.btnZoomIn)
        self.verticalLayout_1.addWidget(self.btnZoomOut)
        self.verticalLayout_1.addLayout(self.horizontalLayout_5)
        self.verticalLayout_1.addLayout(self.horizontalLayout_6)
        self.verticalLayout_1.addLayout(self.horizontalLayout_2)
        self.verticalLayout_1.addLayout(self.horizontalLayout_3)
        self.verticalLayout_1.addLayout(self.horizontalLayout_4)
        
        self.horizontalLayout_1.addLayout(self.verticalLayout_1)
        self.verticalLayout_1.addLayout(self.horizontalLayout_2)
        
        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        
        self.timer = QtCore.QBasicTimer()
        self.populate()

        
        self.setWindowTitle('Basler Camera UI')
        
        self.properties = {'TriggerMode':self.boxTrigger,
                           'GainRaw':self.spinBoxGain,
                           'ExposureTimeAbs':self.spinBoxExposure,
                           'PixelFormat':self.comboBoxPixel}
        
        self.colorTables = {'Smooth Cool Warm':'colorTables/smooth-cool-warm-table-byte-0256.csv',
                            'Bent Cool Warm':'colorTables/bent-cool-warm-table-byte-0256.csv',
                            'Black Body':'colorTables/black-body-table-byte-0256.csv',
                            'Extended Black Body':'colorTables/extended-black-body-table-byte-0256.csv',
                            'KindImann':'colorTables/kindlmann-table-byte-0256.csv',
                            'Extended KindImann':'colorTables/extended-kindlmann-table-byte-0256.csv',
                            'Grey':'colorTables/grey-color-table-byte-0256.csv'}
        
        self.comboBox.activated['QString'].connect(self.onActivated)
        QtCore.QMetaObject.connectSlotsByName(self)    

        self.btnRun.clicked.connect(self.doAction)
        self.btnSave.clicked.connect(self.saveImage)
        self.btnZoomIn.clicked.connect(self.zoomIn)
        self.btnZoomOut.clicked.connect(self.zoomOut)
        self.boxTrigger.currentIndexChanged.connect(self.setProperties)
        self.spinBoxExposure.valueChanged['int'].connect(self.setProperties)
        self.spinBoxGain.valueChanged['int'].connect(self.setProperties) 
        self.comboBoxPixel.currentIndexChanged.connect(self.setProperties)
        self.boxcolorTable.currentIndexChanged.connect(self.setImageTable)
        self.pic_area.move.connect(self.showStatusBar)
        
    def showStatusBar(self):
        try:
            self.statusBar().showMessage(str([int(self.pic_area.mousePos.y()/self.scaleFactor),
                             int(self.pic_area.mousePos.x()/self.scaleFactor)])+'   '+str(self.a[int(self.pic_area.mousePos.y()/self.scaleFactor),
                             int(self.pic_area.mousePos.x()/self.scaleFactor)]))

        except:
            RuntimeError

        
    def setImageTable(self):
        text = self.boxcolorTable.currentText()
        imtable = pd.read_csv(self.colorTables[text])
        self.color_table = [QtGui.qRgb(imtable['RGB_r'][i], 
                                           imtable['RGB_g'][i], imtable['RGB_b'][i]) for i in range(256)]
        try:
            self.QI.setColorTable(self.color_table)
            pixmap = QtGui.QPixmap.fromImage(self.QI)
            self.pic_area.setPixmap(pixmap)
            
        except:
            RuntimeError
            
    def onActivation(self):
        self.btnRun.setEnabled(True)
        self.btnSave.setEnabled(True)
        self.btnZoomIn.setEnabled(True)
        self.btnZoomOut.setEnabled(True)
        self.boxTrigger.setEnabled(True)
        self.spinBoxExposure.setEnabled(True)
        self.sliderExposure.setEnabled(True)
        self.spinBoxGain.setEnabled(True)
        self.sliderGain.setEnabled(True)
        self.labelPixelFormat.setEnabled(True)
        self.comboBoxPixel.setEnabled(True)
        self.boxcolorTable.setEnabled(True)
        self.boxcolorTable.setCurrentIndex(0)
        self.scaleFactor = 1.0
        self.saveimage = False
        self.setGeometry = True
        self.setImageTable()

    def getProperties(self):
        for prop in self.properties.keys():
            if isinstance(self.properties[prop],QtWidgets.QSpinBox):
                self.properties[prop].setValue(self.cam.properties[prop])
            else:
                self.index = self.properties[prop].findText(self.cam.properties[prop])
                self.properties[prop].setCurrentIndex(self.index)
                
    def setProperties(self):
        if self.cam.opened is False:
                self.cam.open() 
        for prop in self.properties.keys():
            if isinstance(self.properties[prop],QtWidgets.QSpinBox):
                self.cam.properties[prop] = self.properties[prop].value()
            else:
                self.cam.properties[prop] = str(self.properties[prop].currentText())
    
    
    def onActivated(self,text):
        self.availableCam = text
        self.cam = py.factory.create_device(self.camList[self.comboBox.currentIndex()])
        self.cam.open()
        self.getProperties()
        self.onActivation()
        
    def show_basler_cams(self):
        return py.factory.find_devices()
    
    def populate(self):
        self.camList = []
        if len(self.show_basler_cams())>0:
            for cam in self.show_basler_cams():
                self.camList.append(cam)
                self.comboBox.addItem(str(cam))
                  
    def timerEvent(self,event):
        self.show_image()
        self.showStatusBar()
        
    
    def saveImage(self):
        if self.timer.isActive():
            self.doAction()
        QtWidgets.QMessageBox.information(self, "SaveFile","Please enter the filepath plus File-Format for the images to be saved (e.g. test.tiff). Supported File-Formats are .bmp, .jpg, .png, .webp, .tiff. Default is .tiff")
        pathname = QtWidgets.QFileDialog.getSaveFileName(self)
        if not not pathname[0]:
            self.file, self.extension = path.splitext(pathname[0])
            if not self.extension in ['.bmp','.jpg','.png','.webp','.tiff']:
                self.extension = '.tiff'
            self.numberImages = 0
            ok = True
            while self.numberImages==0 and ok:
                self.numberImages, ok = QtWidgets.QInputDialog.getInt(self,'test','Please enter the number(>0) of Images to be saved')
            if self.numberImages>0:
                self.pbarSave.setMaximum(self.numberImages)
                self.numberImagesSaved = 0
                self.saveimage = True
                print(self.numberImages,ok)
                self.doAction()
            
    def doAction(self):
        if self.timer.isActive():
            self.btnRun.setText('run')
            self.timer.stop()
            self.cam.close()
            
        else:
            self.timer.start(1,self)
            self.btnRun.setText('stop')
            #self.availableCams = py.factory.find_devices()
            #self.cam = py.factory.create_device(self.camList[self.comboBox.currentIndex()])
            if self.cam.opened is False:
                self.cam.open()
            #self.getProperties()
            
    def show_image(self):
        Picture = True
        try:
            self.a = self.cam.grab_image(timeout=5000)
        except:
            RuntimeError
            Picture = False
            self.cam.close()
            self.cam.open()
            self.getProperties()

        if Picture is True:
            imgPlot, imgSave = self.changeImgForamt(self.a)
            if self.saveimage:
                cv2.imwrite(self.file + '_' + str(self.numberImagesSaved)+self.extension,imgSave)
                self.numberImagesSaved += 1
                self.pbarSave.setValue(self.numberImagesSaved)
                if self.numberImages==self.numberImagesSaved:
                    self.saveimage = False
                    self.doAction()
                    
            '''
            the image-data has to be saved via cv2 and opened by QImage. It's quite dirty, but the option of
            prozessing the image-data directly with QImage unfortunatly doesn't work
            '''
            #QIPlot = QtGui.QImage(imgPlot,imgPlot.shape[1],imgPlot.shape[0],QtGui.QImage.Format_Indexed8)
            cv2.imwrite('.temp/plot.png',imgPlot)
            QIPlot_help = QtGui.QImage('.temp/plot.png')
            
            QIPlot = QIPlot_help.convertToFormat(QtGui.QImage.Format_Indexed8)
            self.QI = QIPlot
            QIPlot.setColorTable(self.color_table)
            
            pixmap = QtGui.QPixmap.fromImage(QIPlot)
            
            if self.setGeometry:
                self.scaleFactor = 600/imgPlot.shape[1]
                self.pic_area.resize(imgPlot.shape[1]*self.scaleFactor,imgPlot.shape[0]*self.scaleFactor)
                self.setGeometry = False
            
            self.pic_area.setPixmap(pixmap)
            
    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)
        
    def scaleImage(self, factor):
        
        self.scaleFactor *= factor
        self.pic_area.resize(factor * self.pic_area.size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)
        
        self.btnZoomIn.setEnabled(self.scaleFactor<3)
        self.btnZoomOut.setEnabled(self.scaleFactor>0.33)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))
    
    
    def changeImgForamt(self,img):
        '''returns a 8-bit image of the input array regarding the current pixel 
        depth setting for the aquisition mode'''
        
        pixelFormat = self.comboBoxPixel.currentText()
        if pixelFormat == 'Mono12':
            imgPlot = np.require(img/16, np.uint8, 'C')
            imgSave = img
        
        if pixelFormat == 'Mono8':
            imgPlot = np.require(img,np.uint8, 'C')
            imgSave = img
            
        return imgPlot.copy(), imgSave.copy()
            
            
        

            

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    start = App()
    exit(app.exec_())
    