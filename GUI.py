import time
import tkinter
import face_rec2
from threading import Thread
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
import detect_trackClass
import cv2

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
    vidPath = "C:/Users/Matthew/Documents/SCHOOL/SuperSenior/ENEE408G/FinalProj/Clips/gatesjobs.mp4"
    # vidPath = txt_fn.get("1.0", "end-0c")
    tracker = detect_trackClass.faceTracker(vidPath)
    w, h = tracker.get_dimensions()
    imageFrame = tkinter.Frame(top, width=w, height=h)
    imageFrame.grid(row=1, column=0)
    lmain = tkinter.Label(imageFrame)
    lmain.grid(row=0, column=1)
    def show_frame():
        frame = tracker.detectAndTrackMultipleFaces()
        # OpenCV represents images in BGR order; however PIL
        # represents images in RGB order, so we need to swap
        # the channels, then convert to PIL and ImageTk format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(image=frame)
        lmain.frame = frame
        lmain.configure(image=frame)
        lmain.after(10, show_frame)

    show_frame()



# widgets
txt_fn = tkinter.Text(top, height=3, width=30)
txt_fn.grid(row=0, column=0)

btn_sf = tkinter.Button(top, text="Choose...", command=button_SelectFile)
btn_sf.grid(row=0, column=1)

btn_go = tkinter.Button(top, text="Go", command=button_Go)
btn_go.grid(row=0, column=2)

# END GUI DEFINITIONS



top.mainloop()
