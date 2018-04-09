from imutils.video import FileVideoStream
from imutils import face_utils
import imutils
import time
import dlib
import cv2


class BF_object:
    def __init__(self):
    	self.maxframes = 0
    	self.framecounter = 0

    def get_progress(self):
        return self.framecounter
    
    def get_maxframes(self):
    	return self.maxframes

    def run(self, filepath):
        detector = dlib.get_frontal_face_detector()
        # predictor = dlib.shape_predictor(os.path.join(sys.path[0], "data/")) #ignore for now

        # Start the frame queue
        vs = FileVideoStream(filepath)

        if (not vs.stream.isOpened()):
            return 0,0

        self.maxframes = int(vs.stream.get(cv2.CAP_PROP_FRAME_COUNT))
        
        vs.start()
        best_frame = 0
        scoremax = 0

        self.framecounter = 0
        # loop over the frames from the video stream
        while (self.framecounter < self.maxframes):

            # grab the frame from the threaded video stream, resize it to
            # have a maximum width of 400 pixels, and convert it to
            # grayscale
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # detect faces in the grayscale frame
            rects, scores, idx = detector.run(gray, 0, 0)
            # loop over the face detections
            self.framecounter = self.framecounter + 1

            for i, rect in enumerate(rects):
                # compute the bounding box of the face
                (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
                # keep track of the highest scored face
                if (scores[i] > scoremax):
                    scoremax = scores[i]
                    best_face = frame[bY:bY + bH, bX:bX + bW]
                    best_frame = self.framecounter
                    #cv2.imshow("BEST_FACE", best_face)

            

            # if the q key was pressed, break from the loop
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        # Stop the frame queue
        vs.stop()


        if (best_frame == 0):
            #If no face was found
            best_face = 0
        else:
            # Swap the R,B values
            best_face = cv2.cvtColor(best_face, cv2.COLOR_BGR2RGB)
        return best_face, best_frame
