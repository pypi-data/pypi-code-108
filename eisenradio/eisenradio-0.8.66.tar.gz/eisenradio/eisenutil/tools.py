import configparser
from os import path
from flask import flash
from eisenradio.lib.eisdb import delete_radio, get_db_connection, get_db_smaller, get_db_path, status_read_status_set
from eisenradio.eisenutil.eisutil import is_in_db_view


def delete_all_radios():
    rv = False
    posts = get_radios()
    for radio in posts:
        rv = delete_radio(radio['id'])
        if rv:
            rv = True
        if not rv:
            rv = False
    # vakuum db
    get_db_smaller()
    flash('Deletion Done', 'success')
    return rv


def export_radios():
    # BLUES_UK = http://149.255.59.3:8232/stream
    rv = True
    radio_url_dict = {}

    db_path = get_db_path()
    export_path = path.abspath(path.dirname(db_path))

    try:
        posts = get_radios()
        for station in posts:
            station_name = status_read_status_set(False, 'posts', 'title', station['id'])
            station_url = status_read_status_set(False, 'posts', 'content', station['id'])
            radio_url_dict[station_name] = station_url
    except KeyError:
        rv = False
    except ValueError:
        rv = False

    try:
        with open(path.join(export_path, 'settings.ini'), 'w') as writer:
            writer.write('[GLOBAL]' + '\n')
            writer.write('[STATIONS]' + '\n')
            for radio, url in radio_url_dict.items():
                writer.write(radio + ' = ' + url + '\n')
                writer.flush()
    except OSError:
        rv = False
    return rv


def import_radios(path_ini):
    ini_dict = find_all_in_stations(path_ini)
    if ini_dict:
        rv = db_import_ini(ini_dict)
        if rv:
            return True
    return False


def find_all_in_stations(path_ini):
    config = configparser.ConfigParser()  # imported library to work with .ini files
    try:
        config.read_file(open(path_ini))
    except FileNotFoundError as ex:
        print(ex)
        return False
    else:
        station_dict = config['STATIONS']
        return station_dict


def db_import_ini(ini_dict):
    download_path = ''
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()

    for key, value in ini_dict.items():
        title = key
        content = value

        i = 1
        search_str = title
        while is_in_db_view(search_str):

            if not is_in_db_view(search_str + '__' + str(i)):
                title = search_str + '__' + str(i)
                break
            i += i

        # if we later want extra save folders for each radio
        try:
            download_path = posts[0]["download_path"]
        except IndexError:
            print(' looks like the first radio to create, no save to path set')
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        try:
            if download_path:
                conn.execute('INSERT INTO posts (title, content, download_path) VALUES (?, ?, ?)',
                             (title, content, download_path))
        except ValueError:
            conn.close()
            return False
    conn.commit()
    conn.close()
    return True


def get_radios():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return posts
