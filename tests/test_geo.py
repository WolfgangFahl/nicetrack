'''
Created on 2023-08-17

@author: wf
'''
from nicesrt.geo import GeoPath
from tests.basetest import Basetest

class Test_GeoPath(Basetest):
    """
    Test the GeoPath functions
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def test_distance(self):
        """
        test haversine distance calculation
        """
        geo_path = GeoPath()
        geo_path.add_point(52.5200, 13.4050)  # Berlin
        geo_path.add_point(48.8566, 2.3522)   # Paris
        geo_path.add_point(51.5074, -0.1278)  # London
        berlin_paris=geo_path.distance(0, 1)
        berlin_london=geo_path.total_distance()                                                             
        debug=self.debug
        debug=True
        if (debug):
            print(f"Berlin-Paris: {berlin_paris:.0f} km")  
            print(f"Berlin-Paris-London: {berlin_london:.0f} km")
        self.assertAlmostEqual(877,berlin_paris,delta=1)
        self.assertAlmostEqual(1221,berlin_london,delta=1)