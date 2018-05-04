from tkinter import *
from tkinter.ttk import *
import socket
import cv2
import numpy as np
import pickle
from threading import Thread
import time
import detect_trackClass
import data_packet
from collections import deque

#TCP_IP = '10.104.178.225'
TCP_IP = '127.0.0.1'
FRAME_PORT = 5005
DATA_PORT = 5006
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

frame_queue = deque()

timeout_duration = 4
sleep_duration = 0.1

number_of_waits = timeout_duration / sleep_duration

        # packet_dict["frame_number"]=str(frame_number)
        # packet_dict["face_count"]=str(num_faces)
        # packet_dict["locations_tl"]=str(locations_tl)
        # packet_dict["locations_br"]=str(locations_br)
        # packet_dict["names"]=str(names)

def getFrame(conn):
    frame = bytes(0)
    frmlngth = conn.recv(BUFFER_SIZE).decode()
    if str(frmlngth) != "finito":
        frmlngth = int(frmlngth)
    # confirm frame length was received
        conn.send('got_len'.encode())
        #print('Expected length:', frmlngth)
        while frmlngth > 0:
            data = conn.recv(BUFFER_SIZE)
            frame += data
            frmlngth -= len(data)
        #print('lngth received:', len(frame))
        # confirm that frame was received
        conn.send('success'.encode())

        return 1, frame
    else:
        return 0, 0


def receive_video():
    frame_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    frame_socket.bind((TCP_IP, FRAME_PORT))
    print('Listening on Frame Socket\n')
    frame_socket.listen(1)

    frame_conn, frame_addr = frame_socket.accept()
    print('Frame Connected. address: ' + str(frame_addr) + '\n')
    frame_counter = 0
    repeat = True
    while repeat:
        ret, frame = getFrame(frame_conn)
        if not ret:
            break
        frame = pickle.loads(frame)
        frame_queue.append(frame)
    print("Client has finished sending frames.\n")
    frame_socket.close()



def process_frames():
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((TCP_IP, DATA_PORT))
    print('Listening on Data Socket\n')
    data_socket.listen(1)

    data_conn, data_addr = data_socket.accept()

    print("Data Connected. address " + str(data_addr) + '\n')
    tester = detect_trackClass.faceTracker()
    frame_counter = 0
    loop_repeat = True
    while loop_repeat:
        timeout_counter = 0
        if (len(frame_queue) > 0):
            frame_counter += 1
            frame_to_process = frame_queue.popleft()
            num_faces, face_locs_tl, face_locs_br, face_names = tester.detectAndTrackMultipleFaces(frame_to_process)
            if num_faces > 0:
                #for z in range(0, num_faces):
                   # print("I found " + face_names[z] + " at " + str(
                   #     face_locs_tl[z]) + ' on frame number ' + str(frame_counter) + '\n')
                newpacket = data_packet.data_packet(frame_counter, num_faces, face_locs_tl, face_locs_br, face_names)
                #cv2.rectangle(frame_to_process,face_locs_tl[0],face_locs_br[0],(0,0,200))
                #cv2.imshow("test", frame_to_process)
                #cv2.waitKey(1)
            else:
                newpacket = data_packet.data_packet(frame_counter, 0, [], [], [])
                #print("I found no one on frame number " +
                #      str(frame_counter) + '\n')

            encoded_packet = pickle.dumps(newpacket)
            data_conn.sendall(encoded_packet)
            #thing = time.time()
            #print("Sent a packet at " + str(thing) + '\n')
            recv = data_conn.recv(BUFFER_SIZE)
        else:
            time.sleep(sleep_duration)
            timeout_counter += 1
            if timeout_counter == number_of_waits:
                loop_repeat = False
                print("Time out reached")
    data_conn.close()


thread_recframes = Thread(target=receive_video)
thread_recframes.start()

thread_displayframes = Thread(target=process_frames)
thread_displayframes.start()
