'''
Created on 2023-08-30

@author: wf
'''
import cv2
from tests.basetest import Basetest

class TestOpenCV(Basetest):
    """
    test opencv
    """
    
    def testVersion(self):
        print(cv2.__version__)