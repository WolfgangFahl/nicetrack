'''
Created on 2023-08-16

@author: wf
'''
import os
from nicetrack.srt import SRT
from ngwidgets.basetest import Basetest
import requests

class Test_SRT(Basetest):
    """
    test SRT class
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def fetch_srt_files_from_github(self, repo_url: str, path: str):
        # Extract user and repo name from the given URL
        parts = repo_url.split("/")
        user, repo = parts[-2], parts[-1]
        
        # Construct the API URL
        api_url = f"https://api.github.com/repos/{user}/{repo}/{path}"
    
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        files = response.json()
        
        srt_files = [file["download_url"] for file in files if file["name"].lower().endswith(".srt")]
        return srt_files

    def test_srt(self):
        """
        test some srt samples 
        """
        srt_samples=[("""1
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
""",3,48.486375,8.375567,0.00001),("""1
00:00:01,000 --> 00:00:02,000
HOME(149.0251,-20.2532) 2017.08.05 14:11:51
GPS(149.0251,-20.2533,16) BAROMETER:1.9
ISO:100 Shutter:60 EV: Fnum:2.2""",1,-20.2533,16,149.0251)]
        # Load the SRT text using the from_text classmethod
        for _i,srt_sample in enumerate(srt_samples):
            srt_text,count,lat,lon,delta=srt_sample
            srt = SRT.from_text(srt_text)
            self.assertEqual(count,len(srt.subtitles))
            srt.debug=True
            geo_path=srt.as_geopath()
            self.assertEqual(count,len(geo_path.path))
            for tp in geo_path.path:        
                self.assertAlmostEqual(tp.lat, lat, delta=delta)
                self.assertAlmostEqual(tp.lon, lon, delta=delta)
                
    def check_sample(self,srt_file_url:str,hint:str,debug:bool=True):
        response = requests.get(srt_file_url)
        response.raise_for_status()

        srt_text = response.text
        file_name = srt_file_url.split('/')[-1]
        return self.check_text(srt_text,hint,file_name,debug)
        
    def check_text(self,srt_text,hint,file_name,debug):
        srt=SRT.from_text(srt_text)
        geo_path=srt.as_geopath()
        total_distance=geo_path.total_distance()
        
        if debug:
            print(f"{hint}:{len(geo_path.path)}:{total_distance:.3f} km:{file_name}")
        return srt
                
    def test_drone_videos(self):
        """
        Test method to check all SRT files from a local test directory.
        """
        # local test - set you own drone videos path here
        dronevideos_path = "/Volumes/videos/quadrocopter/2023"
        
        if os.path.exists(dronevideos_path):
            index=0
            file_list=sorted(os.listdir(dronevideos_path))
            for filename in file_list:
                if filename.endswith(".SRT") and not filename.startswith("._"):
                    index+=1
                    #print(filename)
                    with open(os.path.join(dronevideos_path, filename), 'r', encoding='utf-8') as file:
                        srt_text = file.read()
                        self.check_text(srt_text, hint=f"{index:2}", file_name=filename, debug=True)
                    
    def test_sample(self):
        sample_url="https://raw.githubusercontent.com/JuanIrache/dji-srt-viewer/master/samples/sample4.SRT"
        srt=self.check_sample(sample_url,"sample4",debug=True)
        debug=True
        for index in range(len(srt.subtitles)):
            d=srt.as_dict(index)
            if debug:
                print(f"{index:3}:{d}")
        #self.assertEqual("2018-08-19 08:00:36",str(d))
        
    def test_samples(self):
        """
        test JuanIrache samples
        """
        debug=self.debug
        debug=True
        repo_urls = [
            "https://github.com/JuanIrache/DJI_SRT_Parser",
            "https://github.com/JuanIrache/dji-srt-viewer"]
        for ir,repo_url in enumerate(repo_urls):
            srt_files = self.fetch_srt_files_from_github(repo_url, "contents/samples")
    
            for i,srt_file_url in enumerate(srt_files):
                t=len(srt_files)
                hint=f"{ir+1}:{i+1:2d}/{t:2d}"
                self.check_sample(srt_file_url,hint,debug)
                