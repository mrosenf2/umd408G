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
import os
import platform
#import face_recognition_models

#cnn_face_detector = dlib.cnn_face_detection_model_v1(cnn_face_detection_model)
#Operation Variables
score_min_to_track = -1
score_max_to_ID = -1
scale_down_factor = 1
face_pool_size = 2
update_tracker = 4
tracking_strictness = 6
distance_thresh = 0.5
voters_number = 10
tracking_cap = 2
class face_info:
    def __init__(self):
        self.identified = False
        self.faceTracker = 0
        self.name = "Who?"
        self.queuecount = 0
        self.queuescoremax = -5
        self.queuebestface = 0
        self.ID = 0
        self.frameCounter = 0

    def reset_queue(self):
        self.queuebestface = 0
        self.queuescoremax = -5
        self.queuecount = 0



class faceTracker:
    dir = os.getcwd()
    arch = platform.architecture()
    if arch[0] == '32bit':
        classifier_model_path = dir + "\\knn\\trained_knn_model_32.clf"
    else:
        classifier_model_path = dir + "\\knn\\new_model.txt"

    classifier_model_path = dir + "\\knn-classifiers\\trained_knn_model_faceonly.clf"
    classifier_2_model_path = dir + "\\knn-classifiers\\trained_knn_model_inside_dataset.clf"

    landmark_predictor_path = dir + "\\knn\\shape_predictor_5_face_landmarks.ckn"

    detector = dlib.get_frontal_face_detector()
    # predictor = dlib.shape_predictor(landmark_predictor_path)
    #The deisred output width and height

    with open(classifier_model_path, 'rb') as f:
        knn_clf = pickle.load(f)
    with open(classifier_2_model_path, 'rb') as f:
        knn_clf_2 = pickle.load(f)

    found_face_id = 0
    Onscreen_Faces = []


    #The color of the rectangle we draw around the face


    #variables holding the current frame number and the current faceid
    frameCounter = 0

    def __init__(self):
        #Initialize a face cascade using the frontal face haar cascade provided with the OpenCV library
        #Make sure that you copy this file from the opencv project to the root of this project folder
        self.previously_found_names = []
        self.previously_found_encodings = []
        #self.videoPath = videoPath
        #self.capture = cv2.VideoCapture(self.videoPath)
        #self.video_height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #self.video_width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        #print ("This video is " + str(self.video_width) + 'x' + str(self.video_height))

    def get_dimensions(self):
        return self.video_width, self.video_height

    """method that will take a single frame as input and return a data structure containing information about tracked faces and locations"""
    def detectAndTrackMultipleFaces(self, baseImage):
        #fps = self.capture.get(cv2.CAP_PROP_FPS)
        #spf = float(1/fps)

        time_start_loop = time.time()
        time_last = time_start_loop
        showit = False
        try:
            #rc, fullSizeBaseImage = self.capture.read()
            #Server no longer needs to read from the file - it needs to read from the queue

            #if not rc:
            #    return


            #baseImage = cv2.resize(fullSizeBaseImage, (0,0), fx=1/scale_down_factor, fy=1/scale_down_factor)
            
            #gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)

            gray = baseImage.copy()
            baseImage = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

            #resultImage = baseImage.copy()

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
            self.frameCounter += 1

            #Update all the trackers and remove the ones for which the update
            #indicated the quality was not good enough
            fidsToDelete = []
            for fid,Onscreen_Face in enumerate(self.Onscreen_Faces):

                trackingQuality = Onscreen_Face.faceTracker.update( baseImage )

                #If the tracking quality is not good enough, we must delete
                #this tracker
                if trackingQuality < tracking_strictness:
                    fidsToDelete.append( fid )

            for fid in reversed(fidsToDelete):

                if (len(self.Onscreen_Faces)-1 >= fid):
                    print("Removing fid " + str(fid) + " from list of trackers")
                    self.Onscreen_Faces.pop( fid )
                else:
                    print("Trying to delete index " + str(fid) + ', but length of Onscreen_Faces is only ' + str(len(self.Onscreen_Faces)) + '\n')
                    for fid,Onscreen_Face in enumerate(self.Onscreen_Faces):
                        print(str(fid) + ': ' + Onscreen_Face.name + '\n')
                    

            if (self.frameCounter % update_tracker) == 0:

                rects, scores, idx = self.detector.run(gray, 0, 0)
                #face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")
                #dets = cnn_face_detector()
                tracker_list = []
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

                        for fid,Onscreen_Face in enumerate(self.Onscreen_Faces):
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
                            if len(self.Onscreen_Faces) < tracking_cap:

                                self.found_face_id += 1
                                print("Creating new tracker " + str(self.found_face_id))
                            #Create and store the tracker
                                tracker = dlib.correlation_tracker()

                                r = face_info()
                                r.faceTracker = tracker
                                r.ID = self.found_face_id
                                tracker_list.append(len(self.Onscreen_Faces))
                                self.Onscreen_Faces.append(r)
                                self.Onscreen_Faces[-1].faceTracker.start_track(baseImage, dlib.rectangle(x-10,y-20,x+w+10,y+h+20))

                        else:
                            tracker_list.append(matchedFid)

                for u in range(len(self.Onscreen_Faces)-1,-1,-1):     
                    if u not in tracker_list:
                        print("No face found in tracker " + str(u) + "\n")
                        self.Onscreen_Faces.pop(u)



                                #cv2.imshow("ADD_TRACKER", baseImage[y:y+h,x:x+w])
            #Now loop over all the trackers we have and draw the rectangle
            #around the detected faces. If we 'know' the name for this person
            #(i.e. the recognition thread is finished), we print the name
            #of the person, otherwise the message indicating we are detecting
            #the name of the person
            for fid,Onscreen_Face in enumerate(self.Onscreen_Faces):
                tracked_position =  Onscreen_Face.faceTracker.get_position()

                t_x = int(tracked_position.left())
                t_y = int(tracked_position.top())
                t_w = int(tracked_position.width())
                t_h = int(tracked_position.height())

                # cv2.putText(resultImage, Onscreen_Face.name ,
                #             (int(t_x), int(t_y+t_h/2)),
                #             cv2.FONT_HERSHEY_SIMPLEX,
                #             0.5, (0, 0, 255), 2,2)
                # cv2.rectangle(resultImage, (t_x,t_y),(t_x+t_w,t_y+t_h),(0,0,255))

                if not Onscreen_Face.identified:

                    starty = t_y
                    endy = (t_y+t_h)
                    startx = t_x
                    endx = (t_x+t_w)

                    rects, scores, idx = self.detector.run(baseImage[starty:endy,startx:endx], 0, 0)

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
                            encoded_faces = face_recognition.face_encodings(face_to_encode,num_jitters=5)


                            for encoded_face in encoded_faces:
                                print("attempting...'\n")
                                if len(self.previously_found_encodings) > 0:
                                    search_all = face_recognition.compare_faces(self.previously_found_encodings,encoded_face,0.4)

                                    if True in search_all:
                                        first_match_index = search_all.index(True)
                                        Onscreen_Face.name = self.previously_found_names[first_match_index]
                                        Onscreen_Face.identified = True
                                        print("Found " + Onscreen_Face.name + " from index " + str(first_match_index) + '\n')
                                if not Onscreen_Face.identified:
                                    print("Passing this face to recognition...\n")
                                    # cv2.imshow("FACE_TO_REC",face_to_encode)
                                    # cv2.waitKey(1)
                                    # time.sleep(5)
                                    candidate = face_rec2.predict(prefound_encodings=encoded_face, distance_threshold=distance_thresh, knn_clf=self.knn_clf_2, voters=voters_number)
                                    for name in candidate:
                                        if name == "inside":
                                            prediction = face_rec2.predict(prefound_encodings=encoded_face,distance_threshold=distance_thresh,knn_clf=self.knn_clf,voters=voters_number)
                                            for name in prediction:

                                                Onscreen_Face.name = name
                                                Onscreen_Face.identified = True
                                                self.previously_found_encodings.append(encoded_face)
                                                self.previously_found_names.append(Onscreen_Face.name)
                                                print("Found " + Onscreen_Face.name + " from model.\n")
                                        else:
                                            Onscreen_Face.name = "Unknown"
                                            Onscreen_Face.identified = True
                                            self.previously_found_encodings.append(encoded_face)
                                            self.previously_found_names.append(Onscreen_Face.name)
                                            print("Found " + Onscreen_Face.name + " from model.\n")


                                    
                        Onscreen_Face.reset_queue()


            #Since we want to show something larger on the screen than the
            #original 320x240, we resize the image again
            #
            #Note that it would also be possible to keep the large version
            #of the baseimage and make the result image a copy of this large
            #base image and use the scaling factor to draw the rectangle
            #at the right coordinates.

            #largeResult = cv2.resize(resultImage,
             #                        (self.OUTPUT_SIZE_WIDTH,self.OUTPUT_SIZE_HEIGHT))
            ret_names = []
            for each in self.Onscreen_Faces:
                ret_names.append(each.name)

            ret_locations_tl = []
            ret_locations_br = []
            for each in self.Onscreen_Faces:
                temp_loc = each.faceTracker.get_position()
                loc_tuple_tl = (int(temp_loc.left()),int(temp_loc.top()))
                loc_tuple_br= (int(temp_loc.right()),int(temp_loc.bottom()))
                ret_locations_tl.append(loc_tuple_tl)
                ret_locations_br.append(loc_tuple_br)
            return len(self.Onscreen_Faces), ret_locations_tl, ret_locations_br, ret_names






    #To ensure we can also deal with the user pressing Ctrl-C in the console
    #we have to check for the KeyboardInterrupt exception and break out of
    #the main loop
        except KeyboardInterrupt as e:
            cv2.destroyAllWindows()
            pass
    #
    # #Destroy any OpenCV windows and exit the application
    # time_end_loop = time.time()
    # print("Finished in " + str(time_end_loop - time_start_loop))
    #
    # cv2.destroyAllWindows()
    # exit(0)

if __name__ == '__main__':
    detectAndTrackMultipleFaces()




# number of rectangles,  rectangle locations, names
