"""
Created on 2023-08-31

@author: wf
"""
import io
import os
import cv2
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from nicegui import ui

class VideoStepper:
    """
    Display a video step by step (frame-by-frame).
    """

    def __init__(self, video_path: str=None, root_path: str=None, fps: int = 30):
        """
        Initialize the VideoStepper instance.
        
        Args:
            video_path (str): Path to the video file.
            root_path (str): Root directory path.
            fps (int, optional): Frames per second. Defaults to 30.
        """
        self.cap=None
        self.root_path=root_path
        self.video_path = None
        self.fps = fps
        self.set_video_path(video_path)
        
    def close(self):
        if self.cap is not None:
            self.cap.release()
        
    def set_video_path(self,video_path:str):
        self.close()
        self.video_path=video_path
        if video_path is None or not os.path.exists(video_path):
            self.video_size=0
            self.base_url=None
            self.fps=1
            # dummy image
            self.url="https://picsum.photos/id/28/1024/768"  
            return
        self.video_size = os.path.getsize(video_path)
        if self.root_path:
            if video_path.startswith(self.root_path):
                video_path = video_path.replace(self.root_path, "")
                if video_path.startswith("/"):
                    # replace first slash
                    video_path = video_path.replace("/", "", 1)
                else:
                    video_path = os.path.basename(video_path)
        self.base_url=f"/video_step/{video_path}"   
        self.cap = cv2.VideoCapture(self.video_path)
        self.set_frame_index(0)
        
    def set_frame_index(self,frame_index:int=0):
        self.frame_index=frame_index
        if self.base_url:
            self.url = f"{self.base_url}/{self.frame_index}"
        
    def get_view(self,container):
        with container:
            self.view=ui.interactive_image(
                events=['click', 'mousedown', 'mouseup'], 
                cross=True
            ).bind_source_from(self, 'url').bind_content(self, 'svg_content')
        return self.view
        
    def get_frame(self, frame: int=None):
        """
        Extracts the specified frame from the video.

        Args:
            frame (int): The frame number to extract.

        Returns:
            numpy.ndarray or None: The image of the specified frame or None if the frame doesn't exist.
        """
        if self.cap is None:
            return None
        if frame is None:
            frame=self.frame_index
            
        # Calculate the frame number
        frame_number = frame * self.fps

        # Set the position of the video file capture to the desired frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = self.cap.read()

        if ret:
            return frame
        else:
            return None
   
    def get_image(self, frame: int=None, img_format: str = "jpg") -> bytes:
        """
        Extracts the specified frame from the video and converts it to the desired image format.

        Args:
            frame (int): The frame number to extract.
            img_format (str, optional): Image format, supports "jpg" and "png". Defaults to "jpg".

        Returns:
            bytes or None: The image bytes of the specified frame in the desired format or None if the frame doesn't exist.
        """
        if frame is None:
            frame=self.frame_index
            
        # Check if the provided format is supported
        if img_format not in ["jpg", "png"]:
            raise ValueError("Unsupported image format. Please use 'jpg' or 'png'.")
        
        # Get the frame from the video
        frame_img = self.get_frame(frame)
        
        # If frame exists, encode it to the desired format
        if frame_img is not None:
            retval, buffer = cv2.imencode(f'.{img_format}', frame_img)
            
            if retval:
                return buffer.tobytes()
        return None
    
    async def stream_image(self, frame_index: int = 0, img_format: str = "jpg") -> StreamingResponse:
        """
        Stream an image from the video at the specified frame index in the given image format.
    
        Args:
            frame_index (int, optional): Frame index to retrieve. Defaults to 0.
            img_format (str, optional): Image format, supports "jpg" and "png". Defaults to "jpg".
        
        Raises:
            HTTPException: Raises a 404 exception if the video is not available.
        
        Returns:
            StreamingResponse: The image from the specified frame in the desired format.
        """
        if not self.video_size:
            raise HTTPException(status_code=404, detail=f"Video not available")
        
        image_bytes = self.get_image(frame_index, img_format)
        
        if image_bytes:
            return StreamingResponse(io.BytesIO(image_bytes), media_type=f"image/{img_format}")
        else:
            raise HTTPException(status_code=404, detail="Image not found")