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
		found_face, framenum = test.run(filepath=txt_fn.get('1.0','end-1c'))
		#If a face is found in the clip
		if (framenum > 0):
			#Create a photo object that can be placed into a canvas
			found_face = Image.fromarray(found_face)
			found_face = ImageTk.PhotoImage(found_face)
			canvas_bf.create_image(100,100, image= found_face,anchor='center')
			lbl_fc['text'] = 'The best face was found on frame #' + str(framenum)
			top.title("Team Shaspasms")
		#If a face wasn't found in the clip
		else:
			lbl_fc['text'] = 'NO FACES FOUND'
		#Stop the thread
		t.stopped = True
	def update_progress():
		def get_data():
			cur_time = time.time()
			cur_frame = test.get_progress()
			lbl_pg['text']='Frame progress: ' + str(cur_frame) + '/' + str(max_frames) + '.     Elapsed time: ' + str(float("{0:.2f}".format(cur_time - start_time))) +'s'
		start_time = time.time()
		time.sleep(3)
		max_frames = test.get_maxframes()
		while t.is_alive():
			get_data()
			time.sleep(.5)
		get_data()
		r.stopped = True
	top.title("WORKING...")
	t = Thread(target=callback)
	t.start()

	r = Thread(target=update_progress)
	r.start()
		
#widgets
txt_fn = tkinter.Text(top, height=3, width=30)
txt_fn.grid(row=0, column=0)

btn_sf = tkinter.Button(top, text="Choose...",command=button_SelectFile)
btn_sf.grid(row=0,column=1)

canvas_bf = tkinter.Canvas(top, width = 200, height = 200)  
canvas_bf.grid(row=1,column=0)

btn_go = tkinter.Button(top, text="Go",command=button_Go)
btn_go.grid(row=0,column=2)

lbl_fc = tkinter.Label(top)
lbl_fc.grid(row=2,column=0)

lbl_pg = tkinter.Label(top)
lbl_pg.grid(row=3,column=0)
###############END GUI DEFINITIONS

test = bestface.BF_object()

top.mainloop()