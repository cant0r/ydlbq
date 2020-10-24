# ydlbq dokumentáció


### **ydlbq.py** szkript
A szkript futása a paraméterként átadott URL cím ellenőrzésével kezdődik.    
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
AZ ellenőrzések nagyon egyszerűek, a következőkre figyelünk:
* Lett-e átadva paraméter?
* Az átadott paraméter valid URL?
    * Ezt az `urllib` modul segítségével ellenőrizzük, ha sikerül _parse_-olni akkor valid.
* Megnézzük, hogy szerepel-e benne a "youtube.com" domain.
* Mivel a _youtube_dl_ is jelenthet hibáról, a `try` blokkban kommunikálunk vele.  

---


### **controller.py** modul    
A _ydlbq_ szkript az ebben a modulban található _Controller_ osztály segítségével kommunikál a rendszerünkre feltelepített __youtube-dl__ programmmal.  

Az osztály példányosításakor a következők hajtódnak végre:    
```python
class Controller:
    def __init__(self, URL):
        with tf.TemporaryFile("w+") as t:
            if sp.run(["youtube-dl", "--version"], stdout=t).returncode != 0:
                  raise Exception("Please install youtube-dl on your system!")
        self.audio_formats = []
        self.video_formats = []
        self.URL = URL

        self._parse_format_table()   
```   
Amikor meghívódik a konstruktor akkor ellenőrizzük, hogy telepítve van-e, azaz, rajta van-e a _PATH_ változón a **youtube-dl** fájlhoz vezető út.   
Amennyiben nincs, akkor kivételt dobunk a felhasználó felé, hogy nem találtuk és telepítse fel (szabályosan).

Az ellenőrzést a `subprocess` modul segítségével végezzük el:
1. Létrehozunk egy _temporary_ fájlt, ami csak addig `with` hatókörében fog csak létezni
2. A `subprocess` modul `run` függvényvét meghívjuk, úgy, hogy ebbe az átmeneti fájlba írjon és ne a standard kimenetre (ez csupán esztétika okokból tesszük)
3. Ha a `run` által visszatérített _CompletedProcess_ típusú objektum által hordozott visszatérési érték 0-tól különbözik akkor nem találtuk meg a _youtube-dl_ fájlt.

A konstruktor maradék részében inicialzálunk néhány tagváltozót és meghívjuk a `_parse_format_table` "privát" tagmetódust.


A `_parse_format_table` lekéri a paraméterként átadott URL-hez tartozó elérhető audió és videó formátumokat a _youtube-dl_ programtól, majd feldolgozza őket `Format` típusú objektumokba.

```python
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
      
```
A konstruktorban látott módszer alapján megint kommunikálunk a _youtube-dl_ programmal, lekérjük az adott URL által mutatott videóhoz elérhető formátumokat.   

Miután az eredményt kiírtuk egy fájlba, elkezdjük feldolgozni azt soronként, a memóriába közvetlenül beolvassuk a fájlt, mivel kicsi lábnyommal rendelkezik. 

A feldolgozás során _list comprehension_ módszert alkalmazva feldaraboljuk az egyes formátumokat leíró sorokat, kihagyva az első releváns információt nem hordozó 4 sort.    
```python      

            self.audio_formats = [ft.Format(int(a[0]), ft.AudioExtension[a[1].upper()], int(a[3].replace("k", ""))) for a in audio_formats]
            self.video_formats = [ft.Format(int(v[0]), ft.VideoExtension[v[1].upper() if v[1] != "3gp" else "_3GP"], sum([int(s) for s in [num.replace("", "0") for num in v[3].split("p")]])) for v in video_formats]
      
```
A metódus legvégén történik meg a tényleges feldolgozás, amikor az előbb elkészített listák alapján létrehozzuk az elérhető formátumokat reprezentáló `Format` típusú objektumokkal rendelkező audió és videó listákat.

Az adott formátumnak megfelelően végrehajtjuk a megfelelő módosításokat, hogy tárolni tudjuk `Format` típusú objektumokban.

---

### **formatable.py** modul
A szkript által használt modellt a `formatable` modul írja le:
```python
class Format:
    def __init__(self, format_code, extension, resolution):
        self.format_code = format_code
        self.extension = extension
        self.resolution = resolution
        
```
A `Format` osztály konstruktora egy szimpla hozzárendelő konstruktor, innen is látható, hogy a `Format` osztály csak egy egyszerű _data class_.     
```python
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
```
Megkülönböztetjük az audió és videó formátumokat _enum_-ok használatával.    
A `youtube-dl` áltla támogatott összes formátum fel van sorolva itt, forrás `man youtube-dl`.  

