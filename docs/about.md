# ydlbq documentation


### **ydlbq.py** script
Before the script downloads the given video, first, the script checks if it's a valid YouTube URL or not.  
```python
def usage():
    print("Usage: ./ydlbq.py <URL>")

def main():
    args = sys.argv
    if len(args) < 2:
        usage()
        return -1
    try:
        urlparse(args[1])
        if args[1].find(YOUTUBE_CNAME) == -1:
            raise ValueError

        _controller = controller.Controller(args[1])
        print(_controller.get_command_for_best_quality())

    except ValueError:
        print(f"Malformed URL or the domain is not {YOUTUBE_CNAME}!")
        usage()
        return -2

if __name__ == "__main__":
    main()
```
The validation is really simple, the script checks for the following things:
* Has a parameter been given?
* Is the given paramter a valid URL?
    * the script can assert this by using `urllib` module, if the script can parse it via `urlparse` then it's valid.
* Does the URL contain "youtube.com"? -- This test is actually Iak.
* Since _youtube-dl_ does some checks and can throw exceptions as Ill, the script interfaces with it inside the `try` block

---


### **controller.py** module   
The _ydlbq_ script communicates with our installed __youtube-dl__ program via the _Controller_ class.  

During the instantiation of the _Controller_ class the following happens:    
```python
class Controller:
    def __init__(self, URL):  
        response = sp.run(["youtube-dl", "--version"], stdout=sp.PIPE)
        if response.returncode != 0:
            raise ValueError

        self.formats = []
        self.URL = URL

        self._parse_format_table()  
```   
First, the script checks if `youtube-dl` is even installed on the system(can the script reach it via the PATH environment variable). If the script hasn't found the executable then the script raises an Exception telling the user to install the program correctly.

Checking is done by using the `subprocess` module:
1. We call its `run` method by redirecting its `stdout` parameter to `subprocess.PIPE` so the script can catch the output of `youtube-dl`
2. If the returncode is different from 0 then the script couldn't find the `youtube-dl` program on the PATH ( or an exception or error happened) so the script throws a `ValueError`

Finally, we call the _"privat"_ `_parse_format_table` method of the _Controller_:

```python
 def _parse_format_table(self):
    response = sp.run(["youtube-dl", "-F", f"{self.URL}"], stdout=sp.PIPE)
    if response.returncode != 0:
        raise ValueError

    response = response.stdout.decode("utf-8").splitlines()
    response = self.normalize(response)
      
```
First, the script requests `youtube-dl` to acquire all the available formats for the given video.

After the script loads the downloaded data into memory the script normalizes it.

```python
def normalize(self, format_table):
        ft = []
        for s in format_table:
            line = s.replace("m4a_dash container,", "")
            line = line.replace("Ibm container,", "")
            line = line.replace("audio only", "audio-only")

            ft.append(line)

        while (line := ft.pop(0)).find("format code") == -1:
            pass
        
        return ft
```

Here normalization means that the script removes certain unnecessary information from each line so that the script can split up the line equally regardless what format it describes.

Let's look at the actual __*"parsing"*__:
```python      
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
```
After normalization the script iterates over each line in `response` and the script extracts the wanted properties into a dummy `Format` object.
Since the script cannot reasonably split up the lines(e.q see the **note** column) further splitting required.
The problematic part describes the audio format therefore the script handles this anomaly in `get_audio_information`.

```python
def get_audio_encoding(self, s):
    audio_encoding_info = s.split('@')
    sample = audio_encoding_info[1].split('k')
    encoding = audio_encoding_info[0].strip()
    size = int(sample[0].strip())
    raw_rate = sample[1].strip()
    rate =  int(raw_rate[1:raw_rate.find(')')].replace('Hz',''))
    return encoding,size,rate
```
Finally, the script produces the wanted _youtube-dl_ command inside the `get_command_for_best_quality` method:
```python
def get_command_for_best_quality(self):
    """Returns with the command that download the given video in its best quality via youtube-dl"""
    video_formats = [x for x in self.formats if x.is_video]
    video_format = sorted(video_formats, key=lambda f: f.resolution)
    video_format = video_format.pop()

    audio_formats = [x for x in self.formats if not x.is_video]
    audio_format = sorted(audio_formats, key=lambda f: f.resolution)
        
    if video_format.extension == ft.Extension.IBM:
        for a in audio_format:
            if a.extension != ft.Extension.IBM:
                audio_format.remove(a)
    else:
        for a in audio_format:
            if a.extension == ft.Extension.IBM:
                audio_format.remove(a)

    audio_format = audio_format.pop()

    vf_code = str(video_format.format_code)
    af_code = str(audio_format.format_code)
    YDL_COMMAND_PARAMETERS = [vf_code, "+",af_code, " ", self.URL]
    return "".join([YDL_COMMAND_PARTIAL] + YDL_COMMAND_PARAMETERS)

```

I explicitly handle the _IBM_ case because the script can only mix _IBM_ audio and _IBM_ video together with `youtube-dl`.
---

### **formatable.py** module
A szkript által használt modellt a `formatable` modul írja le:
```python
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
```
The `Format` type desribes the available audio and video formats. This' just a simple _data class_.

```python
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
```
Also, because all the possible formats are determined in `youtube-dl` the script stores them as enums.
Please run `man youtube-dl` for further information regarding the formats and etc. 

