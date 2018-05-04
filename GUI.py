import time
import tkinter
import face_rec2
from threading import Thread
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
# import detect_trackClass
import cv2
import os
import socket
import pickle
import threading
import client

# START GUI DEFINITIONS
# main window

top = tkinter.Tk()
top.title("Team Shaspasms")

ip = '10.104.176.33'
# ip = '127.0.0.1'
cxn = client.clientcxn(ip, 5005, 5006)
# cxn = None


# button functions


def button_Webcam():
    cap = cv2.VideoCapture(0)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

    # Snap webcam next to original location of GUI
    cv2.namedWindow('frame')
    cv2.moveWindow("frame", gui_width+gui_offset_x, gui_offset_y)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            out.write(frame)

            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    # tracker = detect_trackClass.faceTracker('output.avi')
    # Snap results window next to original location of GUI
    cv2.namedWindow('Result')
    cv2.moveWindow("Result", gui_width+gui_offset_x, gui_offset_y)
    try:
        while True:
            frame = tracker.detectAndTrackMultipleFaces()
            cv2.imshow("Result", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt as e:
        pass

def button_SelectFile():
    filename = askopenfilename()
    txt_fn.delete('1.0', tkinter.END)
    txt_fn.insert(tkinter.END, filename)

def button_Go():
    dir = os.getcwd()
    #vidPath = dir + "\\Clips\\gatesjobs.mp4"
    vidPath = txt_fn.get("1.0", "end-1c")
    capture = cv2.VideoCapture(vidPath)
    try:
        cxn.run(capture)
    except KeyboardInterrupt as e:
        pass


def connect(cxn, lbl):
    cxn.createCxn()
    print('creating cxn')
    while True:
        if cxn.getStatus() == 0:
            lbl.set('Connecting...')
        elif cxn.getStatus() == 1:
            lbl.set('Connection Established')
            time.sleep(2)
        else:
            lbl.set('Connection Failed')
            time.sleep(2)
# widgets
txt_fn = tkinter.Text(top, height=3, width=30)
txt_fn.grid(row=0, column=0)

btn_sf = tkinter.Button(top, text="Use Webcam", command=button_Webcam)
btn_sf.grid(row=0, column=1)

upload=ImageTk.PhotoImage(file="upload.png")
btn_sf = tkinter.Button(top, image=upload, height=200, width=200,relief='raised',bd=4, command=button_SelectFile)
btn_sf.grid(row=2, column=0)

lbl_info = tkinter.StringVar()
# lbl_info.set('Connecting...')
tkinter.Label(top, textvariable=lbl_info).grid(row=3,column=0)

photo=ImageTk.PhotoImage(file="go.png")
btn_go = tkinter.Button(top, image=photo, height=200, width=200,relief='raised',bd=4, command= button_Go)
btn_go.grid(row=2, column=1)



# Set GUI position and results position
gui_width = 600
gui_height = 400
gui_offset_x = 100
gui_offset_y = 100
top.geometry(str(gui_width)+"x"+str(gui_height)+"+"+str(gui_offset_x)+"+"+str(gui_offset_y))
preview_image = cv2.imread('film_preview.png')
cv2.imshow('video', preview_image)
cv2.moveWindow("video", gui_width+gui_offset_x, gui_offset_y)
cv2.resizeWindow('video', gui_width, gui_height)



lbl_info.set('Welcome')

# END GUI DEFINITIONS
tgt = connect


# cxn.createCxn()
t = threading.Thread(target=tgt, args=(cxn,lbl_info,))
t.start()

top.mainloop()
