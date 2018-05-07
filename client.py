from threading import Thread
from PIL import Image, ImageTk
import cv2
import os
import socket
import pickle
import threading
from collections import deque
import data_packet
import time

BUFFER_SIZE = 1024
skip_rate = 2

def prepare_frame(frm, data):
    for i in range(data.face_count):
        tl = data.locations_tl[i]
        br = data.locations_br[i]
        name = data.names[i]
        cv2.putText(frm, name, (int(tl[0]), int(tl[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2,2)
        cv2.rectangle(frm, tl,br,(0,0,255))
    return frm

class clientcxn:
    def __init__(self, IP, port1, port2):
        self.TCP_IP = IP
        self.TCP_PORT1 = port1
        self.TCP_PORT2 = port2
        self.frmSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.frameQueue = deque() # list of all frames sent not yet played back
        self.dataQueue = deque()
        self.frmIdx = 0
        self.__cxnstatus = 0 # disconnected



    def getStatus(self):
        return self.__cxnstatus

    def __connect(self):
        try:
            print('Establishing frame connection...')
            self.frmSock.connect((self.TCP_IP, self.TCP_PORT1))
            print('Frame connection established')
            print('Establishing data connection...')
            self.dataSock.connect((self.TCP_IP, self.TCP_PORT2))
            print('Data connection established')
            self.__cxnstatus = 1 # connected
            return True
        except OSError as e:
            print('Failed to establish connection')
            self.__cxnstatus = -1 # error status
            return False

    def createCxn(self):
        # tgt = self.__connect
        # t = threading.Thread(target=tgt)
        # t.start()
        try:
            print('Establishing frame connection...')
            self.frmSock.connect((self.TCP_IP, self.TCP_PORT1))
            print('Frame connection established')
            print('Establishing data connection...')
            self.dataSock.connect((self.TCP_IP, self.TCP_PORT2))
            print('Data connection established')
            self.__cxnstatus = 1 # connected
            return True
        except OSError as e:
            print('Failed to establish connection')
            self.__cxnstatus = -1 # error status
            return False

    def run(self, video_path):

        tgt1 = self.sendFramesCont
        tgt2 = self.rcvData
        tgt3 = self.play_frames
        t1 = threading.Thread(target=tgt1, args=(video_path,))
        t2 = threading.Thread(target=tgt2)
        t3 = threading.Thread(target=tgt3)
        t1.start()
        t2.start()
        t3.start()


    def sendFrame(self, frm, sock):
        """send length, wait for confirmation, send frame, wait for confirmation"""
        # create frame as bytes
        frm = pickle.dumps(frm)
        # send frame length
        sock.sendall(str(len(frm)).encode())
        # wait for confirmation of frame lenght
        recv = sock.recv(BUFFER_SIZE).decode()
        # send frome
        sock.sendall(frm)
        # wait for confirmation of frame
        recv = sock.recv(BUFFER_SIZE).decode()




    def closeconn(self):
        self.frmSock.close
        self.dataSock.close

    def sendFramesCont(self, video_path):
        capture = cv2.VideoCapture(video_path)
        if video_path == 0:
            time.sleep(2)
        """continuously sends frames to server from given videocapture arg"""

        try:
            while True:
                ret, frame = capture.read()
                if not ret:
                    print('end of video')
                    self.frmSock.sendall('finito'.encode())
                    break
                try:
                    self.frmIdx += 1
                    frame = cv2.resize(frame,(640,480))
                    self.frameQueue.append({"frame": frame, "idx": self.frmIdx})
                    if self.frmIdx % skip_rate == 0:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        self.sendFrame(frame, self.frmSock)


                except (ConnectionAbortedError, ConnectionResetError) as e:
                    print("Cxn was terminated")
                    break
        except KeyboardInterrupt as e:
            return 0

    def rcvData(self):
        """continuously receives data from serve, adds to queue"""
        try:
            while True:

                try:

                    recv = self.dataSock.recv(BUFFER_SIZE)
                    self.dataSock.sendall('verif'.encode())
                    data = pickle.loads(recv)
                    self.dataQueue.append(data)
                    # print("Received frame", data.frame_number)
                except (ConnectionAbortedError, ConnectionResetError) as e:
                    print("Cxn was terminated")
                    break
                except (EOFError) as e:
                    print('error receiving')
        except KeyboardInterrupt as e:
            return 0



    def play_frames(self):
        """playback video"""

        frame_count = 1
        previous_rectangle = False
        previous_rectangle_tl = (0,0)
        previous_rectangle_br = (0,0)
        previous_name = 'none'
        try:
            while True:

                if (len(self.frameQueue) > 0):

                    if (frame_count % skip_rate == 0):
                        #if this is true then we are on a frame that was sent to the server
                        if len(self.dataQueue) > 0:

                            frm = self.frameQueue.popleft()
                            fidx = frm["idx"]
                            frm = frm["frame"]
                            #HI2
                            data = self.dataQueue.popleft()
                            didx = data.frame_number*skip_rate
                            if(didx != fidx):
                                print('indices do not match', fidx, didx)

                            if data.face_count == 0:
                                    previous_rectangle = False
                            for i in range(0,data.face_count):
                                tl = data.locations_tl[i]
                                br = data.locations_br[i]
                                name = data.names[i]
                                cv2.putText(frm, name, (int(tl[0]), int(tl[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2,2)
                                cv2.rectangle(frm, tl,br,(0,0,255))
                                previous_rectangle = True
                                previous_rectangle_tl = tl
                                previous_rectangle_br = br
                                previous_name = name

                            cv2.imshow('video', frm)
                            frame_count += 1
                        else:
                            time.sleep(0.05)
                    else:
                        frame_count += 1
                        frm = self.frameQueue.popleft()
                        frm = frm["frame"]
                        if previous_rectangle:
                            cv2.rectangle(frm,previous_rectangle_tl,previous_rectangle_br,(0,0,255))
                            cv2.putText(frm, previous_name, (int(tl[0]), int(tl[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2,2)
                        cv2.imshow('video', frm)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                else:
                    time.sleep(0.1)

        except KeyboardInterrupt as e:
            return 0






# ip = '10.104.178.225'
# dir = os.getcwd()
# vidPath = dir + "\\Clips\\gatesjobs.mp4"
# capture = cv2.VideoCapture(vidPath)
# cxn = clientcxn(ip, 5005, 5006)
# tgt1 = cxn.sendFramesCont
# tgt2 = cxn.rcvData
# tgt3 = cxn.play_frames
# t1 = threading.Thread(target=tgt1, args=(capture,))
# t2 = threading.Thread(target=tgt2)
# t3 = threading.Thread(target=tgt3)
# t1.start()
# t2.start()
# t3.start()
