from imutils.video import FileVideoStream
from imutils import face_utils
import imutils
import time
import dlib
import cv2

def run(filepath):
	detector = dlib.get_frontal_face_detector()
	#predictor = dlib.shape_predictor(os.path.join(sys.path[0], "data/")) #ignore for now

	#Start the frame queue
	vs = FileVideoStream(filepath).start()

	#Allow the videostream queue to populate
	time.sleep(1)

	framecounter = 0
	best_frame = 0
	scoremax = 0

	# loop over the frames from the video stream
	while vs.more():

	    # grab the frame from the threaded video stream, resize it to
	    # have a maximum width of 400 pixels, and convert it to
	    # grayscale
	    frame = vs.read()
	    frame = imutils.resize(frame, width=400)
	    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	    # detect faces in the grayscale frame
	    rects, scores, idx = detector.run(gray, 0, 0)
	    # loop over the face detections
	    for i, rect in enumerate(rects):
            # compute the bounding box of the face
	        (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
	        # keep track of the highest scored face
	        if (scores[i] > scoremax):
	            scoremax = scores[i]
	            best_face = frame[bY:bY + bH, bX:bX + bW]
	            best_frame = framecounter
	            #cv2.imshow("BEST_FACE", best_face)

	    framecounter = framecounter + 1


	    # if the q key was pressed, break from the loop
	    key = cv2.waitKey(1) & 0xFF
	    if key == ord("q"):
	        break
	
	#Stop the frame queue
	vs.stop()
	#Swap the R,B values
	best_face = cv2.cvtColor(best_face, cv2.COLOR_BGR2RGB)
	return best_face, best_frame