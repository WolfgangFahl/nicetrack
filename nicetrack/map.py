'''
Created on 2023-01

https://github.com/zauberzeug/nicegui/blob/main/examples/map/main.py

@author: rodja
'''
from ngwidgets import leaflet.leaflet  # this module wraps the JavaScript lib leafletjs.com into an easy-to-use NiceGUI element

from nicegui import Client, ui

class MapExample:
    """
    Leaflet based map example
    """

    def __init__(self):
        self.zoom_level=9
        self.locations = {
            (48.486375, 8.375567): 'Baiersbronn',
            (52.5200, 13.4049): 'Berlin',
            (52.37487,9.74168): 'Hannover',
            (40.7306, -74.0060): 'New York',
            (39.9042, 116.4074): 'Beijing',
            (35.6895, 139.6917): 'Tokyo',
        }
        
        self.zoom_levels = {
            9:9,
            10:10,
            11:11,
            12:12,
            13:13,
            14:14,
            15:15,
            16:16,
            17:17,
        }
        
        @ui.page('/')
        async def main_page(client: Client):
            await self.show_map(client)
            
    def on_change_zoom_level(self,_ce):
        self.zoom_level=_ce.value
        self.map.set_zoom_level(self.zoom_level)
        pass
    
    async def draw_path(self,_ce):
        """
        """
        with self.map as geo_map:
            locs=list(self.locations.keys())
            path=[locs[1],locs[2]]
            geo_map.draw_path(path)
            
            
    async def show_map(self,client:Client):
        self.map = leaflet().classes('w-full h-96')
        selection = ui.select(self.locations, on_change=lambda e: self.map.set_location(e.value,zoom_level=self.zoom_level)).classes('w-40')
        zoom_selection=ui.select(self.zoom_levels, on_change=self.on_change_zoom_level).classes('w-40')
        await client.connected()  # wait for websocket connection
        selection.set_value(next(iter(self.locations)))  # trigger map.set_location with first location in selection
        zoom_selection.set_value(self.zoom_level)
        ui.button("Path",on_click=self.draw_path)
    
    def run(self):    
        ui.run(title="map example",reload=False)
    
if __name__ == "__main__":
    map_example=MapExample()
    map_example.run()
