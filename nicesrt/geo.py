'''
Created on 16.08.2023

@author: wf
'''
from typing import List, Tuple

class GeoPath:
    def __init__(self):
        self.path: List[Tuple[float, float]] = []

    def add_point(self, lat: float, lon: float) -> None:
        """Add a point to the geo path."""
        self.path.append((lat, lon))

    def get_path(self) -> List[Tuple[float, float]]:
        """Return the path."""
        return self.path
