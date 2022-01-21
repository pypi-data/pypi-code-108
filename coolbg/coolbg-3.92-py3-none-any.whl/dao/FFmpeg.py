import math
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.fx import make_loopable, loop
from bgeditor.common.utils import get_dir
import uuid
import os
import shutil

def create_suource_can_loop_path(clip_path, is_delete = True, ext="mp4"):
    return create_source_can_loop(get_dir('download'), clip_path, is_delete = is_delete, ext=ext)
def create_source_can_loop(dir_path, clip_path, is_delete = True, ext = "mp4" ):
    tmp_clip_path_z_resync = None
    try:
        if dir_path.endswith("/"):
            dir_path = dir_path[:-1]
        clip = VideoFileClip(clip_path,audio=False)
        tmp_clip_path_z = os.path.join(dir_path, str(uuid.uuid4()) + '-' + os.path.basename(clip_path))
        clip.write_videofile(tmp_clip_path_z, fps=24, codec='libx264')
        clip.close()
        clip = VideoFileClip(tmp_clip_path_z, audio=False)
        cross = clip.duration/5
        if cross > 3:
            cross=3
        clip = make_loopable.make_loopable(clip, cross)
        tmp_clip_path_z = os.path.join(dir_path, str(uuid.uuid4()) + '-' + os.path.basename(clip_path).split(".")[0] + "." + ext)
        tmp_clip_path_z_resync = os.path.join(dir_path , str(uuid.uuid4()) + '-re-sync-' + os.path.basename(clip_path).split(".")[0] + "." + ext)
        try:
            clip.write_videofile(tmp_clip_path_z, fps=24, codec='libx264')
            clip.close()
            tmp_clip_path_z_resync=tmp_clip_path_z
        except:
            cmd = "ffmpeg -y -i \"%s\" -c:v libx264 -crf 22 \"%s\"" % (tmp_clip_path_z, tmp_clip_path_z_resync)
            os.system(cmd)
            os.remove(tmp_clip_path_z)
            pass
        if is_delete:
            os.remove(clip_path)
        try:
            clip = VideoFileClip(tmp_clip_path_z_resync)
            if clip.duration is None or clip.duration < 0.1:
                tmp_clip_path_z_resync = None
        except:
            tmp_clip_path_z_resync = None
            pass
    except:
        pass
    return tmp_clip_path_z_resync

def create_loop_audio_times(audio_path, times, is_del=True):
    try:
        tmp_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(audio_path))
        shutil.copyfile(audio_path, tmp_clip_path)
        file_merg_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()))
        final_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final-' + os.path.basename(audio_path))
        file_merg = open(file_merg_path, "a")
        for i in range(times):
            file_merg.write("file '%s'\n" % tmp_clip_path)
        file_merg.close()
        cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
        os.system(cmd)
        os.remove(tmp_clip_path)
        os.remove(file_merg_path)
        if is_del:
            os.remove(audio_path)
        return final_clip_path
    except:
        pass
    return None
def create_loop_audio(audio_path, loop_duration):
    if loop_duration < 0 : loop_duration = 600
    try:
        audio_clip = AudioFileClip(audio_path)
        clip_duration = audio_clip.duration
        audio_clip.close()
        if clip_duration > loop_duration:
            return audio_path
        tmp_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(audio_path))
        shutil.copyfile(audio_path, tmp_clip_path)
        times = int(math.ceil(loop_duration / clip_duration))
        file_merg_path = os.path.join(get_dir('coolbg_ffmpeg') , str(uuid.uuid4()))
        final_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final-' + os.path.basename(audio_path))
        file_merg = open(file_merg_path, "a")
        for i in range(times):
            file_merg.write("file '%s'\n" % tmp_clip_path)
        file_merg.close()
        cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
        os.system(cmd)
        os.remove(tmp_clip_path)
        os.remove(file_merg_path)
        clip = AudioFileClip(final_clip_path)
        clip_duration = clip.duration
        clip.close()
        if clip_duration < loop_duration:
            return None
        return final_clip_path
    except:
        pass
    return None
def add_null_sound(input):
    output=  os.path.join(get_dir('coolbg_ffmpeg') ,str(uuid.uuid4()) + '-' + os.path.basename(input))
    cmd = f"ffmpeg -f lavfi -i anullsrc -i \"{input}\" -c:v copy -b:a 128000 -ar 44100 -c:a mp3 -map 0:a -map 1:v -shortest \"{output}\""
    os.system(cmd)
    return output
