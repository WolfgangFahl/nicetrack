import io
import os
import av
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from nicegui import ui

class VideoStepperAV:
    """
    Display a video step by step (frame-by-frame) using PyAV for video decoding.
    """

    def __init__(self, video_path: str=None, root_path: str=None, fps: int = 30):
        self.container = None
        self.root_path = root_path
        self.video_path = None
        self.fps = fps
        self.set_video_path(video_path)

    def close(self):
        if self.container is not None:
            self.container.close()

    def set_video_path(self, video_path: str):
        self.close()
        self.video_path = video_path
        if video_path is None or not os.path.exists(video_path):
            self.video_size = 0
            self.base_url = None
            self.fps = 1
            # dummy image
            self.url = "https://picsum.photos/id/28/1024/768"
            return
        self.video_size = os.path.getsize(video_path)
        if self.root_path:
            if video_path.startswith(self.root_path):
                video_path = video_path.replace(self.root_path, "")
                if video_path.startswith("/"):
                    video_path = video_path.replace("/", "", 1)
                else:
                    video_path = os.path.basename(video_path)
        self.base_url = f"/video_step/{video_path}"
        self.container = av.open(self.video_path)
        self.set_frame_index(0)

    def set_frame_index(self, frame_index: int = 0):
        self.frame_index = frame_index
        if self.base_url:
            self.url = f"{self.base_url}/{self.frame_index}"

    def get_view(self, container):
        with container:
            self.view = ui.interactive_image(
                events=['click', 'mousedown', 'mouseup'],
                cross=True
            ).bind_source_from(self, 'url').bind_content(self, 'svg_content')
        return self.view

    def get_frame(self, frame_index: int = None):
        if self.container is None:
            return None
        if frame_index is None:
            frame_index = self.frame_index

        # Seek to the desired frame
        video_stream = self.container.streams.video[0]
        frame_num = frame_index
        framerate = video_stream.average_rate
        time_base = video_stream.time_base
        sec = int(frame_num / framerate)
        self.container.seek(sec * 1000000, whence='time', backward=True)
        
        # Get the next available frame
        for _ in range(sec, frame_num):
            frame = next(self.container.decode(video=0))
        return frame.to_image()

    def get_image(self, frame_index: int = None, img_format: str = "jpg") -> bytes:
        if frame_index is None:
            frame_index = self.frame_index

        # Check if the provided format is supported
        if img_format not in ["jpg", "png"]:
            raise ValueError("Unsupported image format. Please use 'jpg' or 'png'.")

        # Get the frame from the video
        frame_img = self.get_frame(frame_index)

        # If frame exists, encode it to the desired format
        if frame_img is not None:
            buffer = io.BytesIO()
            img_format = "jpeg" if img_format == "jpg" else img_format  # Handle 'jpg' -> 'jpeg'
            frame_img.save(buffer, format=img_format)
            return buffer.getvalue()
        return None

    async def stream_image(self, frame_index: int = 0, img_format: str = "jpg") -> StreamingResponse:
        if not self.video_size:
            raise HTTPException(status_code=404, detail=f"Video not available")

        image_bytes = self.get_image(frame_index, img_format)

        if image_bytes:
            return StreamingResponse(io.BytesIO(image_bytes), media_type=f"image/{img_format}")
        else:
            raise HTTPException(status_code=404, detail="Image not found")
