#!/usr/bin/env python

"""
Cara Takemoto
Caitlyn Clabaugh
Meagan Neal
Melanie Shafer
Kathryn Rath

Soccer tool!! 


"""
import math
import numpy as np
import scipy as sp
import Image as im
import shm
import tkMessageBox, tkFont, tkSimpleDialog, tkFileDialog, sys, os, ImageTk
from Tkinter import *

import readFSM

class MainWindow: 
    
	def __init__(self, fsmInput, naoTeam, naoID):
		
		self.naoTeam = naoTeam
                self.naoID = naoID 
		
		self.root = Tk()

		self.root.title("Team "+self.naoTeam+" player "+self.naoID)

		self.states = [None] * 3

		for fsm in range(len(fsmInput)):
			self.states[fsm] = fsmInput[fsm]

		self.background = Canvas(self.root, width=500, height=300) 
		self.background.grid(row=0, column=0) 

		#Create buttons on window
		self.draw_fsm()

		#set first current states from shared memory
		self.currentState = [None] * 3
		self.currentIndex = [None] * 3
		
		for fsm in range(len(self.states)):
			##CHANGE TO MEMORY SEG
			self.currentState[fsm] = 'bodyIdle'

		#Create window for robot's view
		self.setupRoboView()

		#create event that is constantly renewed to get new data
                self.root.after(0, self.update)

		self.root.mainloop()

	def setupRoboView(self):
		##Init Image for robot view

		#Creates window for robot view
		self.robotView = Toplevel(master=self.root)

                self.robotView.title("Camera View for Team "+str(self.naoTeam)+' '+str(self.naoID))

		#Create canvas
                self.rvCanvas = Canvas(self.robotView, width=160, height=120)
                self.rvCanvas.pack()

		#Get user's ID
                usr = str(os.getenv('USER'))

		#Make shared memory segment
                viSegName = 'vcmImage' +str(self.naoTeam)+str(self.naoID)+usr
		self.vcmImage = shm.ShmWrapper(viSegName)

		#Convert image
		yuyv = self.vcmImage.get_yuyv()
                rgbImg = self.yuyv2rgb(yuyv)
		
                self.topImg = ImageTk.PhotoImage(rgbImg)
        
                #Add background to canvas
                self.tImgID = self.rvCanvas.create_image(0, 0, anchor=NW, image=self.topImg)
                self.rvCanvas.grid(row=0, column=0, columnspan=4)
        

	def update(self):

		#show live image stream of what robot is seeing
                self.dispVideo()

		#highlight current state
		self.highlight_current_state()

		#create event that is constantly renewed to get new data
                self.root.after(200, self.update)

            
	def draw_fsm(self):
		#create attribute to hold buttons
		self.stateB = [None] * len(self.states)
		#Go through the fsm machines and their states and figure out
		#where to display them
		col_num = 0
		for fsm in range(len(self.states)):
			row_num = 0
			self.stateB[fsm] = [0] * len(self.states[fsm])
			for state in range(len(self.states[fsm])):
				self.stateB[fsm][state] = Button(self.background, text=str(self.states[fsm][state]), command=self.changeState,  width=20, background="white")
				self.stateB[fsm][state].grid(row=row_num, column=col_num)
				row_num += 1
			col_num += 1
			  

	def changeState(self):
		##CHANGE TO MEMORY SEG
		self.currentState[fsm] = None

	def highlight_current_state(self):
		#Find current states and highlight them
		for fsm in range(len(self.states)):
			stateName = 'bodyIdle' # This will be grabbed from shared memory, using the global variable memory_segment set earlier
			#If first time being called, set first state
			if self.currentIndex[fsm] == None and self.currentState[fsm] in self.states[fsm]:
				self.currentIndex[fsm] = self.states[fsm].index(self.currentState[fsm])
			#To eliminate extra work, only run if the state has changed
			elif stateName == self.currentState:
				continue
			if stateName in self.states[fsm]:
				stateIndex = self.states[fsm].index(stateName)
				#highlight new current state as red
				self.stateB[fsm][stateIndex].config(background="red")
				#unhighlight old current state
				self.stateB[fsm][self.currentIndex[fsm]].config(background="white")
				#set new current states
				self.currentState[fsm] = stateName
				self.currentIndex[fsm] = stateIndex
			else:
				print "ERROR: UNKNOWN STATE"   

        def dispVideo(self):
                #Displays the image of the robot 
                yuyv = self.vcmImage.get_yuyv()
                rgbImg = self.yuyv2rgb(yuyv)
                #display img somewhere (you could test with a different image)
                #note rgb image size is (160,120)
                
                self.topImg = ImageTk.PhotoImage(rgbImg)
		#Delete old image
		self.rvCanvas.delete(self.tImgID)
                #update image to be new image
                self.tImgID = self.rvCanvas.create_image(0, 0, anchor=NW, image=self.topImg)

        #HELPERS
        def yuyv2rgb(self, yuyv):
                #converts from yuyv shared mem format to rgb image
                #from text_image.py
                # data is actually int32 (YUYV format) not float64
                yuyv.dtype = 'uint32'
                # convert to uint8 to seperate out YUYV
                yuyv.dtype = 'uint8'
                # reshape to Nx4
                yuyv_u8 = yuyv.reshape((120, 80, 4))
        
                #convert from yuyv to yuv to rgb
                rgb = []
                for i in range(len(yuyv_u8)):
                        row = []
                        for j in range(len(yuyv_u8[0])):
                                y1 = yuyv_u8[i][j][0]
                                u = yuyv_u8[i][j][1]
                                y2 = yuyv_u8[i][j][2]
                                v = yuyv_u8[i][j][3]
                                rgb1 = self.yuv2rgb(y1, u, v)
                                row.append(rgb1)
                                rgb2 = self.yuv2rgb(y2, u, v)
                                row.append(rgb2)
                        rgb.append(row)
                #convert rgblist of tuples of (r,g,b) to array
                rgbArr = np.asarray(rgb)
                #convert array to image and save
                img = im.fromarray(np.uint8(rgbArr))
                # YOU CAN USE img TO DISPLAY ANYWHERE I THINK!
                #img.save('img.png') #just saved to test out...
                return img

        def yuv2rgb(self, y, u, v):
                c = y - 16
                d = u - 128
                e = v - 128
                R = (298 * c) + (409 * e) + 128
                G = (298 * c) - (100 * d) - (208 * e) + 128
                B = (298 * c) + (516 * d) + 128
                R >>= 8
                G >>= 8
                B >>= 8
                return (self.clip(R), self.clip(G), self.clip(B))
        
        def clip(self,v):
                v = max(v, 0)
                v = min(v, 255)
                return v        

test = MainWindow(readFSM.getBGHfsm(), sys.argv[1], sys.argv[2])

