#!/usr/bin/env python

# Color Table Editor

from Tkinter import *
import tkFileDialog
from PIL import Image
import ImageTk, ImageDraw
import cPickle as pickle
import array
import copy

#TODO
# - Convolve: this does not cluster properly, maybe working in 2d space? may don't consider black pixels?
# - Click and drag, erase blue square
# - Convoled image is never saved
# - Should be done in C:
#          * Convolve or clustering/filter
#          * Find similar colors
#          * 3D view of YUYV space
#          * YUYV <--> RGB
#          * Everything?

# Dictionary of six possible colors 
rgb_color = {}
rgb_color[0] = (0, 0, 0)
rgb_color[1] = (255, 140, 0) # orange
rgb_color[2] = (255, 255, 0) # yellow
rgb_color[4] = (0, 255, 255) # cyan
rgb_color[8] = (34, 139, 34) # green
rgb_color[16] = (255, 255, 255) # white

#BUG
def vote(matrix, width, height, i):
    votes = {}
    count = {}
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            p = (i + x) + y * width
            col = p % width
            row = p // width
            if 0 <= col < width and 0 <= row < height and matrix[p] != 0: #do not consider black
                votes[matrix[p]] = votes.get(matrix[p], 0) + 1
    if len(votes.values()) != 0:
        m = max(votes.values())
    else:
        return 0
    if m > 0: #changed neighborhood from 4
        return votes.keys()[votes.values().index(m)]
    else:
        return 0

# Smoothing out the yuyv space
# BUG: As 2D, should be 3D space
# BUG: Never saved
def convolve(matrix, width, height):
    newmatrix = [0] * len(matrix)
    for i in range(len(matrix)):
        newmatrix[i] = vote(matrix, width, height, i)
    return newmatrix

def make_yuv(filename):
    ## Access rgb[row][col]
    ## Access yuv[col][row]
    yuv = [[None for r in range(240)] for c in range(320)]
    fp = open(filename, "r")
    rgb = []
    row = []
    c = 0
    r = 0
    for line in fp:
        y1, u, y2, v = [int(i) for i in line.split()]
        row.append(yuv2rgb(y1, u, v))
        yuv[c][r] = (y1, u, v)
        c += 1
        row.append(yuv2rgb(y2, u, v))
        yuv[c][r] = (y1, u, v)
        c += 1
        if c == 320:
            c = 0
            r += 1
            rgb.append(row)
            row = []
    return yuv, rgb

def yuv2rgb(y, u, v):
    c = y - 16
    d = u - 128
    e = v - 128
    R = (298 * c) + (409 * e) + 128
    G = (298 * c) - (100 * d) - (208 * e) + 128
    B = (298 * c) + (516 * d) + 128
    R >>= 8
    G >>= 8
    B >>= 8
    return (clip(R), clip(G), clip(B))

def clip(v):
    v = max(v, 0)
    v = min(v, 255)
    return v

