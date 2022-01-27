from ytspace.sql_funcs import *;
from ytspace.yt_funcs import *;

connection = connect_to_mysql()
cursor = cursor_connection(connection)

def query(*args):
    cursor.execute(*args)
    try: connection.commit()
    except: pass

def yt_add(video_link, audio = False):
    media, video_music, media_type = yt_download(video_link, audio = audio)

    media_record = (media_type[0],) + media
    query(add_media, media_record)

    media_id = get_last_id()

    video_music_record = (media_id,) + video_music
    query(add_video_music.format(media_type[1]), video_music_record)

    return media_id, video_music[0]

def yt_delete(media_id):
    table_name = get_table_name(media_id)

    query(delete_video_music.format(table_name, media_id))
    query(delete_media.format(media_id))

def get_table_name(media_id):
    query(find_type.format(media_id))
    media_type = [x[0] for x in cursor][0]

    return "music" if media_type == 0 else "videos"

def get_last_id():
    query("SELECT id FROM media ORDER BY id DESC LIMIT 1")

    return [i[0] for i in cursor][0]
