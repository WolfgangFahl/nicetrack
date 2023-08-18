'''
Created on 16.08.2023

@author: wf
'''
from typing import List, Tuple
import math
import logging
import os
from nicesrt.version import Version
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.cachingStrategy import CachingStrategy,JSON
from pathlib import Path

class GeoPath:
    """
    a 3D Path of geographic coordinates in lat/lon notation
    """
    def __init__(self,name:str=None,cacheDir:str=None):
        self.name=name
        self.path: List[Tuple[float, float]] = []
        if cacheDir is None:
            home = str(Path.home())
            cacheDir=f"{home}/.nominatim"     
        self.cacheDir=cacheDir
        if not os.path.exists(self.cacheDir):
            os.makedirs(cacheDir)
        logging.getLogger('OSMPythonTools').setLevel(logging.ERROR)     
        CachingStrategy.use(JSON, cacheDir=cacheDir)
        self.nominatim = Nominatim()  

    def add_point(self, lat: float, lon: float) -> None:
        """Add a point to the geo path."""
        self.path.append((lat, lon))

    def get_path(self) -> List[Tuple[float, float]]:
        """Return the path."""
        return self.path
    
    def haversine_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate the Haversine distance between two points."""
        # Radius of the Earth in kilometers
        R = 6371.0

        # Convert degrees to radians
        lat1 = math.radians(point1[0])
        lon1 = math.radians(point1[1])
        lat2 = math.radians(point2[0])
        lon2 = math.radians(point2[1])

        # Differences in coordinates
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance in kilometers
        distance = R * c
        return distance
    
    def validate_index(self,index:int):
        max_index=len(self.path)-1
        if index < 0 or index >max_index:
            raise ValueError(f"Invalid index {index}: valid range is 0-{max_index}")

    def distance(self, index1: int, index2: int) -> float:
        """Calculate the distance along the path from point at index1 to index2."""
        # Validate indices
        self.validate_index(index1)
        self.validate_index(index2)
        
        # Ensure index1 is less than index2
        index1, index2 = min(index1, index2), max(index1, index2)
        
        total_distance = 0
        for i in range(index1, index2):
            total_distance += self.haversine_distance(self.path[i], self.path[i+1])

        return total_distance
    
    def total_distance(self)->float:
        total_distance=0
        if len(self.path)>1:
            total_distance=self.distance(0, len(self.path)-1)
        return total_distance
    
    def decimal_to_dms(self,decimal_degree:float):
        degrees = int(decimal_degree)
        minutes = int((decimal_degree - degrees) * 60)
        seconds = (decimal_degree - degrees - minutes/60) * 3600.0
        return degrees, minutes, seconds

    def lat_lon_to_dms_string(self,latitude, longitude)->str:
        lat_degree, lat_minute, lat_second = self.decimal_to_dms(latitude)
        lon_degree, lon_minute, lon_second = self.decimal_to_dms(longitude)
        
        lat_direction = "N" if latitude >= 0 else "S"
        lon_direction = "E" if longitude >= 0 else "W"
        
        lat_str = f"{abs(lat_degree)}° {abs(lat_minute)}' {abs(lat_second):.4f}'' {lat_direction}"
        lon_str = f"{abs(lon_degree)}° {abs(lon_minute)}' {abs(lon_second):.4f}'' {lon_direction}"
        
        return lat_str, lon_str

    def as_dms(self,index:int)->Tuple(str,str):
        """
        get path point at index in Degrees, Minutes, Seconds notation
        """
        self.validate_index(index)
        lat, lon = self.path[index]
        dms=self.lat_lon_to_dms_string(lat, lon)
        return dms
    
    def get_start_location_details(self) -> str:
        """
        Get details of the starting location using Nominatim.
        """
        if len(self.path)<1:
            return "No points in path"
        
        # Fetch the location details using the first point in the path
        lat, lon = self.path[0]
        location = self.nominatim.query(f'{lat}, {lon}').toJSON()[0]
        
        # Extract desired details from the response
        # This example gets the display name, but you can extract other fields as required
        details=location.get('display_name', "Location not found")
        return details