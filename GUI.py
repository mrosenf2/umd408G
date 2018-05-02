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
import threading

# START GUI DEFINITIONS
# main window
top = tkinter.Tk()
top.title("Team Shaspasms")

ip = '10.104.178.225'
cxn = clientcxn(ip, 5005, 5006)



# button functions


def button_Webcam():
    cap = cv2.VideoCapture(0)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

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
    tracker = detect_trackClass.faceTracker('output.avi')
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
    tracker = detect_trackClass.faceTracker(vidPath)
    try:
        while True:
            frame = tracker.detectAndTrackMultipleFaces()
            cv2.imshow("Result", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt as e:
        pass


# widgets
txt_fn = tkinter.Text(top, height=3, width=30)
txt_fn.grid(row=0, column=0)

btn_sf = tkinter.Button(top, text="Use Webcam", command=button_Webcam)
btn_sf.grid(row=0, column=1)

upload=ImageTk.PhotoImage(file="upload.png")
btn_sf = tkinter.Button(top, image=upload, height=200, width=200,relief='raised',bd=4, command=button_SelectFile)
btn_sf.grid(row=2, column=0)

photo=ImageTk.PhotoImage(file="go.png")
btn_go = tkinter.Button(top, image=photo, height=200, width=200,relief='raised',bd=4, command=button_Go)
btn_go.grid(row=2, column=1)

# END GUI DEFINITIONS



top.mainloop()
