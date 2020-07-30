import cv2
from managers import WindowManager, CaptureManager
import rects
from trackers import FaceTracker
import filters

class Camera(object):

    def __init__(self):
        self._windowManager = WindowManager('Camer', self.onKeypress)
        self._captureManager = CaptureManager(
            cv2.VideoCapture(0), self._windowManager, True)
        
        self._filters = [filters.BGRPortraCurveFilter(), filters.BGRProviaCurveFilter(), 
                        filters.BGRVelviaCurveFilter(), filters.BGRCrossProcessCurveFilter()]
        self._currentFilter = 0
        self._curveFliter = self._filters[self._currentFilter]
        
        self._faceTracker = FaceTracker()
        self._shoulddrawRects = False
        self._shouldswapFaces = False

    def run(self):
        """Run the main loop"""
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame
            
            #Tracking and swapping faces in a camera feed
            self._faceTracker.update(frame)
            tracked_faces = self._faceTracker.faces
            
            #Updating current filter
            self._curveFliter = self._filters[self._currentFilter]
            filters.strokeEdges(frame, frame)
            self._curveFliter.apply(frame, frame)

            if self._shouldswapFaces:
                rects.swapRects(frame, frame, [tf.faceRect for tf in tracked_faces])
            
            if self._shoulddrawRects:
                self._faceTracker.drawRects(frame)

            self._captureManager.exitFrame()
            self._windowManager.processEvents()
    
    def onKeypress(self, keycode):
        """Handle a keypress
        
        space    -> Take a screenshot.
        tab      -> Start/stop recording a screencast
        escape   -> Quit
        Enter    -> Previous image filter
        Backspace    -> Next image filter
        x        -> Start/stop drawing rectangles
        q        -> Start/stop swapping faces
        """
        if keycode == 32: #space
            self._captureManager.writeImage('screenshot.png')
        elif keycode == 9: #tab
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo('screencast.mp4')
            
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == 13:
            if self._currentFilter != 0:
                self._currentFilter -=1
            else:
                self._currentFilter = 3
        elif keycode == 8:
            if self._currentFilter !=3:
                self._currentFilter += 1
            else:
                self._currentFilter = 0
        elif keycode == 120: #x
            self._shoulddrawRects = not self._shoulddrawRects
        elif keycode == 113: #q
            self._shouldswapFaces = not self._shouldswapFaces

        elif keycode == 27: #escape
            self._windowManager.destroyWindow()
        



if __name__=="__main__":
    Camera().run()


