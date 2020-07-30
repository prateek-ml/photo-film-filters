import cv2
import numpy as np
import time

### Abstracting a video stream ###
class CaptureManager(object):

    def __init__(self, capture, previewWindowManager = None, shouldMirrorPreview = False):

        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview

        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None
        self._imageFileName = None
        self._videoFileName = None
        self._videoEncoding = None
        self._videoWriter = None

        self._startTime = None
        self._framesElapsed = 0.0
        self._fpsEstimate = None

    @property
    def channel(self):
            return self._channel
        
    @channel.setter
    def channel(self, value):
            if self._channel != value:
                self._channel = value
                self._frame = None
    @property
    def frame(self):
            if self._enteredFrame and self._frame is None:
                _, self._frame = self._capture.read()
            return self._frame

    @property
    def isWritingImage(self):
            return self._imageFileName is not None
        
    @property
    def isWritingVideo(self):
            return self._videoFileName is not None

    def enterFrame(self):
            """Capture the next frame, if any."""

            #Let's first check if previous frame was exited
            assert not self._enteredFrame, 'Previous enterFrame() had no matching exitFrame()'

            if self._capture is not None:
                self._enteredFrame = self._capture.grab()
        
    def exitFrame(self):
            """Draw to the window. Write to files. Release the frames."""

            #Check whether any grabbed frame is retrievable.
            #The getter may retrieve and cache the frame.
            if self._frame is None:
                self._enteredFrame = False
                return
     
            #Update the FPS estimate and related variables
            if self._framesElapsed == 0:
                self._startTime = time.time()
            else:
                timeElapsed = time.time() - self._startTime
                self._fpsEstimate = self._framesElapsed / timeElapsed
            self._framesElapsed += 1

            #Draw to window, if any
            if self.previewWindowManager is not None:
                if self.shouldMirrorPreview:
                    mirroredFrame = np.fliplr(self._frame).copy()
                    self.previewWindowManager.show(mirroredFrame)
                else:
                    self.previewWindowManager.show(self._frame)

            #Draw to image file, if any
            if self.isWritingImage:
                cv2.imwrite(self._imageFileName, self._frame)
                self._imageFileName = None
            
            #Write to video file, if any
            self._writeVideoFrame()

            #Release the frame
            self._frame = None
            self._enteredFrame = None
        
    def writeImage(self, filename):
            """Write the next exited frame to an image file."""
            self._imageFileName = filename
        
    def startWritingVideo(self, filename, encoding=cv2.VideoWriter_fourcc('m','p','4','v')):
            """Start writing exited frames to a video file."""
            self._videoFileName = filename
            self._videoEncoding = encoding
        
    def stopWritingVideo(self):
            """Stop writing exited frames to a video file."""
            self._videoFileName = None
            self._videoEncoding = None
            self._videoWriter = None
    
    def _writeVideoFrame(self):

        if not self.isWritingVideo:
            return
        
        if self._videoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            if fps == 0.0:
                # The FPS is unknown, so we use an estimate
                if self._framesElapsed < 20:
                    # Wait until more frames elapse so that
                    # estimate is more stable
                    return
                else:
                    fps = self._fpsEstimate
            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
            int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
            self._videoWriter = cv2.VideoWriter(self._videoFileName, self._videoEncoding, 20.0, size)

            self._videoWriter.write(self._frame)

# Abstracting a window and keyboard
class WindowManager(object):

    def __init__(self, windowName, keyPressCallback=None):
        self.keyPressCallback = keyPressCallback

        self._windowName = windowName
        self._isWindowCreated = False
    
    @property
    def isWindowCreated(self):
        return self._isWindowCreated
    
    def createWindow(self):
        cv2.namedWindow(self._windowName)
        self._isWindowCreated = True
    
    def show(self, frame):
        cv2.imshow(self._windowName, frame)
    
    def destroyWindow(self):
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False
    
    def processEvents(self):
        keycode = cv2.waitKey(1)
        if self.keyPressCallback is not None and keycode != -1:
            # Discard any non-ASCII info
            keycode &= 0xFF
            self.keyPressCallback(keycode)
