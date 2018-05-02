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
import numpy as np

# START GUI DEFINITIONS
# main window
top = tkinter.Tk()
top.title("Team Shaspasms")

# setup client connection
# TCP_IP = '10.104.190.43'
TCP_IP = '127.0.0.1'
host, _, _ = socket.gethostbyaddr(TCP_IP)
TCP_PORT = 5005
BUFFER_SIZE = 1024
# set up video



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((TCP_IP, TCP_PORT))

def sendFrame(frm):
    # create frame as bytes
    frm = pickle.dumps(frm)
    # send frame length
    s.sendall(str(len(frm)).encode())
    # wait for confirmation of frame lenght
    recv = s.recv(BUFFER_SIZE).decode()
    # send frome
    s.sendall(frm)
    # wait for confirmation of frame
    recv = s.recv(BUFFER_SIZE).decode()

    
def closeconn():
    s.close()


# button functions


def button_Webcam():
    cap = cv2.VideoCapture(0)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
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
    tracker = detect_trackClass.faceTracker('output.avi')
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
    vidPath = dir + "\\Clips\\gatesjobs.mp4"
    # vidPath = txt_fn.get("1.0", "end-0c")
    # tracker = detect_trackClass.faceTracker(vidPath)
    capture = cv2.VideoCapture(vidPath)
    loop_on = False
    try:
        while True:
            ret, frame = capture.read()
            if not ret:
                print('end of video')
                break

            try:
                #sendFrame(frame)
                #time.sleep(1.0/40)
                cv2.imshow('video', frame)
                cv2.waitKey(1)
            except (ConnectionAbortedError, ConnectionResetError) as e:
                print("Cxn was terminated")
                top.destroy()

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
frame = cv2.imread('best_tom.png')

gui_width = 600
gui_height = 400
gui_offset_x = 100
gui_offset_y = 100
top.geometry(str(gui_width)+"x"+str(gui_height)+"+"+str(gui_offset_x)+"+"+str(gui_offset_y))
cv2.imshow('video', frame)
cv2.moveWindow("video", gui_width+gui_offset_x, gui_offset_y)


top.mainloop()