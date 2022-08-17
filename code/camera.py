import time
import cv2

class camera:
    def __init__(self, port=-1):
        self.vs = cv2.VideoCapture(port, cv2.CAP_V4L)
        self.ret = False
        self.img = None
        self.running = True

    def update(self):
        while self.running:
            self.ret, self.img = self.vs.read()

    def get(self):
        return self.ret, self.img

    def shutdown(self):
        self.running = False
        time.sleep(0.5)
        self.vs.release()
