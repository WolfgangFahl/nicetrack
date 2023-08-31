"""
Created on 27.08.2023

@author: wf
"""
from fastapi import Header, HTTPException
from starlette.responses import FileResponse, StreamingResponse
import os
import cv2

class VideoStream():
    """
    wrapper to stream a local file as a video
    """

    def __init__(self, video_path):
        self.video_path = video_path
        self.video_size = os.path.getsize(video_path)
        
    def generate_frames(self, start_time: float = 0.0, fps: float = 30.0):
        cap = cv2.VideoCapture(self.video_path)
        
        # Calculate the starting frame based on start_time and fps
        start_frame = int(start_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


    async def video_feed(self, start_time: float = 0.0, fps: float = 30.0):
        frame_gen = self.generate_frames(start_time=start_time, fps=fps)
        return StreamingResponse(frame_gen, media_type="multipart/x-mixed-replace; boundary=frame")

    def parse_range_header(self, range_header: str) -> tuple:
        """
        Parse the Range header to determine the part of the file to stream.
        Returns a tuple of (start_byte, end_byte).
        """
        start_byte, end_byte = None, None
    
        if range_header:
            try:
                byte1, byte2 = range_header.replace("bytes=", "").split("-")
                start_byte = int(byte1)
                end_byte = int(byte2) if byte2 else None
            except ValueError:
                raise HTTPException(status_code=400, detail="Malformed range header")
    
        return start_byte, end_byte
    
    def stream_partial_content(self, start: int, end: int) -> StreamingResponse:
        """
        Stream the content between the start and end bytes.
        """
        def content_generator():
            with open(self.video_path, 'rb') as video:
                video.seek(start)
                while start <= end:
                    chunk_size = min(8192, end - start + 1)
                    buffer = video.read(chunk_size)
                    if not buffer:
                        break
                    start += chunk_size
                    yield buffer
    
        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{self.video_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": "video/mp4",
        }
    
        return StreamingResponse(content_generator(), status_code=206, headers=headers)
    
    def get_video(self, range_header: str = Header(default=None)):
        start, end = self.parse_range_header(range_header)
    
        if not start and not end:
            # Just serve the whole file if no range
            return FileResponse(self.video_path, media_type="video/mp4")
    
        if start >= self.video_size:
            raise HTTPException(status_code=416, detail="Range not satisfiable")
    
        end = end or self.video_size - 1
        return self.stream_partial_content(start, end)
