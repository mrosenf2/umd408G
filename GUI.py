import time
import tkinter
import face_rec2
from threading import Thread
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
import detect_trackClass
import cv2
import os
import socket
import pickle

# START GUI DEFINITIONS
# main window
top = tkinter.Tk()
top.title("Team Shaspasms")

# setup client connection
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

def sendFrame(frm):
    print('frame:',frm)
    # create frame as bytes
    frm = pickle.dumps(frm)
    s.sendall(str(len(frm)).encode())
    s.sendall(frm)
    recv = s.recv(BUFFER_SIZE)
    print("received data:", recv)
def closeconn():
    s.close()




# button functions


def button_SelectFile():
    filename = askopenfilename()
    txt_fn.delete('1.0', tkinter.END)
    txt_fn.insert(tkinter.END, filename)

def button_Go():
    dir = os.getcwd()
    vidPath = dir + "\\Clips\\gatesjobs.mp4"
    # vidPath = txt_fn.get("1.0", "end-0c")
    tracker = detect_trackClass.faceTracker(vidPath)
    try:
        while True:
            frame = tracker.detectAndTrackMultipleFaces()
            print((frame))
            # cv2.imshow("Sent Frame", frame)
            try:
                sendFrame(frame)
            except ConnectionAbortedError as e:
                print("Cxn was terminated")
                top.destroy()
                break                        
            input("press enter to continue")
    except KeyboardInterrupt as e:
        top.destroy()
        pass


# widgets
txt_fn = tkinter.Text(top, height=3, width=30)
txt_fn.grid(row=0, column=0)

# btn_sf = tkinter.Button(top, text="Choose...", command=button_SelectFile)
# btn_sf.grid(row=0, column=1)

btn_go = tkinter.Button(top, text="Go", command=button_Go)
btn_go.grid(row=0, column=2)

# END GUI DEFINITIONS



top.mainloop()
