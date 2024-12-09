"""
Created on 2024-12-17

@author: wf
"""
from ngwidgets.leaflet_map import LeafletMap
from nicegui import ui


class Map:
    """
    A class to create and display a map centered on the user's current location.
    """

    def __init__(self, solution, zoom_level=10):
        """
        Initializes the Map class with a solution and a default zoom level.
        """
        self.solution = solution
        self.zoom_level = zoom_level
        self.map = None


    async def setup_ui(self):
        """
        Sets up the user interface for the map, fetching the geolocation and initializing the map.
        """
        try:
            location = await self.get_location()
            #location =  (51.244, 6.520)
            if location:
                with ui.row() as self.map_row:
                    self.map = LeafletMap(center=location, zoom=self.zoom_level)
                    await self.map.initialized()
                    self.map.marker(latlng=location)
            with ui.row() as self.label_row:
                ui.label().bind_text_from(self.map, 'center',lambda center: f'Center: {center[0]:.3f}, {center[1]:.3f}')
                ui.label().bind_text_from(self.map, 'zoom',lambda zoom: f'Zoom: {zoom}')
                #ui.label().bind_text(lambda: f'Layers: {len(self.map.layers)}')  # Layer counter

            with ui.grid(columns=2) as self.grid:
                ui.button(icon='zoom_in', on_click=lambda: setattr(self.map, 'zoom', self.map.zoom + 1))
                ui.button(icon='zoom_out', on_click=lambda: setattr(self.map, 'zoom', self.map.zoom - 1))

        except Exception as ex:
            self.solution.handle_exception(ex)

    async def get_location(self):
        """
        Fetches the current geographic location of the user via JavaScript.
        Returns the coordinates as a tuple (latitude, longitude).
        """
        location=None
        response = await ui.run_javascript('''
            return await new Promise((resolve, reject) => {
                if (!navigator.geolocation) {
                    reject(new Error('Geolocation is not supported by your browser'));
                } else {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            resolve({
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                            });
                        },
                        () => {
                            reject(new Error('Unable to retrieve your location'));
                        }
                    );
                }
            });
        ''', timeout=5.0)
        if 'latitude' in response:
            location=response['latitude'], response['longitude']
        return location




