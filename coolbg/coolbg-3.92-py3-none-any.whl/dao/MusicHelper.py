import youtube_dl, requests
from bgeditor.common.utils import get_dir, download_file,normal_audio
from bgeditor.dao.FFmpeg import create_loop_audio_times
import uuid,json, shutil,os
from moviepy.editor import *
import subprocess
import urllib
import time
def download_audio(url, ext='mp3', retries= 3):
    try:
        file_name = str(uuid.uuid4()) + "." + ext
        rs = os.path.join(get_dir('download'), file_name)
        ydl_opts = {
            'outtmpl': rs,
            'format': 'bestaudio/m4a',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception:
        if(retries<0):
            raise
        return download_audio(url, ext, retries-1)
    return rs
def create_lyric_outro_songs(deezer_artist_id, lyric_outro_repeat, retries=3):
    if deezer_artist_id == 977996688:
        return None
    res = requests.get(f"http://source.automusic.win/deezer/artist/preview/{deezer_artist_id}/{lyric_outro_repeat}").json()
    arr_song=[]
    file_merg_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()))
    file_merg = open(file_merg_path, "a")
    final_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final.mp3')
    for item in res:
        tmp = download_file(item, ext='mp3')
        try:
            audio_test = AudioFileClip(tmp)
            audioduration = audio_test.duration
            audio_test.close()
            if audioduration < 1:
                continue
        except:
            continue
            pass
        tmp = normal_audio(tmp)
        tmp = fade_audio(tmp)
        arr_song.append(tmp)
        file_merg.write("file '%s'\n" % tmp)
    file_merg.close()
    if retries>0 and len(arr_song) != lyric_outro_repeat:
        retries-=1
        os.remove(file_merg_path)
        return create_lyric_outro_songs(deezer_artist_id, lyric_outro_repeat, retries=retries)

    if len(arr_song) > 1:
        cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
        os.system(cmd)
        os.remove(file_merg_path)
        for song in arr_song:
            try:
                os.remove(song)
            except:
                pass
    else:
        if len(arr_song) == 1:
            return arr_song[0]
    if len(arr_song) == 0:
        return None
    try:
        audio_moviepy = AudioFileClip(final_clip_path)
        if audio_moviepy.duration < 1:
            final_clip_path = None
        audio_moviepy.close()
    except:
        pass
    return final_clip_path
def fade_audio(audio_path, fade_time=3, dur=30):
    tmp_clip_path = os.path.join(get_dir('coolbg_ffmpeg'),str(uuid.uuid4()) + '-' + os.path.basename(audio_path))
    duration = dur-fade_time
    cmd = f'ffmpeg -i "{audio_path}" -af "afade=t=in:st=0:d={fade_time}, afade=t=out:st={duration}:d={fade_time}" "{tmp_clip_path}"'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    os.remove(audio_path)
    return tmp_clip_path
def check_song(file_path):
    try:
        audio_test = AudioFileClip(file_path)
        audioduration = audio_test.duration
        audio_test.close()
        if audioduration < 1:
            return False
    except:
        return False
        pass
    return True
def create_compilation_songs(data, job_id, mf_server):
    #[{"type":3,"url":"","repeat":1}]
    #3: youtube_video
    #7: deezer
    #8: link direct
    arr_songs=data
    file_merg_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()))
    file_merg = open(file_merg_path, "a")
    final_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final.mp3')
    cnt_song=0
    one_song_path=""
    try:
        for song in arr_songs:
            try:
                arr_tmp=song['uri'].split(":")
                song['local']=''
                if arr_tmp[0] == "youtube":#youtube
                    song['local']=download_audio(arr_tmp[2])
                if arr_tmp[0] == "direct":#direct
                    tmp=song['uri'].replace("direct:track:","")
                    ext = None
                    if "gdrive" in tmp:
                        ext="mp3"
                    song['local'] = download_file(tmp,ext=ext)
                    # cnt_retries = 0
                    # while (not check_song(song['local'])) and cnt_retries<3:
                    #     time.sleep(1)
                    #     song['local'] = download_file(tmp, ext=ext)
                    #     cnt_retries += 1
                if arr_tmp[0] == "deezer":#deezer
                    song_info=requests.get("http://source.automusic.win/deezer/track/get/"+arr_tmp[2], timeout=180).json()
                    song['local'] = download_file(song_info['url_128'])
                if arr_tmp[0] == "spotify":  # spotify
                    arr_song_info = requests.get("http://source.automusic.win/spotify/track/get/" + arr_tmp[2], timeout= 180).json()
                    if len(arr_song_info)>0:
                        song_info = arr_song_info[0]
                        song['local'] = download_file(song_info['url_128'])
                if arr_tmp[0] == "soundcloud":
                    tmp = song['uri'].replace("soundcloud:track:", "")
                    song['local'] = download_file(tmp)
                if arr_tmp[0] == "automusic" and arr_tmp[1] == "source":
                    arr_song_info = requests.get("http://source.automusic.win/config/f-retrieve/"+arr_tmp[2] +
                                                 f"?jobid={job_id}&mfs={urllib.parse.quote_plus(mf_server)}", timeout= 600).json()
                    for song_info in arr_song_info:
                        try:
                            arr_songs.append({"uri":"direct:track:"+song_info['url_128'], "repeat":1})
                        except:
                            pass

                #after download song, re-check song
                if not check_song(song['local']):
                    continue
                song['local']=normal_audio(song['local'])
                if song['repeat'] > 1:
                    song['local']= create_loop_audio_times(song['local'], song['repeat'])

                if not "coolbg_ffmpeg" in song['local']:
                    tmp_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(song['local']))
                    shutil.copyfile(song['local'], tmp_clip_path)
                    os.remove(song['local'])
                    song['local']=tmp_clip_path
                one_song_path=song['local']
                file_merg.write("file '%s'\n" % song['local'])
                cnt_song+=1
            except:
                import traceback
                traceback.print_exc()
                pass
        file_merg.close()
        if cnt_song>1:
            cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
            os.system(cmd)
            os.remove(file_merg_path)
            for song in arr_songs:
                try:
                    os.remove(song['local'])
                except:
                    pass
        else:
            if cnt_song ==1:
                return one_song_path
    except:
        pass
    if cnt_song == 0:
        return None
    try:
        audio_moviepy = AudioFileClip(final_clip_path)
        if audio_moviepy.duration < 1:
            final_clip_path=None
        audio_moviepy.close()
    except:
        pass
    return final_clip_path




