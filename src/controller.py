#!/usr/bin/env python3

import subprocess as sp
import formattable as ft
import tempfile as tf

YDL_COMMAND_PARTIAL = "youtube-dl -f "

class Controller:
    def __init__(self, URL):
       
        response = sp.run(["youtube-dl", "--version"], stdout=sp.PIPE)
        if response.returncode != 0:
            raise ValueError

        self.formats = []
        self.URL = URL

        self._parse_format_table()        

   
    def _parse_format_table(self):
        """Creates audio and video list that holds all the appropriate Format instances"""
       
        response = sp.run(["youtube-dl", "-F", f"{self.URL}"], stdout=sp.PIPE)
        if response.returncode != 0:
            raise ValueError

        response = response.stdout.decode("utf-8").splitlines()
        response = self.normalize(response)
        

        for line in response:
            dummy = ft.Format(0,0,0)
            l = line.strip().split(maxsplit=4)
            dummy.format_code = l[0]
            extension = l[1].upper()
            dummy.extension = ft.Extension[extension if extension != "3GP" else "_3GP"]
            res = l[3]
            if res.find("p") != -1:
                expanded_res = sum([int(p.replace('', '0')) for p in res.split('p')])
                dummy.resolution = expanded_res
            else:
                dummy.resolution = 0
                dummy.is_video = False
            
            note = l[4].split(',')
            dummy.size = note[-1]
            if not dummy.is_video:
                dummy.encoding, dummy.sample_size, dummy.sample_rate = self.get_audio_encoding(note[1])
            else:
                dummy.encoding = note[1].strip()
                dummy.fps = int(note[2].replace("fps", "").strip())
                if note[3].strip() != "video only":
                    dummy.encoding, dummy.sample_size, dummy.sample_rate = self.get_audio_encoding(note[3])

            self.formats.append(dummy)

    def get_audio_encoding(self, s):
        audio_encoding_info = s.split('@')
        sample = audio_encoding_info[1].split('k')
        encoding = audio_encoding_info[0].strip()
        size = int(sample[0].strip())
        raw_rate = sample[1].strip()
        rate =  int(raw_rate[1:raw_rate.find(')')].replace('Hz',''))
        return encoding,size,rate

    def get_command_for_best_quality(self):
        """Returns with the command that download the given video in its best quality via youtube-dl"""
        video_formats = [x for x in self.formats if x.is_video]
        video_format = sorted(video_formats, key=lambda f: f.resolution)
        video_format = video_format.pop()

        audio_formats = [x for x in self.formats if not x.is_video]
        audio_format = sorted(audio_formats, key=lambda f: f.resolution)
        
        if video_format.extension == ft.Extension.WEBM:
            for a in audio_format:
                if a.extension != ft.Extension.WEBM:
                    audio_format.remove(a)
        else:
            for a in audio_format:
                if a.extension == ft.Extension.WEBM:
                    audio_format.remove(a)

        audio_format = audio_format.pop()

        vf_code = str(video_format.format_code)
        af_code = str(audio_format.format_code)
        YDL_COMMAND_PARAMETERS = [vf_code, "+",af_code, " ", self.URL]
        return "".join([YDL_COMMAND_PARTIAL] + YDL_COMMAND_PARAMETERS)

    def normalize(self, format_table):
        ft = []
        for s in format_table:
            line = s.replace("m4a_dash container,", "")
            line = line.replace("webm container,", "")
            line = line.replace("audio only", "audio-only")

            ft.append(line)

        while (line := ft.pop(0)).find("format code") == -1:
            pass
        
        return ft
