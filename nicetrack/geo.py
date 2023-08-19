'''
Created on 16.08.2023

@author: wf
'''
from typing import List, Tuple
import math
import logging
import os
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.cachingStrategy import CachingStrategy, JSON
from pathlib import Path
import gpxpy
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Trackpoint:
    lat: float
    lon: float
    elevation: float = None
    timestamp: datetime = None

class GeoPath:
    """
    a 3D Path of geographic coordinates in lat/lon notation
    """
    def __init__(self, name: str=None, cacheDir: str=None):
        self.name = name
        self.path: List[Trackpoint] = []
        if cacheDir is None:
            home = str(Path.home())
            cacheDir = f"{home}/.nominatim"
        self.cacheDir = cacheDir
        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)
        logging.getLogger('OSMPythonTools').setLevel(logging.ERROR)
        CachingStrategy.use(JSON, cacheDir=self.cacheDir)
        self.nominatim = Nominatim()

    @classmethod
    def from_points(cls, *points) -> "GeoPath":
        """
        get a geopath for the given points
        """
        geo_path = cls()
        for point in points:
            lat, lon = point
            geo_path.add_point(lat, lon)
        return geo_path

    @classmethod
    def from_gpx(cls, gpx_data: str) -> "GeoPath":
        geo_path = cls()
        gpx = gpxpy.parse(gpx_data)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    geo_path.add_point(point.latitude, point.longitude, point.elevation, point.time)
        return geo_path

    def add_point(self, lat: float, lon: float, elevation: float = None, timestamp: datetime = None) -> None:
        self.path.append(Trackpoint(lat, lon, elevation, timestamp))

    def get_path(self) -> List[Trackpoint]:
        return self.path
    
    def as_tuple_list(self) -> List[Tuple[float, float]]:
        return [(point.lat, point.lon) for point in self.path]

    def haversine_distance(self, point1: Trackpoint, point2: Trackpoint) -> float:
        R = 6371.0
        lat1 = math.radians(point1.lat)
        lon1 = math.radians(point1.lon)
        lat2 = math.radians(point2.lat)
        lon2 = math.radians(point2.lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def validate_index(self, index: int):
        max_index = len(self.path) - 1
        if index < 0 or index > max_index:
            raise ValueError(f"Invalid index {index}: valid range is 0-{max_index}")

    def distance(self, index1: int, index2: int) -> float:
        self.validate_index(index1)
        self.validate_index(index2)
        index1, index2 = min(index1, index2), max(index1, index2)
        total_distance = 0
        for i in range(index1, index2):
            total_distance += self.haversine_distance(self.path[i], self.path[i + 1])
        return total_distance

    def total_distance(self) -> float:
        total_distance = 0
        if len(self.path) > 1:
            total_distance = self.distance(0, len(self.path) - 1)
        return total_distance

    def decimal_to_dms(self, decimal_degree: float):
        degrees = int(decimal_degree)
        minutes = int((decimal_degree - degrees) * 60)
        seconds = (decimal_degree - degrees - minutes/60) * 3600.0
        return degrees, minutes, seconds

    def lat_lon_to_dms_string(self, latitude: float, longitude: float) -> str:
        lat_degree, lat_minute, lat_second = self.decimal_to_dms(latitude)
        lon_degree, lon_minute, lon_second = self.decimal_to_dms(longitude)
        lat_direction = "N" if latitude >= 0 else "S"
        lon_direction = "E" if longitude >= 0 else "W"
        lat_str = f"{abs(lat_degree)}° {abs(lat_minute)}' {abs(lat_second):.4f}'' {lat_direction}"
        lon_str = f"{abs(lon_degree)}° {abs(lon_minute)}' {abs(lon_second):.4f}'' {lon_direction}"
        return lat_str, lon_str

    def as_dms(self, index: int) -> Tuple[str, str]:
        self.validate_index(index)
        lat, lon = self.path[index].lat, self.path[index].lon
        dms = self.lat_lon_to_dms_string(lat, lon)
        return dms

    def as_google_maps_link(self, index: int) -> str:
        self.validate_index(index)
        lat, lon = self.path[index].lat, self.path[index].lon
        link = f"https://maps.google.com/?q={lat},{lon}"
        return link

    def get_start_location_details(self) -> str:
        if len(self.path) < 1:
            return "No points in path"
        lat, lon = self.path[0].lat, self.path[0].lon
        location = self.nominatim.query(f'{lat}, {lon}').toJSON()[0]
        details = location.get('display_name', "Location not found")
        return details