def merge_list_video(vids, is_del=True):
    file_merg_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()))
    final_clip_path = os.path.join(get_dir('results') , str(uuid.uuid4()) + '-final-' + os.path.basename(vids[0]))
    file_merg = open(file_merg_path, "a")
    arrtmp = []
    for vid in vids:
        tmp_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(vid))
        shutil.copyfile(vid, tmp_clip_path)
        if is_del:
            os.remove(vid)
        file_merg.write("file '%s'\n" % tmp_clip_path)
        arrtmp.append(tmp_clip_path)
    file_merg.close()
    cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
    os.system(cmd)
    os.remove(file_merg_path)
    for item in arrtmp:
        os.remove(item)
    clip = VideoFileClip(final_clip_path)
    clip_duration = clip.duration
    clip.close()
    if clip_duration < 1:
        return None
    return final_clip_path


def merge_intro_outro(clip_path, intro = None, outro = None):
    arrVids=[]
    if not intro and not outro:
        return clip_path
    if intro:
        arrVids.append(intro)
    arrVids.append(clip_path)
    if outro:
        arrVids.append(outro)
    return merge_list_video(arrVids, True)

def create_video_audio(clip_path, audio_path, rs_path=None, is_del=True):
    try:
        tmp_clip_path_z=rs_path
        if tmp_clip_path_z is None:
            tmp_clip_path_z = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final.mp4')
        cmd = f"ffmpeg -i \"{clip_path}\" -i \"{audio_path}\" -vcodec copy -acodec copy -map 0:v -map 1:a -shortest -flags global_header -y \"{tmp_clip_path_z}\""
        os.system(cmd)
        if is_del:
            os.remove(clip_path)
            os.remove(audio_path)
    except:
        tmp_clip_path_z = None
        pass
    return tmp_clip_path_z
def convert_gif(video_path, is_del=True):
    tmp_clip_path_z = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-gif.avi')
    cmd=f"ffmpeg -i \"{video_path}\"  -c:v ffv1 \"{tmp_clip_path_z}\""
    os.system(cmd)
    if is_del:
        os.remove(video_path)
    return tmp_clip_path_z
def convert_gif_moviepy(video_path, is_del=True):
    tmp_clip_path_z = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-gif.avi')
    clip = VideoFileClip(video_path,audio=False, has_mask=True)
    clip.write_videofile(tmp_clip_path_z, fps=clip.fps, codec='libx264')
    clip.close()
    if is_del:
        os.remove(video_path)
    return tmp_clip_path_z
def create_loop(clip_path, loop_duration, can_loopable = True):
    try:
        clip = VideoFileClip(clip_path)
        if not can_loopable:
            try:
                if clip.duration > loop_duration:
                    return clip_path
                clip = make_loopable.make_loopable(clip, 0.5)
                tmp_clip_path_z = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(clip_path))
                #tmp_clip_path_z_resync = get_dir('coolbg_ffmpeg') + str(uuid.uuid4()) + '-re-sync-' + os.path.basename(clip_path).split(".")[0]+".avi"
                clip.write_videofile(tmp_clip_path_z, fps=clip.fps, codec='libx264')
                clip.close()
                # cmd = "ffmpeg -y -i \"%s\" \"%s\"" % (tmp_clip_path_z, tmp_clip_path_z_resync)
                # os.system(cmd)
                # os.remove(tmp_clip_path_z)
                clip = VideoFileClip(tmp_clip_path_z)
                tmp_clip_path = tmp_clip_path_z
            except:
                pass
        else:
            tmp_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-' + os.path.basename(clip_path))
            shutil.copyfile(clip_path, tmp_clip_path)

        clip_duration = clip.duration
        clip.close()
        if clip_duration > loop_duration:
            return clip_path
        times = int(math.ceil(loop_duration /clip_duration))+1
        # print(times)
        file_merg_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()))
        final_clip_path = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + '-final-' + os.path.basename(clip_path))
        file_merg = open(file_merg_path, "a")
        for i in range(times):
            file_merg.write("file '%s'\n" % tmp_clip_path)
        file_merg.close()
        cmd = "ffmpeg -y -f concat -safe 0 -i \"%s\" -codec copy \"%s\"" % (file_merg_path, final_clip_path)
        os.system(cmd)
        os.remove(tmp_clip_path)
        os.remove(file_merg_path)
        clip = VideoFileClip(final_clip_path)
        clip_duration = clip.duration
        clip.close()
        if clip_duration < loop_duration:
            return None
        return final_clip_path
    except:
        return None
