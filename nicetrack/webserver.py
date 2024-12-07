"""
Created on 2023-06-19

@author: wf
"""

import os

from fastapi import Header, HTTPException, Query
from ngwidgets.file_selector import FileSelector
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.leaflet_map import LeafletMap
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, ui

from nicetrack.geo import GeoPath
from nicetrack.srt import SRT
from nicetrack.version import Version
from nicetrack.video_stepper import VideoStepper
from nicetrack.video_stepper_av import VideoStepperAV

# from nicetrack.video import Video
from nicetrack.video_stream import VideoStream


class WebServer(InputWebserver):
    """
    WebServer class that manages the server

    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2023-2024 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right,
            version=Version(),
            default_port=9859,
            short_name="nicetrack",
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = NicetrackSolution
        return server_config

    def __init__(self):
        """
        Constructs all the necessary attributes for the
        WebServer object.
        """
        config = WebServer.get_config()
        InputWebserver.__init__(self, config=config)

        @ui.page("/video_play/{video_path:path}")
        async def video_play(
            client: Client, video_path: str, range_header: str = Header(None)
        ):
            await self.page(
                client, NicetrackSolution.video_play, video_path, range_header
            )

        @ui.page("/video_feed/{video_path:path}")
        async def video_feed(
            client: Client,
            video_path: str,
            start_time: float = Query(0.0, description="Start timestamp in seconds"),
            fps: float = Query(30.0, description="Frames per second of the video"),
        ):
            await self.page(
                client,
                NicetrackSolution.video_feed,
                video_path,
                start_time=start_time,
                fps=fps,
            )

        @ui.page("/video_step/{video_path:path}/{frame_index:int}")
        async def video_step(client: Client, video_path: str, frame_index: int = 0):
            await self.page(
                client, NicetrackSolution.video_step, video_path, frame_index
            )

    @classmethod
    def examples_path(cls) -> str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), "../nicetrack_examples")
        path = os.path.abspath(path)
        return path


class NicetrackSolution(InputWebSolution):
    """
    A class to handle the UI and integration Nicetrack.
    """

    def __init__(self, webserver: WebServer, client: Client):
        """
        Initialize the solution

        Calls the constructor of the base solution
        Args:
            webserver (WebServer): The webserver instance associated with this context.
            client (Client): The client instance this context is associated with.
        """
        super().__init__(webserver, client)  # Call to the superclass constructor#

        self.geo_desc = None
        self.geo_path = None
        self.zoom_level = 9
        self.video_stepper = None

    def set_zoom_level(self, zoom_level):
        self.zoom_level = zoom_level
        with self.geo_map as geo_map:
            geo_map.zoom = zoom_level

    def get_video_stream(self, video_path: str):
        # Check if not local
        if not self.is_local:
            raise HTTPException(
                status_code=400, detail="Videos only available in local mode of server"
            )
        # Check if the video name exists in the root path
        video_source = os.path.join(self.root_path, video_path)
        if not os.path.exists(video_source):
            raise HTTPException(
                status_code=404, detail=f"Video {video_source} not found"
            )
        video_stream = VideoStream(video_source)
        return video_stream

    async def video_play(self, video_path: str, range_header: str):
        video_stream = self.get_video_stream(video_path)
        stream_response = video_stream.get_video(range_header)
        return stream_response

    async def video_feed(
        self, video_path: str, start_time: float = 0.0, fps: int = 30.0
    ):
        video_stream = self.get_video_stream(video_path)
        stream_response = await video_stream.video_feed(start_time, fps)
        return stream_response

    async def video_step(self, video_path: str, frame_index: int = 0):
        if self.video_stepper is None:
            self.video_stepper = VideoStepper(video_path, self.root_path)
        stream_response = await self.video_stepper.stream_image(frame_index)
        return stream_response

    def mark_trackpoint_at_index(self, index: int):
        """
        mark the trackpoint at the given index

        Args:
            index(int): the index of the position
        """
        if self.geo_path:
            # get the trackpoint
            self.geo_path.validate_index(index)
            tp = self.geo_path.path[index]
            info = tp.get_info(self.geo_path.nominatim, with_details=False)
            loc = (tp.lat, tp.lon)
            self.trackpoint_desc.content = info
            with self.geo_map as geo_map:
                geo_map.center = loc
                geo_map.zoom = self.zoom_level
            if self.video_stepper:
                # @TODO make configurable
                fps = 30
                frame_index = self.geo_path.get_video_frame_index(index, fps)
                self.video_stepper.set_frame_index(frame_index)

    async def render(self, _click_args=None):
        """
        Renders the SRT content

        Args:
            click_args (object): The click event arguments.
        """
        try:
            input_source = self.input
            if input_source.startswith("https://cycle.travel/map/journey/"):
                input_source = input_source.replace("/map/journey", "/gpx") + ".gpx"
            ui.notify(f"rendering {input_source}")
            geo_text = self.do_read_input(input_source)
            if input_source.lower().endswith(".srt"):
                self.srt = SRT.from_text(geo_text)
                self.geo_path = self.srt.as_geopath()
            elif input_source.lower().endswith(".gpx"):
                self.geo_path = GeoPath.from_gpx(geo_text)
            path_len = len(self.geo_path.path)
            self.time_slider._props["max"] = path_len
            self.time_slider.value = 0
            file_name = ""
            tp_index = self.time_slider.value
            tp = self.geo_path.path[tp_index]
            info = tp.get_info(self.geo_path.nominatim)
            try:
                file_name = self.input.split("/")[-1]
            except BaseException as _bex:
                pass
            desc = f"""{file_name}<br>{info}<br>
{path_len} points
"""
            self.geo_desc.content = desc
            with self.geo_map as geo_map:
                path_2d = self.geo_path.as_tuple_list()
                if len(path_2d) > 0:
                    loc = path_2d[0]
                    geo_map.center = loc
                    geo_map.zoom = self.zoom_level
                    print(f"setting location to {loc}")
                    geo_map.draw_path(path_2d)
            # show render result in log
            # self.log_view.push(render_result.stderr)
        except BaseException as ex:
            self.handle_exception(ex, self.do_trace)

    async def on_play(self):
        """
        play the corresponding video
        """
        if not self.input:
            return
        try:
            if self.input.endswith(".SRT"):
                # pyQT video playing
                video_path = self.input.replace(".SRT", ".MP4")
                self.video_stepper.set_video_path(video_path)
                pass
        except BaseException as ex:
            self.handle_exception(ex, self.do_trace)

    async def home(self):
        """Generates the home page with a map"""

        def setup_home():
            """ """
            with ui.element("div").classes("w-full"):
                with ui.splitter() as splitter:
                    with splitter.before:
                        self.example_selector = FileSelector(
                            path=self.root_path, handler=self.read_and_optionally_render
                        )
                        self.input_input = ui.input(
                            value=self.input, on_change=self.input_changed
                        ).props("size=100")
                        self.tool_button(
                            tooltip="reload", icon="refresh", handler=self.reload_file
                        )
                        if self.is_local:
                            self.tool_button(
                                tooltip="open", icon="file_open", handler=self.open_file
                            )
                            self.tool_button(
                                tooltip="play", icon="play_circle", handler=self.on_play
                            )
                    with splitter.after:
                        self.geo_desc = ui.html("")
                        self.trackpoint_desc = ui.html("")
                with ui.splitter() as splitter:
                    with splitter.before:
                        with LeafletMap(classes="w-full h-96") as self.geo_map:
                            pass
                    with splitter.after as self.video_container:
                        self.video_stepper = VideoStepper(None, self.root_path)
                        self.video_view = self.video_stepper.get_view(
                            self.video_container
                        )
            slider_props = "label-always"
            self.zoom_slider = ui.slider(
                min=1,
                max=20,
                step=1,
                value=self.zoom_level,
                on_change=lambda e: self.set_zoom_level(e.value),
            ).props(slider_props)
            self.time_slider = ui.slider(
                min=0,
                max=100,
                step=1,
                value=50,
                on_change=lambda e: self.mark_trackpoint_at_index(e.value),
            ).props(slider_props)

        await self.setup_content_div(setup_home)

    def configure_run(self):
        self.allowed_urls = [
            "https://raw.githubusercontent.com/JuanIrache/DJI_SRT_Parser/master/samples/",
            "https://raw.githubusercontent.com/JuanIrache/dji-srt-viewer/master/samples/",
            "https://cycle.travel/gpx/",
            "https://cycle.travel/map/journey/",
            self.examples_path(),
            self.root_path,
        ]
