#!/usr/bin/env python3
from enum import Enum

class AudioExtension(Enum):
    AAC  = 0
    WAV  = 1
    M4A  = 2
    MP3  = 3
    WEBM = 4
    OGG  = 5
    
class VideoExtension(Enum):
    _3GP = 0
    FLV  = 1
    WEBM = 2
    MP4  = 3

class Format:
    def __init__(self, format_code = -1, extension = None, resolution = -1):
        self.format_code = format_code
        self.extension = extension
        self.resolution = resolution
        


        