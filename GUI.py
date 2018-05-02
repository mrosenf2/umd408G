import tkinter
from threading import Thread
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
# import detect_trackClass
import cv2
import os
import socket
import pickle
import threading

# START GUI DEFINITIONS
# main window
top = tkinter.Tk()
top.title("Team Shaspasms")



# button functions


def button_SelectFile():
    filename = askopenfilename()
    txt_fn.delete('1.0', tkinter.END)
    txt_fn.insert(tkinter.END, filename)

def button_Go():
    dir = os.getcwd()
    vidPath = dir + "\\Clips\\gatesjobs.mp4"
    # vidPath = txt_fn.get("1.0", "end-0c")
    # tracker = detect_trackClass.faceTracker(vidPath)
    capture = cv2.VideoCapture(vidPath)


# widgets
txt_fn = tkinter.Text(top, height=3, width=30)
txt_fn.grid(row=0, column=0)

# btn_sf = tkinter.Button(top, text="Choose...", command=button_SelectFile)
# btn_sf.grid(row=0, column=1)

btn_go = tkinter.Button(top, text="Go", command=button_Go)
btn_go.grid(row=0, column=2)

# END GUI DEFINITIONS



top.mainloop()
