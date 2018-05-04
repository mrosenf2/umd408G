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
        tgt = self.__connect
        t = threading.Thread(target=tgt)
        t.start()

    def run(self, capture):
        tgt1 = self.sendFramesCont
        tgt2 = self.rcvData
        tgt3 = self.play_frames
        t1 = threading.Thread(target=tgt1, args=(capture,))
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

    def sendFramesCont(self, capture):
        """continuously sends frames to server from given videocapture arg"""
        try:
            while True:
                ret, frame = capture.read()
                frame = cv2.resize(frame,(560,315))
                if not ret:
                    print('end of video')
                    frmSock.sendall('finito'.encode())
                    break
                try:
                    frame = cv2.resize(frame,(640,480))
                    self.frmIdx += 1
                    # self.frameQueue.append({"frame": frame, "idx": self.frmIdx})
                    self.frameQueue.append(frame)
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
        time.sleep(2)
        try:
            while True:
                if (len(self.dataQueue) > 0 and len(self.frameQueue) > 0):
                    frm = self.frameQueue.popleft()
                    # fidx = frm["idx"]
                    # frm = frm["frame"]
                    data = self.dataQueue.popleft()
                    didx = data.frame_number
                    # if(didx != fidx):
                    #     print('indexes do not match', fidx, didx)

                    image = prepare_frame(frm, data)
                    cv2.imshow('frame', image)
                    cv2.waitKey(1)

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