class Colortable_Generator:
    def __init__(self, master):
        # This dictionary will hold all our image data
        self.backup = []
        # Contains set of unique labeled RGB values
        self.color_dict = {}
        self.color_dict["orange"] = set([])
        self.color_dict["yellow"] = set([])
        self.color_dict["cyan"] = set([])
        self.color_dict["green"] = set([])
        self.color_dict["white"] = set([])
        self.color_dict["robot_blue"] = set([])
        self.color_dict["robot_pink"] = set([])
        self.color_dict["black"] = set([])

        self.initComplete = 0
        frame = Frame(master, width=600 + 512, height=600)
        frame.pack()
        self.master = master
        self.x, self.y, self.w, self.h = -1,-1,-1,-1

        self.master.bind('<Enter>', self.bindConfigure)

            # This stuff all generates the main GUI itself

        self.master.title("Colortable Generator")

        self.Save_Colors_Button = Button(self.master,text="Save Colors", width="15")
        self.Save_Colors_Button.place(x=24, y=468, width=117, height=28)
        self.Save_Colors_Button.bind("<ButtonRelease-1>", self.Save_Colors_Button_Click)

        self.Load_Colors_Button = Button(self.master,text="Load Colors", width="15")
        self.Load_Colors_Button.place(x=150, y=468, width=116, height=27)
        self.Load_Colors_Button.bind("<ButtonRelease-1>", self.Load_Colors_Button_Click)

        self.Merge_Button = Button(self.master,text="Merge", width="15")
        self.Merge_Button.place(x=24, y=520, width=116, height=27)
        self.Merge_Button.bind("<ButtonRelease-1>", self.Merge_Button_Click)

        self.Quit_Button = Button(self.master,text="Quit", width="15")
        self.Quit_Button.place(x=24, y=566, width=116, height=27)
        self.Quit_Button.bind("<ButtonRelease-1>", quit)

        self.Write_Lookup_Table_Button = Button(self.master,text="Write Look-Up Table", width="15")
        self.Write_Lookup_Table_Button.place(x=324, y=540, width=120, height=27)
        self.Write_Lookup_Table_Button.bind("<ButtonRelease-1>", self.Write_Lookup_Table_Button_Click)

        self.Undo_Button = Button(self.master,text="Undo", width="15")
        self.Undo_Button.place(x=24, y=360, width=127, height=28)
        self.Undo_Button.bind("<ButtonRelease-1>", self.Undo_Button_Click)

        self.View_Button = Button(self.master,text="View Space", width="15")
        self.View_Button.place(x=150, y=360, width=127, height=28)
        self.View_Button.bind("<ButtonRelease-1>", self.View_Button_Click)

        self.Convolve_Button = Button(self.master,text="Convolve", width="15")
        self.Convolve_Button.place(x=275, y=360, width=116, height=27)
        self.Convolve_Button.bind("<ButtonRelease-1>", self.Convolve_Button_Click)

        self.Load_Image_Button = Button(self.master,text="Load Image", width="15")
        self.Load_Image_Button.place(x=24, y=36, width=119, height=30)
        self.Load_Image_Button.bind("<ButtonRelease-1>", self.Load_Image_Button_Click)

        lbframe = Frame( self.master )
        self.Canvas_1_frame = lbframe
        #scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Canvas_1 = Canvas(lbframe, width="320", background="white", height="240") #, yscrollcommand=scrollbar.set)
        #scrollbar.config(command=self.Canvas_1.yview)
        #scrollbar.pack(side=RIGHT, fill=Y)
        self.Canvas_1.pack(side=LEFT, fill=BOTH, expand=1)

        self.Canvas_1_frame.place(x=180, y=36)
        self.Canvas_1.bind("<ButtonPress-1>", self.Canvas_1_Click)
        self.Canvas_1.bind("<B1-Motion>", self.Canvas_1_Motion)
        self.Canvas_1.bind("<ButtonRelease-1>", self.Canvas_1_Release)

        lbframe = Frame( self.master )
        self.Canvas_2_frame = lbframe
        #scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Canvas_2 = Canvas(lbframe, width="512", background="white", height="512") #, yscrollcommand=scrollbar.set)
        #scrollbar.config(command=self.Canvas_2.yview)
        #scrollbar.pack(side=RIGHT, fill=Y)
        self.Canvas_2.pack(side=LEFT, fill=BOTH, expand=1)
        self.Canvas_2_frame.place(x=180 + 320, y=36)
        self.Canvas_2.bind("<ButtonPress-1>", self.Canvas_2_Click)
        self.Canvas_2.bind("<B1-Motion>", self.Canvas_2_Motion)
        self.Canvas_2.bind("<ButtonRelease-1>", self.Canvas_2_Release)

        self.Threshold_Val_Entry = Entry(self.master,width="15")
        self.Threshold_Val_Entry.place(x=60, y=432, width=40, height=22)
        self.Threshold_Val_Entry_StringVar = StringVar()
        self.Threshold_Val_Entry.configure(textvariable=self.Threshold_Val_Entry_StringVar)
        self.Threshold_Val_Entry_StringVar.set("0")
        self.Threshold_Val_Entry_StringVar_traceName = self.Threshold_Val_Entry_StringVar.trace_variable("w", self.Threshold_Val_Entry_StringVar_Callback)

        self.Label_1 = Label(self.master,text="Threshold", width="15")
        self.Label_1.place(x=24, y=408, width=112, height=22)

        self.Radiobutton_1 = Radiobutton(self.master,text="Orange", value="orange", width="15")
        self.Radiobutton_1.place(x=12, y=84, width=134, height=26)
        self.RadioGroup1_StringVar = StringVar()
        self.RadioGroup1_StringVar.set("orange")
        self.RadioGroup1_StringVar_traceName = self.RadioGroup1_StringVar.trace_variable("w", self.RadioGroup1_StringVar_Callback)
        self.Radiobutton_1.configure(variable=self.RadioGroup1_StringVar )

        self.Radiobutton_2 = Radiobutton(self.master,text="Yellow", value="yellow", width="15")
        self.Radiobutton_2.place(x=12, y=120, width=134, height=26)
        self.Radiobutton_2.configure(variable=self.RadioGroup1_StringVar )

        self.Radiobutton_3 = Radiobutton(self.master,text="Cyan", value="cyan", width="15")
        self.Radiobutton_3.place(x=12, y=156, width=136, height=26)
        self.Radiobutton_3.configure(variable=self.RadioGroup1_StringVar )

        self.Radiobutton_4 = Radiobutton(self.master,text="Green", value="green", width="15")
        self.Radiobutton_4.place(x=12, y=192, width=140, height=27)
        self.Radiobutton_4.configure(variable=self.RadioGroup1_StringVar )

        self.Radiobutton_5 = Radiobutton(self.master,text="White", value="white", width="15")
        self.Radiobutton_5.place(x=12, y=228, width=134, height=26)
        self.Radiobutton_5.configure(variable=self.RadioGroup1_StringVar )

        self.Radiobutton_6 = Radiobutton(self.master,text="Robot Blue", value="robot_blue", width="15")
        self.Radiobutton_6.place(x=12, y=264, width=134, height=26)
        self.Radiobutton_6.configure(variable=self.RadioGroup1_StringVar )

        self.Radiobutton_7 = Radiobutton(self.master,text="Robot Pink", value="robot_pink", width="15")
        self.Radiobutton_7.place(x=12, y=300, width=134, height=26)
        self.Radiobutton_7.configure(variable=self.RadioGroup1_StringVar )

        self.Radiobutton_8 = Radiobutton(self.master,text="Black", value="black", width="15")
        self.Radiobutton_8.place(x=12, y=320, width=134, height=26)
        self.Radiobutton_8.configure(variable=self.RadioGroup1_StringVar )

        self.master.resizable(0,0)

    def bindConfigure(self, event):
        if not self.initComplete:
            self.master.bind("<Configure>", self.Master_Configure)
            self.initComplete = 1

    def Master_Configure(self, event):
        pass
        if event.widget != self.master:
            if self.w != -1:
                return
        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())
        if (self.x, self.y, self.w, self.h) == (-1,-1,-1,-1):
            self.x, self.y, self.w, self.h = x,y,w,h

        if self.w!=w or self.h!=h:
            self.w=w
            self.h=h

    def Merge_Button_Click(self, event):
        filename = tkFileDialog.askopenfilename()
        self.push()
        fp = open(filename, "r")
        new_color_dict = pickle.load(fp)
        fp.close()
        for key in new_color_dict:
            if key not in self.color_dict:
                self.color_dict[key] = set([])
            self.color_dict[key] = self.color_dict[key].union(new_color_dict[key])
        self.reimage()

    def Convolve_Button_Click(self, event): 
        self.look_up_table = convolve(self.look_up_table, 512, 512)
        self.View_Button_Click(None)

    def Load_Colors_Button_Click(self, event): 
        # Button to open saved data
        save_file = open("Saved_Colortable", "r")
        self.push()
        new_color_dict = pickle.load(save_file)
        save_file.close()
        self.color_dict = {}
        for key in new_color_dict:
            if key not in self.color_dict:
                self.color_dict[key] = set([])
            self.color_dict[key] = self.color_dict[key].union(new_color_dict[key])
        save_file.close()
        self.reimage()

    def Save_Colors_Button_Click(self, event): #click method for component ID=15
        save_file = open("Saved_Colortable", "w")
        pickle.dump(self.color_dict, save_file)
        save_file.close()

    def make_lookup_table(self):
        # our LUT must have 262144 spots for the 262144 possible color combos
        self.look_up_table = [0]*262144 
        # Run the following on each color_dict color:
        if "black" not in self.color_dict:
            self.color_dict["black"] = set([])
        orange_list = self.color_dict["orange"]
        yellow_list = self.color_dict["yellow"]
        black_list = self.color_dict["black"]
        cyan_list = self.color_dict["cyan"]
        green_list = self.color_dict["green"]
        white_list = self.color_dict["white"]
        blue_list = self.color_dict["robot_blue"]
        pink_list = self.color_dict["robot_pink"]

        for color_list, color_id in [(yellow_list, 2),
                                     (cyan_list, 4),
                                     (white_list, 16),
                                     (orange_list, 1),
                                     (green_list, 8)]:
            color_list = list(color_list)
            for i in range(len(color_list)):
                color_triple = color_list[i] # This is 3 decimal YUV values in the form (Y,U,V)
                yuv_space_decimal = self.make_yuv_space_decimal(color_triple)
                self.look_up_table[yuv_space_decimal] = color_id
        # clear black items:
        black_list = list(black_list)
        for i in range(len(black_list)):
            color_triple = black_list[i] # This is 3 decimal YUV values in the form (Y,U,V)
            yuv_space_decimal = self.make_yuv_space_decimal(color_triple)
            self.look_up_table[yuv_space_decimal] = 0

    def make_yuv_space_decimal(self, color_triple):
        y = "00000000" + bin(color_triple[0])[2:]
        y = y[-8:-2] # truncate
        u = "00000000" + bin(color_triple[1])[2:]
        u = u[-8:-2] # truncate
        v = "00000000" + bin(color_triple[2])[2:]
        v = v[-8:-2] # truncate
        yuv_space = "0b" + y + u + v
        yuv_space_decimal = int(yuv_space,2)
        return yuv_space_decimal

    def Write_Lookup_Table_Button_Click(self, event): 
        montage_file = file("Look_Up_Table.raw", "wb")
        final_array = array.array('B')
        final_array.fromlist(self.look_up_table)
        final_array.tofile(montage_file)
        # Bit-write the whole thing

    def View_Button_Click(self, event): #click method for component ID=10
        #self.look_up_table = [0]*262144 
        #fp = open("lut_grasp_green_lines.raw.old", "rb")
        #count = 0
        #for i in range(64 * 64 * 64 - 1):
        #    print count
        #    self.look_up_table[count] = ord(fp.read(1))
        #    count += 1
        #fp.close()
        self.viewimage = Image.new("RGB", (512,512))
        self.viewdraw = ImageDraw.Draw(self.viewimage)
        for y in range(64):
            for u in range(64):
                for v in range(64):
                    row = u + (y / 8) * 64
                    col = v + (y % 8) * 64
                    pos = (y * 64 * 64) + (u * 64) + v
                    if pos < len(self.look_up_table):
                        lookup = self.look_up_table[pos]
                        if lookup != 0:
                            color = rgb_color[lookup]
                        else:
                            color = "black"
                    self.viewdraw.point((col, row), fill=color)
        self.viewphoto = ImageTk.PhotoImage(self.viewimage)
        self.Canvas_2.create_image((256,256),image=self.viewphoto) 
        
    def Undo_Button_Click(self, event): #click method for component ID=10
        self.pop()
        self.reimage()

    def Load_Image_Button_Click(self, event): #click method for component ID=1
        filename = tkFileDialog.askopenfilename()
        self.yuv, self.rgb = make_yuv(filename)
        self.image = Image.new("RGB", (320,240))
        self.draw = ImageDraw.Draw(self.image)
        self.reimage()

    def Canvas_1_Click(self, event): #click method for component ID=9
        self.start_drag = int(event.x), int(event.y)

    def Canvas_1_Motion(self, event): #click method for component ID=9
        end = int(event.x), int(event.y)
        self.draw.rectangle([self.start_drag, end], outline="blue", fill=None)
        self.photo = ImageTk.PhotoImage(self.image)
        self.Canvas_1.create_image((160,120),image=self.photo) 

    def Canvas_1_Release(self, event): #click method for component ID=9
        self.push()
        end = int(event.x), int(event.y)
        for x in range(self.start_drag[0], end[0] + 1, 1):
            for y in range(self.start_drag[1], end[1] + 1, 1):
                self.AddYuyvToDict(x, y, str(self.RadioGroup1_StringVar.get()))
        self.reimage()

    def Canvas_2_Click(self, event): #click method for component ID=9
        self.start_drag = int(event.x), int(event.y)

    def Canvas_2_Motion(self, event): #click method for component ID=9
        end = int(event.x), int(event.y)
        self.viewdraw.rectangle([self.start_drag, end], outline="blue", fill=None)
        self.viewphoto = ImageTk.PhotoImage(self.viewimage)
        self.Canvas_2.create_image((256,256),image=self.viewphoto) 

    def Canvas_2_Release(self, event): #click method for component ID=9
        self.push()
        end = int(event.x), int(event.y)
        for x in range(self.start_drag[0], end[0] + 1, 1):
            for y in range(self.start_drag[1], end[1] + 1, 1):
                self.AddFromYUVSpace(x, y, str(self.RadioGroup1_StringVar.get()))
        self.reimage()
        self.View_Button_Click(None)
        
    def Threshold_Val_Entry_StringVar_Callback(self, varName, index, mode):
        pass

    def RadioGroup1_StringVar_Callback(self, varName, index, mode):
        pass

    def AddYuyvToDict(self, x, y, color_label):
        self.color_dict[color_label] = self.color_dict[color_label].union([self.yuv[x][y]])

    def AddFromYUVSpace(self, x, y, color_label):
        v = int((x % 64) / 63.0 * 255)
        u = int((y % 64) / 63.0 * 255)
        y1 = int((int(x/512.0 * 8) + int(y/512.0 * 8) * 8) / 63.0 * 255)
        self.color_dict[color_label] = self.color_dict[color_label].union([(y1,u,v)])

    def push(self):
        total = 0
        for key in self.color_dict:
            total += len(self.color_dict[key])
        self.backup.append( copy.deepcopy(self.color_dict))
        print "Backup saved!", total

    def pop(self):
        if len(self.backup) > 0:
            self.color_dict = self.backup.pop()
            total = 0
            for key in self.color_dict:
                total += len(self.color_dict[key])
            print "Backup restored!", total
        else:
            print "Nothing left to undo"

    def reimage(self):
        total = 0
        for key in self.color_dict:
            total += len(self.color_dict[key])
        print "Redrawing", total
        self.make_lookup_table()
        # set all pixels that match:
        for c in range(320):
            for r in range(240):
                pos = self.make_yuv_space_decimal(self.yuv[c][r])
                if pos < len(self.look_up_table):
                    lookup = self.look_up_table[pos]
                    if lookup != 0:
                        color = rgb_color[lookup]
                    else:
                        color = self.rgb[r][c]
                    self.draw.point((c, r), fill=color)
        self.photo = ImageTk.PhotoImage(self.image)
        self.Canvas_1.create_image((160,120),image=self.photo) 

def main():
    root = Tk()
    app = Colortable_Generator(root)
    root.mainloop()

if __name__ == '__main__':
    #AddYuyvToDict(1, 1, "orange", [[1,2,3],[1,2,3],[1,2,3]])
    main()
