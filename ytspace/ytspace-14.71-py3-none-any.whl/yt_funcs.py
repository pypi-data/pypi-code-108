from pytube import YouTube as YT;
from pytube import exceptions as pytube_err;
import datetime;
import os;

def yt_download(url, audio = False):
    yt_obj = YT(url)
    title = yt_obj.title

    extension = "mp3" if audio else "mp4"
    file_name = title.replace(" ","_") + "." + extension.lower()
    file_path = get_download_path(0 if audio else 1)

    streams = yt_obj.streams
    streams.filter(file_extension = extension, only_audio = audio)
    stream = streams.get_audio_only() if audio else streams.get_highest_resolution()
    
    print("\n    Downloading...")
    
    current_time = str(datetime.datetime.now()).split()
    date, time = current_time[0], current_time[1]
    
    stream.download(filename = file_name, output_path = file_path)
    
    file_size = (os.path.getsize(file_path + file_name))/(1024**2) # In MB
    file_path = os.path.abspath(file_path)
    
    print("    Download complete.\n")
    print("> File path:", file_path)

    return (
        url,
        date,
        time
    ), (
        title,
        file_size,
        file_name
    ), (0, "music") if audio else (1, "videos")

def get_download_path(media_type):
    if os.name == "nt":
        import winreg
        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), ("Music" if media_type == 0 else "Videos")) + "/"
