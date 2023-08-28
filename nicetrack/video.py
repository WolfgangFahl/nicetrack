'''
Created on 2023-08-27

@author: wf
'''
import vlc
import platform
from PyQt5 import QtWidgets

class Video:
    """
    Video play wrapper
    """
    def __init__(self,video_source:str):
        # Create a basic vlc instance
        self.instance = vlc.Instance()

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.video_source=video_source
        # In this widget, the video will be drawn
        if platform.system() == "Darwin": # for MacOS
            self.videoframe = QtWidgets.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtWidgets.QFrame()
        pass
        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(video_source)

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()
        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        if platform.system() == "Linux": # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows": # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

    
    def play(self):
            # Create an instance of the VLC player
            player = vlc.MediaPlayer(self.video_source)
        
            # Play the video
            status=player.play()

            pass