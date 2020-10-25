#!/usr/bin/env python3
from enum import Enum

class Extension(Enum):
    AAC  = 0
    WAV  = 1
    M4A  = 2
    MP3  = 3
    WEBM = 4
    OGG  = 5
    _3GP = 6
    FLV  = 7
    MP4  = 8
   

class Format:
    def __init__(self, format_code, extension, resolution, is_video=True, encoding="", size="",sample_rate=0, sample_size=0, fps=0):
        self.format_code = format_code
        self.extension = extension
        self.resolution = resolution
        self.is_video = is_video
        self.encoding = encoding
        self.size = size
        self.sample_rate = sample_rate
        self.sample_size = sample_size
        self.fps = fps    


        