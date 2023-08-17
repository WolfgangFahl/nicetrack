'''
Created on 16.08.2023

@author: wf
'''
from typing import List, Tuple
import math

class GeoPath:
    def __init__(self):
        self.path: List[Tuple[float, float]] = []

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

    def distance(self, index1: int, index2: int) -> float:
        """Calculate the distance along the path from point at index1 to index2."""
        # Validate indices
        if index1 < 0 or index1 >= len(self.path) or index2 < 0 or index2 >= len(self.path):
            raise ValueError("Invalid indices provided")
        
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
