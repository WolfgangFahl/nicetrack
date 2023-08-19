'''
Created on 2023-08-16

@author: wf
'''
from datetime import datetime
from nicetrack.geo import GeoPath
from typing import Optional
import json
import pysrt
import re
import sys
import traceback


class SRT:
    """
    Class to represent and manipulate SRT (SubRip Subtitle) data.
    
    Attributes:
        subtitles (list): List of parsed subtitles.
    """

    def __init__(self, subtitles, patterns=None, debug:bool=False):
        """
        Initializes the SRT object with the given subtitles and extraction patterns.
        """
        self.subtitles = subtitles
        self.debug = debug
        # Default patterns
        self.patterns = {
            'key_value': r'\[(\w+)\s*:\s*([\d.-]+)\]',
            'double_key_value': r'\[(\w+)\s*:\s*([\d.-]+)\s+(\w+)\s*:\s*([\d.-]+)\]',
            'bracketed_value': r'(\w+)\(([\d.-]+),([\d.-]+)(?:,([\d.-]+))?\)'
        }

        if patterns:
            self.patterns.update(patterns)

    @classmethod
    def from_text(cls, text):
        """
        Class method to create an SRT object from a raw text string.
        """
        subtitles = pysrt.from_string(text)
        return cls(subtitles)
    
    def handle_exception(self, e: BaseException, trace: Optional[bool] = False):
        """Handles an exception by creating an error message.

        Args:
            e (BaseException): The exception to handle.
            trace (bool, optional): Whether to include the traceback in the error message. Default is False.
        """
        if trace:
            error_msg = str(e) + "\n" + traceback.format_exc()
        else:
            error_msg = str(e)
        if self.debug:
            print(error_msg,file=sys.stderr)
    
    def as_dict(self,index: int) -> dict:
        """
        convert the subtitle at the given index to a dict
        """
        if index < len(self.subtitles):
            s = self.subtitles[index].text
        if "<font" in s:
            d=self.as_dji_dict(s)
        else:
            d=self.as_srt_dict(s)
        d=self.as_unified_dict(d)
        return d
    
    def as_unified_dict(self, data_dict: dict) -> dict:
        unified_dict = {}
    
        # Key look-up map along with their respective type-casting functions
        lookup = {
            "lat": (["latitude", "gps_latitude"], float),
            "lon": (["longitude", "gps_longitude"], float),
            "elevation": (["abs_alt", "barometer"], float),
            "timestamp": (["timestamp"], None)
        }
    
        for unified_key, (possible_keys, type_case) in lookup.items():
            for key in possible_keys:
                if key in data_dict:
                    value = data_dict[key]
                    if type_case:
                        if value:
                            value = type_case(value)
                    unified_dict[unified_key] = value
                    break  # Break once we've found the first matching key
    
        return unified_dict



    def as_dji_dict(self,s: str) -> dict:
        """
        Convert a provided string with timestamps and metadata into a dictionary.
        
        Parameters:
            s (str): Input string with timestamps and metadata.
            
        Returns:
            dict: Dictionary with extracted data.
        
        Example:
        --------
        s = '''00:00:00,000 --> 00:00:00,033
        <font size="28">SrtCnt : 1, DiffTime : 33ms
        2023-08-15 09:18:24.589
        [iso : 200] [shutter : 1/180.0] [fnum : 170] [ev : 1.3] [ct : 5490] 
        [color_md : default] [focal_len : 240] [dzoom_ratio: 10000, delta:0],
        [latitude: 48.486375] [longitude: 8.375567] [rel_alt: 0.000 abs_alt: 530.095] </font>'''
        
        result = as_dji_dict(s)
        print(result)
        """
    
        # Extract SrtCnt and DiffTime
        srtcnt_pattern = r"SrtCnt : (\d+)"
        difftime_pattern = r"DiffTime : (\d+ms)"
        
        srtcnt = re.search(srtcnt_pattern, s).group(1) if re.search(srtcnt_pattern, s) else None
        difftime = re.search(difftime_pattern, s).group(1) if re.search(difftime_pattern, s) else None
    
        # Extract the main timestamp
        main_timestamp_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})"
        main_timestamp = re.search(main_timestamp_pattern, s).group(1) if re.search(main_timestamp_pattern, s) else None
    
        # Extract the start and end timestamps
        timestamp_pattern = r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})"
        timestamp_match = re.search(timestamp_pattern, s)
        start_time = timestamp_match.group(1) if timestamp_match else None
        end_time = timestamp_match.group(2) if timestamp_match else None
    
        # Extract metadata enclosed within square brackets
        metadata_pattern = r"\[(.*?)\]"
        metadata_matches = re.findall(metadata_pattern, s)
        metadata_dict = {}
        for match in metadata_matches:
            # Handling for rel_alt and abs_alt specifically
            if "rel_alt" in match and "abs_alt" in match:
                rel_alt_match = re.search(r"rel_alt:\s*([-+]?\d*\.\d+|\d+)", match)
                abs_alt_match = re.search(r"abs_alt:\s*([-+]?\d*\.\d+|\d+)", match)
                if rel_alt_match:
                    metadata_dict['rel_alt'] = float(rel_alt_match.group(1))
                if abs_alt_match:
                    metadata_dict['abs_alt'] = float(abs_alt_match.group(1))
                continue
    
            # Splitting the rest of the metadata
            metadata_split = match.split(":")
            if len(metadata_split) >= 2:
                key = metadata_split[0].strip()
                if len(metadata_split) == 2:
                    value = metadata_split[1].strip()
                else:
                    value = ":".join(metadata_split[1:]).strip()
                metadata_dict[key] = value
    
        # Adding additional metadata to the dictionary
        metadata_dict['start_time'] = start_time
        metadata_dict['end_time'] = end_time
        metadata_dict['SrtCnt'] = int(srtcnt) if srtcnt else None
        metadata_dict['DiffTime'] = difftime
        metadata_dict['timestamp_str'] = main_timestamp
        metadata_dict['timestamp'] = datetime.strptime(main_timestamp, "%Y-%m-%d %H:%M:%S.%f") if main_timestamp else None
        
        return metadata_dict

   
    def as_srt_dict(self,s:str) -> dict:
        """
        Convert SRT format to dict.
        
        Parameters:
            s (str): Input string in SRT format containing metadata.
        
        Returns:
            dict: Dictionary representation of the input metadata.
        
        Example:
        --------
        s = '''1
        00:00:01,000 --> 00:00:02,000
        HOME(149.0251,-20.2532) 2017.08.05 14:11:51
        GPS(149.0251,-20.2533,16) BAROMETER:1.9
        ISO:100 Shutter:60 EV: Fnum:2.2'''
        
        result = as_srt_dict(s)
        print(result)
        """
        # Regular expression to capture key-value pairs
        pattern = r'(\w+):\s*([\d.]+)'
        
        # Find all key-value pairs
        kv_matches = re.findall(pattern, s)
        
        # Extract HOME and GPS data
        home_match = re.search(r'HOME\(([-\d.]+),([-\d.]+)\)', s)
        gps_match = re.search(r'GPS\(([-\d.]+),([-\d.]+),([\d.]+)\)', s)
        
        # Extract timestamp
        date_match = re.search(r'(\d{4}.\d{2}.\d{2} \d{2}:\d{2}:\d{2})', s)
        
        # Build the initial data dictionary
        data = {
            'home_latitude': float(home_match.group(2)) if home_match else None,
            'home_longitude': float(home_match.group(1)) if home_match else None,
            'gps_latitude': float(gps_match.group(2)) if gps_match else None,
            'gps_longitude': float(gps_match.group(1)) if gps_match else None,
            'gps_3': float(gps_match.group(3)) if gps_match else None,
            'timestamp': datetime.strptime(date_match.group(1), "%Y.%m.%d %H:%M:%S") if date_match else None,
        }
        
        # Append additional key-value pairs to the data dictionary
        for key, value in kv_matches:
            # Convert the string value to its appropriate type (integer or float)
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # keep it as string if conversion fails
            
            # Add to the data dictionary
            data[key.lower()] = value
        
        return data

    def as_geopath(self) -> GeoPath:
        """
        Converts the SRT object into a GeoPath object by extracting latitudes and longitudes.
        """
        geo_path = GeoPath()
        
        for index in range(len(self.subtitles)):
            try:
                d=self.as_dict(index)
                if self.debug:
                    print(json.dumps(d,indent=2,default=str))
                lat=d.get("lat")
                lon=d.get("lon")
                elevation=d.get("elevation")
                timestamp=d.get("timestamp")  
                if lat and lon:  
                    geo_path.add_point(lat, lon, elevation, timestamp)
            except BaseException as ex:
                self.handle_exception(ex, trace=self.debug)

        return geo_path

        
