#!/usr/bin/env python

"""
Cara Takemoto
Caitlyn Clabaugh
December 2011

Workstation script
"""
import pexpect, time
import Image 
from Tkinter import *

class pythonVision:
        def __init__(self, naoIP, cameraID=0, resolution=2):
                #Set up for Window

                #Define some variables
                self.ip = naoIP
                self.port = 9559
                self.pw = 'nao'
                self.naoImgP = '/home/nao/'
                self.localImgP = './'
                self.camID = cameraID
                self.res = resolution
                
                #creats root, or master
                self.root = Tk()
                
                self.root.resizable

                #save the width and height
                if self.res == 1:
                        self.width = 320
                        self.height = 240
                else:
                        self.width = 640
                        self.height = 480
                
                #Set up default image
                self.image = PhotoImage(file=self.localImgP+'defaultImg'+str(self.width)+str(self.height)+'.gif')

                #Create canvas
                self.canvas = Canvas(self.root, width=self.width, height=self.height)
        
                #Add background to canvas
                self.view = self.canvas.create_image(0, 0, anchor=NW, image=self.image)
                
                #shift view so that you can't click off image
                self.canvas.xview_moveto(0.0)
                self.canvas.yview_moveto(0.0)
                self.canvas.pack(fill=BOTH, expand=YES)
                
                #Set title of the window
                self.root.title("Python Vision Detection")
                
                #If window is resized, update width
                #The widget changed size (or location, on some platforms).
                #The new size is provided in the width and height attributes of the event object passed to the callback.
                self.root.bind("<Configure>", self.updateWH)

                #create event that is constantly renewed to get new data
                self.root.after(0, self.update)
        
                #Keeps running, handles all events
                self.root.mainloop()
                
        def setupNaoCam(self):
                #Log into Nao and run the nao sript
                try:
                        print 'Running '+'ssh nao@'+self.ip
                        takePic = pexpect.spawn('ssh nao@'+self.ip)
                        response = takePic.expect('password:')

                        #Unexpected pattern, guess asking about keys
                        if response != 0:
                                takePic.sendline('yes')
                                response = takePic.expect('password:')
                                if response == 0:
                                        takePic.sendline(self.pw)
                                else:
                                        raise Exception('ssh login failed.')
                        #Asking for password
                        else:
                                takePic.sendline(self.pw)
                                print 'Sending password'

                        #try removing previous image so will update...
                        #takePic.sendline('rm naoImage.gif')
                        print 'Running: '+'python naoVision.py '+self.ip+' > naoVision.log'
                        takePic.sendline('python naoVision.py '+self.ip+'> naoVision.log')
                        
                        #make sure that the command is given time to execute
                        #expects the promp
                        print takePic.expect('.*]\$', timeout=30)
                        takePic.sendline('ls -al > test')
                        print takePic.expect('.*]\$', timeout=30)
                        takePic.sendline('logout')
                        print 'Logging out of ssh'
                        
                except Exception, e:
                        print 'Cannot run script on Nao:'
                        print str(e)
                        exit(1)

        def getImage(self):
                #Alt method to takePic prob doesnt work

                #remove previous image
                pexpect.run('rm *.gif')

                #Get path to images
                #figure out how to determine image name
                try:
                        scpImage = pexpect.spawn('scp nao@'+self.ip+':'+self.naoImgP+'naoImage.gif ./')
                        print 'Running '+'scp nao@'+self.ip+':'+self.naoImgP+'naoImage.gif ./'
                        response = scpImage.expect('password:')

                        #Unexpected pattern, guess asking about keys
                        if response != 0:
                                scpImage.sendline('yes')
                                response = scpImage.expect('password:')
                                if response == 0:
                                        scpImage.sendline(self.pw)
                                else:
                                        raise Exception('scp login failed.')
                        else:
                                scpImage.sendline(self.pw)
                                print 'Sending password'
                       
                except Exception, e:
                        print 'Cannot retrieve image from Nao:'
                        print str(e)
                        exit(1)

                print "Image copied to local"

                scpImage.sendline('ls -al > test')

                #Create Background
                self.image = PhotoImage(file='naoImage.gif')
                
                #save the width and height
                self.width = self.image.width()
                self.height = self.image.height()
                
                #remove previous view
                self.canvas.delete(self.view)

                #Update canvas
                self.view = self.canvas.create_image(0, 0, anchor=NW, image=self.image)
                
        def updateWH(self, event):
                #Called when the main window is changed
                
                #save the width and height
                self.width = event.width
                self.height = event.height
                
        def update(self):
                print "Updating.."
                #show live image stream of what robot is seeing
                self.setupNaoCam()
                self.getImage()

                #call Image processing commands here

                #reschedule update so it runs again
                self.root.after(10000, self.update)
        
if len(sys.argv) >2:
        win = pythonVision(sys.argv[1], sys.argv[2])
elif len(sys.argv) >1:
        win = pythonVision(sys.argv[1])
else:
        print "Usage: \n pythonVision.py nao_ip camera_id"
