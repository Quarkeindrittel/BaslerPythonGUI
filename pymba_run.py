#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 16:50:22 2017

@author: andreas
"""
import pymba.vimba as vim
import time

# start Vimba
with vim.Vimba() as vimba:
    # get system object
    system = vimba.getSystem()
    # list available cameras (after enabling discovery for GigE cameras)
    if system.GeVTLIsPresent:
        system.runFeatureCommand("GeVDiscoveryAllOnce")
        time.sleep(0.2)
    cameraIds = vimba.getCameraIds()
    for cameraId in cameraIds:
        print('Camera ID:', cameraId)
    
    # get and open a camera
    camera0 = vimba.getCamera(cameraIds[0])
    camera0.openCamera()
    
    # list camera features
    cameraFeatureNames = camera0.getFeatureNames()
    for name in cameraFeatureNames:
        print('Camera feature:', name)

    # get the value of a feature
    print(camera0.AcquisitionMode)

    # set the value of a feature
    camera0.AcquisitionMode = 'SingleFrame'

    # create new frames for the camera
    frame0 = camera0.getFrame()    # creates a frame
    frame1 = camera0.getFrame()    # creates a second frame

    # announce frame
    frame0.announceFrame()

    # capture a camera image
    camera0.startCapture()
    frame0.queueFrameCapture()
    camera0.runFeatureCommand('AcquisitionStart')
    camera0.runFeatureCommand('AcquisitionStop')
    frame0.waitFrameCapture()

    # get image data...
    imgData = frame0.getBufferByteData()

    # ...or use NumPy for fast image display (for use with OpenCV, etc)
    import numpy as np
    moreUsefulImgData = np.ndarray(buffer = frame0.getBufferByteData(),
                                   dtype = np.uint8,
                                   shape = (frame0.height,
                                            frame0.width,
                                            1))

    import matplotlib.pyplot as plt
    plt.imshow(imgData)
    plt.show()
    
    # clean up after capture
    camera0.endCapture()
    camera0.revokeAllFrames()

    # close camera

#if __name__ == '__main__':
    #print('programm started')