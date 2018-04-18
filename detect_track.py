#!/usr/bin/python
'''
    Author: Guido Diepen <gdiepen@deloitte.nl>
'''

import cv2
import dlib
import time
import pickle
import threading
import face_rec2
import face_recognition
from imutils import face_utils
from PIL import Image, ImageTk
import tkinter

#Operation Variables
score_min_to_track = -1
score_max_to_ID = -0.5
scale_down_factor = 1
face_pool_size = 5
update_tracker = 10
tracking_strictness = 6


class face_info:
    def __init__(self):
        self.identified = False
        self.faceTracker = 0
        self.name = "Who?"
        self.queuecount = 0
        self.queuescoremax = -5
        self.queuebestface = 0
        self.ID = 0
    def reset_queue(self):
        self.queuebestface = 0
        self.queuescoremax = -5
        self.queuecount = 0



def detectAndTrackMultipleFaces():
    #Initialize a face cascade using the frontal face haar cascade provided with
    #the OpenCV library
    #Make sure that you copy this file from the opencv project to the root of this
    #project folder

    previously_found_names = []
    previously_found_encodings = []



    classifier_model_path="C:/Users/Matthew/Documents/SCHOOL/SuperSenior/ENEE408G/FinalProj/knn/trained_knn_model.txt"
    landmark_predictor_path = "C:/Users/Matthew/Documents/SCHOOL/SuperSenior/ENEE408G/FinalProj/knn/shape_predictor_5_face_landmarks.dat"
    faceCascade = cv2.CascadeClassifier('C:/Users/Matthew/Anaconda3/Library/etc/haarcascades/haarcascade_frontalface_default.xml')
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(landmark_predictor_path)
    #The deisred output width and height
    OUTPUT_SIZE_WIDTH = 900
    OUTPUT_SIZE_HEIGHT = 800

    with open(classifier_model_path, 'rb') as f:
        knn_clf = pickle.load(f)
    found_face_id = 0
    Onscreen_Faces = []

    capture = cv2.VideoCapture("C:/Users/Matthew/Documents/SCHOOL/SuperSenior/ENEE408G/FinalProj/Clips/gatesjobs.mp4")
    video_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    print ("This video is " + str(video_width) + 'x' + str(video_height))
    fps = capture.get(cv2.CAP_PROP_FPS)
    spf = float(1/fps)

    cv2.namedWindow("base-image", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("result-image", cv2.WINDOW_AUTOSIZE)

    #Position the windows next to eachother
    cv2.moveWindow("base-image",0,100)
    cv2.moveWindow("result-image",400,100)

    #Start the window thread for the two windows we are using
    cv2.startWindowThread()

    #The color of the rectangle we draw around the face
    rectangleColor = (0,165,255)

    #variables holding the current frame number and the current faceid
    frameCounter = 0


    time_start_loop = time.time()
    time_last = time_start_loop
    showit = False
    try:
        while True:

            rc, fullSizeBaseImage = capture.read()

            if not rc:
                break

            baseImage = cv2.resize(fullSizeBaseImage, (0,0), fx=1/scale_down_factor, fy=1/scale_down_factor)
            baseImage = cv2.resize(fullSizeBaseImage,(890,500))
            gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)

            pressedKey = cv2.waitKey(1)
            if pressedKey == ord('q'):
                break
            if pressedKey == ord('y'):
                showit = not showit


            resultImage = baseImage.copy()

            #STEPS:
            # * Update all trackers and remove the ones that are not
            #   relevant anymore
            # * Every 10 frames:
            #       + Use face detection on the current frame and look
            #         for faces.
            #       + For each found face, check if centerpoint is within
            #         existing tracked box. If so, nothing to do
            #       + If centerpoint is NOT in existing tracked box, then
            #         we add a new tracker with a new face-id


            #Increase the framecounter
            frameCounter += 1

            #Update all the trackers and remove the ones for which the update
            #indicated the quality was not good enough
            fidsToDelete = []
            for fid,Onscreen_Face in enumerate(Onscreen_Faces):

                trackingQuality = Onscreen_Face.faceTracker.update( baseImage )

                #If the tracking quality is not good enough, we must delete
                #this tracker
                if trackingQuality < tracking_strictness:
                    fidsToDelete.append( fid )

            for fid in fidsToDelete:

                if (len(Onscreen_Faces)-1 >= fid):
                    print("Removing fid " + str(fid) + " from list of trackers")
                    Onscreen_Faces.pop( fid )
                else:
                    print("Trying to delete index " + str(fid) + ', but length of Onscreen_Faces is only ' + str(len(Onscreen_Faces)) + '\n')
                    for fid,Onscreen_Face in enumerate(Onscreen_Faces):
                        print(str(fid) + ': ' + Onscreen_Face.name + '\n')
                    time.sleep(10)

            if (frameCounter % update_tracker) == 0:

                rects, scores, idx = detector.run(gray, 0, 0)
                #faces = faceCascade.detectMultiScale(gray, 1.3, 5)
                # for (_x,_y,_w,_h) in faces:
                #     x = int(_x)
                #     y = int(_y)
                #     w = int(_w)
                #     h = int(_h)
                for o, rect in enumerate(rects):
                    #if True:
                    if (scores[0] > score_min_to_track):
                        (x, y, w, h) = face_utils.rect_to_bb(rect)

                        x_bar = x + 0.5 * w
                        y_bar = y + 0.5 * h

                        matchedFid = None

                    #Now loop over all the trackers and check if the
                    #centerpoint of the face is within the box of a
                    #tracker

                        for fid,Onscreen_Face in enumerate(Onscreen_Faces):
                            tracked_position =  Onscreen_Face.faceTracker.get_position()

                            t_x = int(tracked_position.left())
                            t_y = int(tracked_position.top())
                            t_w = int(tracked_position.width())
                            t_h = int(tracked_position.height())

                            t_x_bar = t_x + 0.5 * t_w
                            t_y_bar = t_y + 0.5 * t_h

                        #check if the centerpoint of the face is within the
                        #rectangleof a tracker region. Also, the centerpoint
                        #of     the tracker region must be within the region
                        #detected as a face. If both of these conditions hold
                        #we have a match
                            if ( ( t_x <= x_bar   <= (t_x + t_w)) and
                                ( t_y <= y_bar   <= (t_y + t_h)) and
                                ( x   <= t_x_bar <= (x   + w  )) and
                                ( y   <= t_y_bar <= (y   + h  ))):
                                matchedFid = fid


                    #If no matched fid, then we have to create a new tracker
                        if matchedFid is None:

                            #shape = predictor(gray,dlib.rectangle(int(x),int(y),int(x+w),int(y+h)))
                            #shape = face_utils.shape_to_np(shape)

                            #if (len(shape) == 5):
                            if True:

                                found_face_id += 1
                                print("Creating new tracker " + str(found_face_id))
                            #Create and store the tracker
                                tracker = dlib.correlation_tracker()

                                r = face_info()
                                r.faceTracker = tracker
                                r.ID = found_face_id
                                Onscreen_Faces.append(r)
                                Onscreen_Faces[-1].faceTracker.start_track(baseImage, dlib.rectangle(x-10,y-20,x+w+10,y+h+20))
                                #cv2.imshow("ADD_TRACKER", baseImage[y:y+h,x:x+w])
            #Now loop over all the trackers we have and draw the rectangle
            #around the detected faces. If we 'know' the name for this person
            #(i.e. the recognition thread is finished), we print the name
            #of the person, otherwise the message indicating we are detecting
            #the name of the person
            for fid,Onscreen_Face in enumerate(Onscreen_Faces):
                tracked_position =  Onscreen_Face.faceTracker.get_position()

                t_x = int(tracked_position.left())
                t_y = int(tracked_position.top())
                t_w = int(tracked_position.width())
                t_h = int(tracked_position.height())

                cv2.putText(resultImage, Onscreen_Face.name ,
                            (int(t_x), int(t_y+t_h/2)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 0, 255), 2,2)
                cv2.rectangle(resultImage, (t_x,t_y),(t_x+t_w,t_y+t_h),(0,0,255))

                if not Onscreen_Face.identified:

                    starty = t_y
                    endy = (t_y+t_h)
                    startx = t_x
                    endx = (t_x+t_w)

                    rects, scores, idx = detector.run(baseImage[starty:endy,startx:endx], 0, 0)

                    for rect in rects:
                        Onscreen_Face.queuecount += 1

                        if scores[0] > Onscreen_Face.queuescoremax:

                            Onscreen_Face.queuescoremax = scores[0]

                            (x,y,w,h) = face_utils.rect_to_bb(rect)
                            if x<0:
                                x=0
                            if y<0:
                                y=0
                            top = starty+y
                            bottom= top+h
                            left= startx+x
                            right = left + w

                            Onscreen_Face.queuebestface = baseImage[top:bottom,left:right]
                            # if showit:
                            #     cv2.imshow(str(idx[-1]),Onscreen_Face.queuebestface)
                            #     time.sleep(1)

                            #cv2.imshow("NEW_BESTFACE", Onscreen_Face.queuebestface)
                    if (Onscreen_Face.queuecount == face_pool_size):
                        # cv2.imshow("BEST_FACE", Onscreen_Face.queuebestface)
                        # cv2.waitKey(1)
                        # time.sleep(1)
                        if Onscreen_Face.queuescoremax > score_max_to_ID:
                            # Found enough faces, send to Augmentation
                            #cv2.imshow("SEND_TO_AUG", Onscreen_Face.queuebestface)

                            face_to_encode = Onscreen_Face.queuebestface
                            face_to_encode = cv2.resize(face_to_encode,(0,0),fx=2,fy=2)
                            encoded_faces = face_recognition.face_encodings(face_to_encode)


                            for encoded_face in encoded_faces:
                                print("attempting...'\n")
                                if len(previously_found_encodings) > 0:
                                    search_all = face_recognition.compare_faces(previously_found_encodings,encoded_face,0.4)

                                    if True in search_all:
                                        first_match_index = search_all.index(True)
                                        Onscreen_Face.name = previously_found_names[first_match_index]
                                        Onscreen_Face.identified = True
                                        print("Found " + Onscreen_Face.name + " from index " + str(first_match_index) + '\n')
                                if not Onscreen_Face.identified:
                                    prediction = face_rec2.predict(prefound_encodings=encoded_face,knn_clf=knn_clf,voters=5)
                                    for name in prediction:

                                        Onscreen_Face.name = name
                                        Onscreen_Face.identified = True
                                        previously_found_encodings.append(encoded_face)
                                        previously_found_names.append(Onscreen_Face.name)
                                        print("Found " + Onscreen_Face.name + " from model.\n")
                        Onscreen_Face.reset_queue()


            #Since we want to show something larger on the screen than the
            #original 320x240, we resize the image again
            #
            #Note that it would also be possible to keep the large version
            #of the baseimage and make the result image a copy of this large
            #base image and use the scaling factor to draw the rectangle
            #at the right coordinates.

            largeResult = cv2.resize(resultImage,
                                     (OUTPUT_SIZE_WIDTH,OUTPUT_SIZE_HEIGHT))

            #Finally, we want to show the images on the screen
            # cv2.imshow("base-image", baseImage)
            #time_now = time.time()
            #elapsed = float(time_now-time_last)
            #while elapsed < spf:

            #    time_now = time.time()
            #    elapsed = float(time_now-time_last)
            #time_last = time_now
            cv2.imshow("result-image", largeResult)
            # tkimage = ImageTk.PhotoImage(largeResult)
            # id = tkCanvas.create_image(0, 0, image=tkimage)






    #To ensure we can also deal with the user pressing Ctrl-C in the console
    #we have to check for the KeyboardInterrupt exception and break out of
    #the main loop
    except KeyboardInterrupt as e:
        pass

    #Destroy any OpenCV windows and exit the application
    time_end_loop = time.time()
    print("Finished in " + str(time_end_loop - time_start_loop))

    cv2.destroyAllWindows()
    exit(0)


if __name__ == '__main__':

    detectAndTrackMultipleFaces()
