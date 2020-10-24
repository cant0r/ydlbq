#!/usr/bin/env python3

import subprocess as sp
import formattable as ft
import tempfile as tf

YDL_COMMAND_PARTIAL = "youtube-dl -f "

class Controller:
    def __init__(self, URL):
        with tf.TemporaryFile("w+") as t:
            if sp.run(["youtube-dl", "--version"], stdout=t).returncode != 0:
                  raise Exception("Please install youtube-dl on your system!")
        self.audio_formats = []
        self.video_formats = []
        self.URL = URL

        self._parse_format_table()        

    def _parse_format_table(self):
        with tf.TemporaryFile(mode="w+", encoding="utf-8", buffering=1) as temp, tf.TemporaryFile(mode="w+") as error:
            sp.run(["youtube-dl", "-F", f"{self.URL}"], stdout=temp, stderr=error)
            if len(error.read()) > 1:
                raise ValueError

            temp.seek(0)
            response = temp.readlines()

            while (line := response.pop(0)).find("format code") == -1:
                pass

            video_formats = [s.strip().split() for s in response if s.find("audio only") == -1]
            audio_formats = [s.replace("audio only", "").strip().split() for s in response if s.find("audio only") != -1]
      

            self.audio_formats = [ft.Format(int(a[0]), ft.AudioExtension[a[1].upper()], int(a[3].replace("k", ""))) for a in audio_formats]
            self.video_formats = [ft.Format(int(v[0]), ft.VideoExtension[v[1].upper() if v[1] != "3gp" else "_3GP"], sum([int(s) for s in [num.replace("", "0") for num in v[3].split("p")]])) for v in video_formats]
           

    def get_command_for_best_quality(self):
        video_format = sorted(self.video_formats, key=lambda f: f.resolution).pop()
        audio_format = None
        if video_format.extension == ft.VideoExtension.WEBM:
            audio_format = sorted([a for a in self.audio_formats if a.extension == ft.AudioExtension.WEBM], key= lambda f: f.resolution).pop()
        else:
            audio_format = sorted([a for a in self.audio_formats if a.extension != ft.AudioExtension.WEBM], key= lambda f: f.resolution).pop()
        
        return "".join([YDL_COMMAND_PARTIAL] + [str(video_format.format_code), "+", str(audio_format.format_code), " ", self.URL])