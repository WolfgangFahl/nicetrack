'''
Created on 2023-08-16

@author: wf
'''
from nicesrt.srt import SRT
from tests.basetest import Basetest

class Test_SRT(Basetest):

    def test_srt(self):
        srt_text="""1
00:00:00,000 --> 00:00:00,033
<font size="28">SrtCnt : 1, DiffTime : 33ms
2023-08-15 09:18:24.589
[iso : 200] [shutter : 1/180.0] [fnum : 170] [ev : 1.3] [ct : 5490] [color_md : default] [focal_len : 240] [dzoom_ratio: 10000, delta:0],[latitude: 48.486375] [longitude: 8.375567] [rel_alt: 0.000 abs_alt: 530.095] </font>

2
00:00:00,033 --> 00:00:00,066
<font size="28">SrtCnt : 2, DiffTime : 33ms
2023-08-15 09:18:24.622
[iso : 200] [shutter : 1/180.0] [fnum : 170] [ev : 1.3] [ct : 5490] [color_md : default] [focal_len : 240] [dzoom_ratio: 10000, delta:0],[latitude: 48.486375] [longitude: 8.375566] [rel_alt: 0.000 abs_alt: 530.095] </font>

3
00:00:00,066 --> 00:00:00,100
<font size="28">SrtCnt : 3, DiffTime : 34ms
2023-08-15 09:18:24.655
[iso : 200] [shutter : 1/180.0] [fnum : 170] [ev : 1.3] [ct : 5490] [color_md : default] [focal_len : 240] [dzoom_ratio: 10000, delta:0],[latitude: 48.486375] [longitude: 8.375566] [rel_alt: 0.000 abs_alt: 530.095] </font>
"""
        # Load the SRT text using the from_text classmethod
        srt = SRT.from_text(srt_text)
    
        # Extract the latitude and longitude from the first subtitle
        lat1 = float(srt.extract_value(0, "latitude"))
        lon1 = float(srt.extract_value(0, "longitude"))
    
        self.assertAlmostEqual(lat1, 48.486375, delta=0.000001)
        self.assertAlmostEqual(lon1, 8.375567, delta=0.000001)