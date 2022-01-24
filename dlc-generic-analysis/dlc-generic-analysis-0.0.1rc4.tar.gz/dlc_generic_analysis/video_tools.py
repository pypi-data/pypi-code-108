import os
import moviepy.editor


def resize(path: str, width):
    clip = moviepy.editor.VideoFileClip(path)
    clip_resized = clip.resize(width=width)
    filename, extension = os.path.splitext(path)
    clip_resized.write_videofile(filename + "_resized" + extension)
