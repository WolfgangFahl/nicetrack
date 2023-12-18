'''
Created on 2023-08-19

@author: wf
'''
import os
from pathlib import Path
import gpxpy
from ngwidgets.basetest import Basetest

class Test_GPX(Basetest):
    """
    test GPX  handling
    """

    def test_read_gpx(self):
        """
        Test reading a GPX file
        """
        # Getting the directory of the current script/file
        current_dir = Path(__file__).parent
    
        # Forming the complete path to the GPX file
        gpx_file_path = os.path.join(current_dir, '..', 'nicetrack_examples', 'gpx', '149759.gpx')
        
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            debug=self.debug
            debug=True
            track_count=len(gpx.tracks)
            # Count the total number of points across all tracks
            total_points = sum(len(segment.points) for track in gpx.tracks for segment in track.segments)
            
            if debug:
                print(f"Found {track_count} GPX tracks")
                print(f"Total number of points across all tracks: {total_points}")
            
            # Check if the GPX file contains a single track
            self.assertEqual(1, track_count, "Expected 1 track in the GPX file")
            expected_point_count=2334
            # check the point count
            self.assertEqual(expected_point_count, total_points, f"Expected {expected_point_count} points, but found {total_points}")
