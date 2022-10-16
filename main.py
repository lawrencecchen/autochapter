import cv2 as cv


# https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html
def process(video_url: str):
  cap = cv.VideoCapture(video_url)
  while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cv.imshow('frame', gray)
    if cv.waitKey(1) == ord('q'):
        break