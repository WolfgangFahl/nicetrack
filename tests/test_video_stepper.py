import os
import numpy as np
import cv2
from tests.basetest import Basetest
from nicetrack.video_stepper import VideoStepper  # Modify this import based on where your VideoStepper class is

class TestVideoStepper(Basetest):
    """
    Test the VideoStepper class
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.video_path = "/Volumes/videos/quadrocopter/2023/DJI_0024.MP4"
    
    def test_get_frame(self):
        if os.path.exists(self.video_path):
            self.stepper = VideoStepper(self.video_path, root_path="/Volumes/videos/quadrocopter/2023/")
            frame = self.stepper.get_frame(5)  # e.g., get the frame of the 5th second
            self.assertIsNotNone(frame, "Frame should not be None")
            self.assertTrue(isinstance(frame, np.ndarray), "Frame should be a numpy ndarray")
            self.assertTrue(frame.shape[2] == 3, "Frame should have 3 channels (RGB)")

    def test_get_image(self):
        if os.path.exists(self.video_path):
            self.stepper = VideoStepper(self.video_path, root_path="/Volumes/videos/quadrocopter/2023/")
            image_bytes = self.stepper.get_image(5, img_format="jpg")
            self.assertIsNotNone(image_bytes, "Image bytes should not be None")
            # Decoding the image bytes to check if it's a valid image
            image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.assertTrue(isinstance(image, np.ndarray), "Decoded image should be a numpy ndarray")
            self.assertTrue(image.shape[2] == 3, "Decoded image should have 3 channels (RGB)")

    def testVersion(self):
        cv_version=cv2.__version__
        debug=self.debug
        if debug:
            print(cv_version)
        major, minor, _ = [int(x) for x in cv_version.split('.')]
    
        self.assertTrue(
            (major > 4) or (major == 4 and minor >= 8),
            "OpenCV version should be at least 4.8"
        )
