import cv2
import time
import tkinter
import bestface 
from threading import Thread
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename

#############START GUI DEFINITIONS
#main window
top = tkinter.Tk()
top.title("Team Shaspasms")
#button functions
def button_SelectFile():
	filename = askopenfilename()
	txt_fn.delete('1.0', tkinter.END)
	txt_fn.insert(tkinter.END,filename)

def button_Go():
	def callback():
		global found_face
		found_face, framenum = bestface.run(txt_fn.get('1.0','end-1c'))
		found_face = Image.fromarray(found_face)
		found_face = ImageTk.PhotoImage(found_face)
		canvas_bf.create_image(1,1, image= found_face,anchor='nw')
		lbl_fc['text'] = 'The face was found on frame #' + str(framenum)
		top.title("Team Shaspasms")	
	top.title("WORKING...")
	t = Thread(target=callback)
	t.start()
#widgets
txt_fn = tkinter.Text(top, height=3, width=30)
txt_fn.grid(row=0, column=0)

btn_sf = tkinter.Button(top, text="Choose...",command=button_SelectFile)
btn_sf.grid(row=0,column=1)

canvas_bf = tkinter.Canvas(top, width = 300, height = 300)  
canvas_bf.grid(row=1,column=0)

btn_go = tkinter.Button(top, text="Go",command=button_Go)
btn_go.grid(row=0,column=2)

lbl_fc = tkinter.Label(top)
lbl_fc.grid(row=2,column=0)
###############END GUI DEFINITIONS

top.mainloop()