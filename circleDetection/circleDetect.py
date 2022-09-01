import numpy as np
import cv2
import sys
import time
sys.path.insert(0, "..")
from camera_opencv import Camera


def detect(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    w,h = gray.shape[::-1]
    
    circle = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1.2,100)
    
    if circle is not None:
        X = []
        Y = []
        R = []
        circles = np.round(circle[0, :]).astype("int")
        for (x,y,r) in circles:
            X.append(x)
            Y.append(y)
            R.append(r)
        return X,Y,R
    else:
        return None, None, None


if __name__ == '__main__':
    cap = Camera()
    while 1:
        zaman = time.time()
        frame = cap.get_frame()
        if frame is not None:
            X,Y,R = detect(frame)
            if X is not None and R is not None:
                for x,y,r in zip(X,Y,R):
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                    cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), 2)

            print("Loop Takes {0} seconds.".format(time.time() - zaman))
            cv2.imshow('circles', frame)
                
            if cv2.waitKey(1) == ord("q"):
                break

    cv2.destroyAllWindows()
        