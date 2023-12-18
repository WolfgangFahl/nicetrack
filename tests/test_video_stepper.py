import os
import numpy as np
import cv2
import time
import unittest
from ngwidgets.basetest import Basetest
from nicetrack.video_stepper import VideoStepper  # Modify this import based on where your VideoStepper class is
from nicetrack.video_stepper_av import VideoStepperAV  # Modify this import based on where your AV-based VideoStepper class is

class TestVideoStepper(Basetest):
    """
    Test the VideoStepper class
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.video_path = "/Volumes/videos/quadrocopter/2023/DJI_0024.MP4"
        self.opencv_stepper = VideoStepper(self.video_path, root_path="/Volumes/videos/quadrocopter/2023/")
        self.pyav_stepper = VideoStepperAV(self.video_path, root_path="/Volumes/videos/quadrocopter/2023/")

    def _test_get_frame(self, stepper):
        if os.path.exists(self.video_path):
            start = time.time()
            frame = stepper.get_frame(5)  # e.g., get the frame of the 5th second
            end = time.time()

            self.assertIsNotNone(frame, "Frame should not be None")
            if isinstance(frame, np.ndarray):
                self.assertTrue(frame.shape[2] == 3, "Frame should have 3 channels (RGB)")

            time_taken = end - start
            return time_taken

    def _test_get_image(self, stepper):
        if os.path.exists(self.video_path):
            start = time.time()
            image_bytes = stepper.get_image(5, img_format="jpg")
            end = time.time()

            self.assertIsNotNone(image_bytes, "Image bytes should not be None")
            image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.assertTrue(isinstance(image, np.ndarray), "Decoded image should be a numpy ndarray")
            self.assertTrue(image.shape[2] == 3, "Decoded image should have 3 channels (RGB)")

            time_taken = end - start
            return time_taken

    @unittest.skipIf(Basetest.inPublicCI(), "queries unreliable wikidata endpoint")
    def test_compare_timing(self):
        """
        """
        opencv_frame_time = self._test_get_frame(self.opencv_stepper)
        pyav_frame_time = self._test_get_frame(self.pyav_stepper)
        opencv_image_time = self._test_get_image(self.opencv_stepper)
        pyav_image_time = self._test_get_image(self.pyav_stepper)

        frame_time_diff = pyav_frame_time - opencv_frame_time
        image_time_diff = pyav_image_time - opencv_image_time

        frame_time_percentage = (frame_time_diff / opencv_frame_time) * 100
        image_time_percentage = (image_time_diff / opencv_image_time) * 100

        print(f"OpenCV Frame Time: {opencv_frame_time:.4f} seconds")
        print(f"PyAV Frame Time: {pyav_frame_time:.4f} seconds")
        print(f"OpenCV Image Time: {opencv_image_time:.4f} seconds")
        print(f"PyAV Image Time: {pyav_image_time:.4f} seconds")

        print(f"Frame Time Difference: {frame_time_diff:.4f} seconds")
        print(f"Image Time Difference: {image_time_diff:.4f} seconds")

        print(f"Frame Time Relative %: {frame_time_percentage:.2f}%")
        print(f"Image Time Relative %: {image_time_percentage:.2f}%")

    def testVersion(self):
        cv_version = cv2.__version__
        debug = self.debug
        if debug:
            print(cv_version)
        major, minor, _ = [int(x) for x in cv_version.split('.')]

        self.assertTrue(
            (major > 4) or (major == 4 and minor >= 8),
            "OpenCV version should be at least 4.8"
        )
