#!/usr/bin/env python

"""
Cara Takemoto
Caitlyn Clabaugh
December 2011

Nao script

"""
from naoqi import ALProxy
import vision_definitions, time, sys, Image 

class naoVision:
        def __init__(self, naoIP, resolution=2, cameraID=0, pwd='./'):
                #Set up for Window

                #Define some variables
                self.ip = naoIP
                self.port = 9559
                self.pw = 'nao'
                self.naoImgP = pwd
                self.camID = cameraID
                self.imgClient = ""
                self.res = resolution
                
                #create proxies to the robot
                self.setupCamera()
                self.takePic()
                
                
        def __del__(self):
                self.cleanUp()

        def cleanUp(self):
                #unsubscribe from camera proxy
                if self.imgClient != "":
                        self.videoProxy.unsubscribe(self.imgClient)

        def setupCamera(self):
                print "Creating proxies to", self.ip

                try:
                        self.camProxy = ALProxy("ALVisionToolbox", self.ip, self.port)
                except Exception, e:
                        print "Error when creating camera proxy:"
                        print str(e)
                        exit(1)

                try:
                        self.videoProxy = ALProxy("ALVideoDevice", self.ip, self.port)
                
                except Exception, e:
                        print "Error when creating video proxy:"
                        print str(e)
                        exit(1)

                try:
                        if self.res == 1:
                                resolution = vision_definitions.kQVGA  # 320 * 240
                        else:
                                resolution = vision_definitions.kVGA  # 640 * 480
                        colorSpace = vision_definitions.kRGBColorSpace
                        self.imgClient = self.videoProxy.subscribe("python_client", resolution, colorSpace, 5)
                except Exception, e:
                        print "Error when creating subscription to video proxy:"
                        print str(e)
                        exit(1)

                # Select camera.
                self.videoProxy.setParam(vision_definitions.kCameraSelectID,self.camID)


        def takePic(self):
                self.image = self.videoProxy.getImageRemote(self.imgClient)

                t0 = time.time()

                # Get a camera image.
                # image[6] contains the image data passed as an array of ASCII chars.
                naoImage = self.videoProxy.getImageRemote(self.imgClient)

                t1 = time.time()

                # Time the image transfer.
                print "Picture capture delay ", t1 - t0

                self.width = naoImage[0]
                self.height = naoImage[1]
                self.Imgarray = naoImage[6]

                # Create a PIL Image from our pixel array.
                self.image = Image.fromstring("RGB", (self.width, self.height), self.Imgarray)

                self.image.save(self.naoImgP+"naoImage.gif")
                
                
if len(sys.argv) >3:
        win = naoVision(sys.argv[1], sys.argv[2], sys.argv[3])       
if len(sys.argv) >2:
        win = naoVision(sys.argv[1], sys.argv[2])
elif len(sys.argv) >1:
        win = naoVision(sys.argv[1])
else:
        print "Usage: \n naoVision.py nao_ip camera_id image_dir"
