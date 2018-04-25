from tkinter import *
from tkinter.ttk import *
import socket
import cv2
import numpy as np
import pickle


TCP_IP = '10.104.190.43'
TCP_PORT = 5005
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

def getFrame(conn):
    frame = bytes(0)
    frmlngth = int(conn.recv(BUFFER_SIZE).decode())
    conn.send('got_len'.encode())
    #print('Expected length:', frmlngth)
    while frmlngth > 0:
        data = conn.recv(BUFFER_SIZE)
        frame += data
        frmlngth -= len(data)
    #print('lngth received:', len(frame))

    return frame



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print('attempting to connect')
conn, addr = s.accept()
print('Connection address:', addr)
repeat = True

try:
	while repeat:
		#print("Attemping GET...\n")
		frame = getFrame(conn)

		# get back ndarray from bytes
		frame = pickle.loads(frame)
		#print("received frame")
		conn.send('success'.encode())
		#print('frame:',frame)
		#input("Press enter to continue")
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1)
		if key == ord('q'):
			repeat = False
except KeyboardInterrupt as e:
            pass
input("Press enter to continue")
conn.close()
