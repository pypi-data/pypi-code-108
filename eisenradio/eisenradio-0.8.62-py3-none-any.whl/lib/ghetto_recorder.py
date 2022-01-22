# 0.1.2a
##################################################################################
#   MIT License
#
#   Copyright (c) [2021] [René Horn]
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
###################################################################################

import io
import os
import queue
import random
##############
import shutil
import threading
import urllib.parse
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from time import sleep, strftime, time
from urllib.error import URLError, HTTPError

import urllib3
from eisenradio.api import ghettoApi


# logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)
# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

version = '0.8.30'
print(f'{version} ghettorecorder (eisen_radio module)')  # ########## version #############


class GBase:
    # class attribute
    dict_exit = {}  # all "single" started (this time four, each station)
    dict_error = {}

    sleeper = 2  # for exit of all threads
    pool = ThreadPoolExecutor(200)
    radio_base_dir = os.path.dirname(os.path.abspath(__file__)) + '//radiostations'  # if not set set_radio_base_dir()
    settings_path = os.path.dirname(os.path.abspath(__file__)) + '//settings.ini'  # if not set in set_settings_path()
    path = os.getcwd()
    path_to = path + '//'
    timer = 0

    def __init__(self, radio_base_dir=None, settings_path=None):
        self.instance_attr_time = 0
        self.trigger = False
        self.radio_base_dir = radio_base_dir
        self.settings_path = settings_path

    @staticmethod
    def make_directory(str_path):
        try:
            os.mkdir(str_path)
        except FileExistsError:
            pass
        else:
            print('\t--> created directory: ' + str_path)

    @staticmethod
    def remove_special_chars(str_name):
        # cleanup for writing files and folders

        # my_str = "hey th~!ere. /\ coolleagues?! Straße"
        ret_value = str_name.translate({ord(string): "" for string in '"!@#$%^*()[]{};:,./<>?\|`~=+"""'})
        return ret_value

    @staticmethod
    def this_time():
        time = strftime("%Y-%m-%d %H:%M:%S")
        return time

    def countdown(self, instance_attr_time):
        t = 0
        while not t == instance_attr_time:
            sleep(1)
            self.timer = t
            print(self.timer)
            t += 1
            if t == 0:
                self.trigger = True
        print(f' done {instance_attr_time} {self.trigger}')
        return self.trigger


class GIni(GBase):  # remnant of command line version

    ini_keys = {}  # cls attribute to store selections from ini file, works because of key[key] = value, else not
    srv_param_dict = {}  # all ini keys plus short url, suffix, server type stuff
    start_stop_recording = {}  # ini key: 'start' , 'stop'; while loop check start, working check stop go upper while
    # ini_key + '_single_title', ini_key + '_rec_from_here'
    cost_current_ini = ''  # ini key for cost_dict calc / should be a dict
    cost_dict = {}  # stores len of received headers to calc amount of data searching strings per day
    fail_meta_dict = {}  # can not read metadata from stream, no data
    # list of search strings delimiter blank, first key is named 'STRINGS': Britney Phantom ไม่เคยจะจำ Elton Jim techno
    search_dict = {'STRINGS': 'Britney Spears ไม่เคยจะจำ Elton AC/DC techno Band feat. mix'}  # only show it is working
    list_items = []  # radio key names for display in terminal
    search_title_keys_list = []  # radio short keys, not start recording all streams, only searched titles
    content_type = {}  # header info audio/mpeg

    @staticmethod
    def parse_url_simple_url(radio_url):
        url = radio_url  # whole url is used for connection to radio server

        # 'http:' is first [0], 'ip:port/xxx/yyy' second item [1] in list_url_protocol
        list_url_protocol = url.split("//")
        list_url_ip_port = list_url_protocol[1].split("/")  # 'ip:port' is first item in list_url_ip_port
        radio_simple_url = list_url_protocol[0] + '//' + list_url_ip_port[0]
        return radio_simple_url


class GNet(GBase):
    http_pool = urllib3.PoolManager(num_pools=200)

    @staticmethod
    def load_url(url):
        # returns status code, if server is alive conn.getcode()
        # use urllib, urllib3 causes response to wait "forever" and timeout is not working either
        # print(f' load_url {url}')
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.getcode()

    @staticmethod
    def is_server_alive(url, key):
        # don't delete - urllib3 timeout=5, placebo, retries=None or =2, screw yourself, since half of conn. die
        # we have server up, but content not presented - zombie
        try:
            GNet.load_url(url)
        except HTTPError:  # lots of strange configured web server

            print('HTTPError')
            GBase.dict_error[key] = 'HTTPError - check radio homepage'
            return True
        except URLError as error:  # <urlopen error timed out>
            print(f' ---> {key} server failed: {error} (no recording) {url}')
            GBase.dict_error[key] = error
            print('URLError')
            return False
        return True

    @staticmethod
    def stream_filetype_url(url, key):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                headers = response.getheader('Content-Type')
        except Exception as ex:
            print(ex)
            return False

        content_type = ''
        if headers == 'audio/aacp' or headers == 'application/aacp':
            content_type = '.aacp'
        if headers == 'audio/aac':
            content_type = '.aac'
        if headers == 'audio/ogg' or headers == 'application/ogg':
            content_type = '.ogg'
        if headers == 'audio/mpeg':
            content_type = '.mp3'
        if headers == 'audio/x-mpegurl' or headers == 'text/html':
            content_type = '.m3u'
        # application/x-winamp-playlist , audio/scpls , audio/x-scpls ,  audio/x-mpegurl

        try:
            GIni.content_type[key] = headers
            if len(headers) <= 5:
                GIni.content_type[key] = 'audio/mpeg'
            # print(f' stream_filetype_url: {GIni.content_type[key]}')
        except Exception as e:
            print(e)
            pass

        return content_type


class GRecorder:
    unknown_title_name = 'untitled_full_record_'
    path_to_song_dict = {}  # {station : file path}
    current_song_dict = {}  # each thread writes the new title to the station key name {station : title}
    start_write_command = {}  # recorder head thread set command to copy first file
    search_pattern_found = {}

    record_active_dict = {}
    listen_active_dict = {}
    ghetto_measure = {}
    ghettoApi.init_ghetto_measurements(ghetto_measure)
    ghetto_analyser_dict = {}
    ghettoApi.init_ghetto_analyser(ghetto_analyser_dict)
    fifo_http_chunk_queue = queue.Queue(maxsize=10)

    @staticmethod  # copy keep-alive timeout=3000
    def ghetto_recorder_display_title(url, ini_key):
        # print(f' ghetto_recorder_display_title: {ini_key}')
        update_terminal = ''.encode('utf-8')
        stream_song_name = GRecorder.current_song_dict[ini_key]
        GIni.fail_meta_dict[url] = 'False'  # message display or not
        GRecorder.search_pattern_found[ini_key] = False

        while not GBase.dict_exit[ini_key]:

            if not len(stream_song_name) <= 2:
                #  GRecorder.current_song_dict[ini_key] = stream_song_name  # WRITE SONG NAME   # :DEACTIVATED:
                stream_song_name = GRecorder.current_song_dict[ini_key]  # :REVERSE:

                if not update_terminal == stream_song_name:
                    update_terminal = stream_song_name
                    try:
                        print(f'\t\t {GBase.this_time().split()[1]} title on {ini_key}: \t {update_terminal}')
                        # see what häppens, góod unìt têst case
                    except UnicodeEncodeError:
                        print('\t\t title on ' + ini_key + ':\t' + 'unicode error (check "$ localectl status")')
                        print('\t\t title on ' + ini_key + ':\t' + 'consider to add additional language support.')

                    except Exception as ex:
                        print('\t\t title on ' + ini_key + ':\t' + 'unknown error (print to your terminal)')
                        print(ex)
                    else:
                        pass
            # give recorder command to record, if we got a match from search gui
            #

            try:
                for _ in GIni.search_title_keys_list:
                    if _ == ini_key:
                        # search option was checked,
                        # call - def search_pattern_start_record, search string match?
                        got_it = GRecorder.search_pattern_start_record(stream_song_name, ini_key)
                        if got_it:
                            GIni.start_stop_recording[ini_key] = 'start'
                        else:
                            GIni.start_stop_recording[ini_key] = 'stop'
                            GRecorder.search_pattern_found[ini_key] = False

            except Exception as ex:
                print(ex)

            for sec in range(GBase.sleeper):
                sleep(1)
                if GBase.dict_exit[ini_key]:
                    # print(f' stop get title {ini_key}')
                    break
            # To Do: make (complete) fake headers to keep connection up
            #        sync sleep time with recorder
            #        one file record with name

    @staticmethod
    def search_pattern_start_record(title, ini_key):
        # search title for strings to see if we should start recording this
        search_list = []  # chop the string

        try:
            strings = GIni.search_dict[ini_key]  # dict with user search strings
            search_list = strings.encode('utf-8').lower().split(b' ')
        except KeyError:
            pass

        for search_str in search_list:

            if not len(search_str) <= 1:  # b'' match problem

                if not title.encode('utf-8').lower().find(search_str) == -1:  # find() returns -1, if not found
                    if not GRecorder.search_pattern_found[ini_key]:
                        print(f'<<<< match station: {ini_key} phrase: {search_str}')
                        GRecorder.search_pattern_found[ini_key] = True
                    return True
        return False

    @staticmethod
    def ghetto_recorder_head(directory_save, stream_suffix, radio_short_key):
        # target: tail works without brain until brain call interrupt
        # print(f' ghetto_recorder_head -- {radio_short_key}')

        sleep(GBase.sleeper)
        # reader must work (conn. url) for writing the path from title name, can have a loop here
        fresh_song = 'False'
        first_record = True
        brake_loop = False
        GRecorder.start_write_command[radio_short_key] = False

        stream_song_name = GRecorder.current_song_dict[radio_short_key]

        try:
            GBase.make_directory(GBase.radio_base_dir)
        except FileNotFoundError:
            GRecorder.current_song_dict[radio_short_key] = '[{-_-}] ZZZzz zz z... Recorder Failure!'
            GBase.dict_exit[radio_short_key] = True  # all radio_short_key treads-will-stop
            print('\t---> Recorder Write Failure in : ' + GBase.radio_base_dir)
            return

        try:
            GBase.make_directory(GBase.radio_base_dir + '//' + radio_short_key)
        except OSError:
            # "heyth~!ere./\coolleagues?!Straße"
            GRecorder.current_song_dict[radio_short_key] = '[{-_-}] ZZZzz  Recorder Failure !!! DIRECTORY !!!'
            print('\t---> Recorder Write Failure in : ' + GBase.radio_base_dir + '//' + radio_short_key)
            sleep(5)
            GBase.dict_exit[radio_short_key] = True  # all radio_short_key treads-will-stop

            return

        while not brake_loop:
            i = 0
            while not GBase.dict_exit[radio_short_key]:
                if not fresh_song == stream_song_name:

                    if i == 5:
                        print(f' \t\t\t\t\t\t(  (  ( (Eisen Radio) )  )  ) )')
                        i = 0
                    i += 1

                    fresh_song = stream_song_name  # check if it can be removed, we look in a dict now
                    clean_name = GBase.remove_special_chars(stream_song_name)
                    if clean_name == GRecorder.unknown_title_name:  # init name of title on startup
                        clean_name = clean_name + radio_short_key + '_date_' + GBase.this_time()
                        clean_name = GBase.remove_special_chars(clean_name)

                    if first_record:
                        fresh_file_path = directory_save + '//' + '_incomplete_' + str(clean_name) + str(stream_suffix)
                        brake_loop = True
                        GRecorder.path_to_song_dict[radio_short_key] = fresh_file_path
                        GRecorder.start_write_command[radio_short_key] = True

                        first_record = False
                    else:
                        fresh_file_path = directory_save + '//' + clean_name + stream_suffix
                        GRecorder.path_to_song_dict[radio_short_key] = fresh_file_path  # NEW PATH ... ... ...

                    if GBase.dict_exit[radio_short_key]:
                        # print(f' exit head__ {radio_short_key}')
                        break

                    while not GBase.dict_exit[radio_short_key]:

                        stream_song_name = GRecorder.current_song_dict[radio_short_key]
                        if not fresh_song == stream_song_name:
                            break

                        for sec in range(5):
                            if GBase.dict_exit[radio_short_key]:
                                fresh_file_path = directory_save + '//' + '_incomplete_' + clean_name + stream_suffix
                                GRecorder.path_to_song_dict[radio_short_key] = fresh_file_path
                                # print(f' exit head_ {radio_short_key}')
                                break
                            sleep(1)

    @staticmethod  # org
    def ghetto_recorder_tail(url, key, path_to_save, suffix):
        # shall be as dump as possible

        while not GBase.dict_exit[key]:
            try:
                if GRecorder.start_write_command[key]:
                    break
            except KeyError:
                pass
            else:
                sleep(.1)

        stream_request_size = io.DEFAULT_BUFFER_SIZE
        old_time = time()
        request = ''
        rand_short = random.randrange(4, 13, 3)

        ghetto_recorder = path_to_save + '//__ghetto_recorder' + str(suffix)
        try:
            ghetto_copy = GRecorder.path_to_song_dict[key]
        except KeyError:
            GRecorder.current_song_dict[key] = '[{-_-}] ZZZzz zz z... Recorder Failure!'
            GBase.dict_exit[key] = True  # all key treads-will-stop
            return
        try:
            request = GNet.http_pool.request('GET', url,
                                             headers={'Connection': 'keep-alive'},
                                             timeout=3000,
                                             preload_content=False)
        except Exception as e:
            print(e)
            pass

        while not GBase.dict_exit[key]:
            with open(ghetto_recorder, 'wb') as record_file:

                for chunk in request.stream(stream_request_size):  # chunks to file

                    # ############################################################## rec
                    # print(f'rec {GRecorder.record_active_dict[key]}')
                    # print(f'lis {GRecorder.listen_active_dict[key]}')

                    if GRecorder.record_active_dict[key]:
                        record_file.write(chunk)
                        if not GRecorder.listen_active_dict[key]:
                            pass
                            # Baustelle
                            # GRecorder.fifo_http_chunk_queue.put(chunk)
                            # GRecorder.ghetto_analyser_dict[key + ',analyser'] = GRecorder.fifo_http_chunk_queue
                    if GRecorder.listen_active_dict[key]:
                        pass
                        # GRecorder.fifo_http_chunk_queue.put(chunk)
                        # GRecorder.ghetto_analyser_dict[key + ',analyser'] = GRecorder.fifo_http_chunk_queue
                        # print(f'listen ---- Baustelle ----- {GRecorder.listen_active_dict[key]}')
                    # ############################################################## rec
                    if not ghetto_copy == GRecorder.path_to_song_dict[key]:

                        try:
                            if os.path.exists(ghetto_copy):
                                os.remove(ghetto_copy)
                            record_file.flush()

                            ghetto_size = os.path.getsize(ghetto_recorder)
                            if int(ghetto_size) >= int(stream_request_size):
                                shutil.copyfile(ghetto_recorder, ghetto_copy)
                        except Exception as ex:
                            print(ex)
                        else:
                            record_file.truncate()
                            record_file.seek(0)

                    ghetto_copy = GRecorder.path_to_song_dict[key]  # SET NEW PATH (title) after copy
                    # #################################
                    if time() - old_time > rand_short:
                        old_time = time()
                        rh = request.headers
                        rand_short = random.randrange(4, 12, 2)

                    if not chunk:
                        request = GNet.http_pool.request('GET', url,
                                                         headers={'Connection': 'keep-alive'},
                                                         timeout=3000,
                                                         preload_content=False)
                        rh = request.headers  # into oblivion
                        break
                    if GBase.dict_exit[key]:
                        sleep(2)  # wait for last file name _incomplete_.....
                        try:
                            record_file.flush()

                            ghetto_size = os.path.getsize(ghetto_recorder)
                            # print(f' ghetto_recorder: {int(ghetto_size)}')
                            # print(f' stream_request_size): {int(stream_request_size)}')

                            if int(ghetto_size) >= int(stream_request_size):
                                ghetto_copy = GRecorder.path_to_song_dict[key]  # full path last file name
                                print(f'\t "{key}" last file (marked: _incomplete_): '
                                      f'{GRecorder.current_song_dict[key]} ')

                                shutil.copyfile(ghetto_recorder, ghetto_copy)
                            record_file.close()

                            if os.path.exists(ghetto_recorder):
                                os.remove(ghetto_recorder)
                        except UnicodeEncodeError:
                            print(f' {key} copy last file (marked: _incomplete_):')
                        except Exception as ex:
                            print(ex)
                        break
            if GBase.dict_exit[key]:
                # print(f' exit file record {key}')
                break

    @staticmethod
    def get_metadata_from_stream_loop(url, key):
        # urllib3 request.stream with headers={'Icy-MetaData': '1'} , keep open (mdr, swr, br5) test

        response = ''
        request = ''
        title = ''
        metadata_content = ''
        old_time = time()
        rand_short = random.randrange(4, 12, 2)
        rand_long = random.randrange(50, 80, 1)

        while not GBase.dict_exit[key]:
            try:
                response = GNet.http_pool.request('GET', url,
                                                  headers={'Connection': 'keep-alive'},
                                                  timeout=3000, preload_content=False)
            except Exception as e:
                print(e)
                pass

            while not GBase.dict_exit[key]:

                if time() - old_time > rand_short:
                    old_time = time()
                    rh = response.headers  # keep conn. alive
                    rand_short = random.randrange(4, 12, 2)
                    # print(response.headers)

                if time() - old_time > rand_long:  # new connection
                    old_time = time()
                    rand_long = random.randrange(50, 80, 1)
                    break
                try:
                    start_time = time()
                    request = GNet.http_pool.request('GET', url,
                                                     headers={'Icy-MetaData': '1'},
                                                     preload_content=False)
                    try:
                        GRecorder.ghetto_measure[key + ',request_time'] = round((time() - start_time) * 1000)
                        GRecorder.ghetto_measure[key + ',suffix'] = request.headers['content-type']
                    except KeyError:
                        pass
                    try:
                        icy_genre = request.headers["icy-genre"]  # [0:30]
                        icy_name = request.headers["icy-name"]
                        icy_br = request.headers["icy-br"]
                        GRecorder.ghetto_measure[key + ",icy_genre"] = icy_genre
                        GRecorder.ghetto_measure[key + ",icy_name"] = icy_name
                        GRecorder.ghetto_measure[key + ",icy_br"] = icy_br
                    except KeyError:
                        pass
                    # print(request.headers)
                except Exception as e:
                    print(e)
                    pass

                try:
                    pass

                except KeyError:
                    pass
                try:
                    icy_metadata = request.headers['icy-metaint']
                    icy_metadata = int(icy_metadata)

                    request.read(icy_metadata)
                    chunk_1b = request.read(1)
                    chunk_1b = ord(chunk_1b)
                    read_bytes = chunk_1b * 16
                    read_bytes = int(read_bytes)
                    metadata_content = request.read(read_bytes)
                except KeyError:
                    pass
                try:
                    metadata_content = metadata_content.decode('utf-8')
                    title_info = metadata_content.split(";")
                    title_info = title_info[0].split("=")
                    title = str(title_info[1])
                    title = GBase.remove_special_chars(title)

                    request.release_conn()  # REQUEST one shot anyway
                    # print(f' -> {key} + {title}')
                except IndexError:
                    try:
                        metadata_content = metadata_content
                        title_info = metadata_content.split(";")
                        title_info = title_info[0].split("=")
                        title = str(title_info[1])
                        title = GBase.remove_special_chars(title)
                    except Exception:
                        request.release_conn()  # REQUEST one shot anyway
                        pass

                else:
                    try:
                        if title[0] == "'" and title[-1] == "'":
                            GRecorder.current_song_dict[key] = title[1:-1]
                        else:
                            GRecorder.current_song_dict[key] = title
                        # print(f' -> {key} + {GRecorder.current_song_dict[key]}')
                    except KeyError:
                        pass
                    except Exception as e:
                        print(e)
                        pass
                    else:
                        for sec in range(rand_short):
                            if GBase.dict_exit[key]:
                                # print(f' out reader {key}')
                                break
                            sleep(1)

    @staticmethod
    def playlist_m3u(url, key):
        # returns the first server of the playlist (not only m3u)
        try:
            read_url = GNet.http_pool.request('GET', url, preload_content=False)
        except Exception as ex:
            print(ex)
        else:
            file = read_url.read().decode('utf-8')

            m3u_lines = file.split("\n")
            # print(' \n    m3u_lines    ' + file)
            m3u_lines = list(filter(None, m3u_lines))  # remove empty rows
            m3u_streams = []
            for row_url in m3u_lines:
                if row_url[0:4].lower() == 'http'.lower():
                    m3u_streams.append(row_url)  # not to lower :)
                    # print(len(m3u_streams))

            if len(m3u_streams) > 1:
                print(f' {key} Have more than one server in playlist_m3u. !!! Take first stream available.')
                play_server = m3u_streams[0]
                return play_server
            if len(m3u_streams) == 1:
                # print(' One server found in playlist_m3u')
                play_server = m3u_streams[0]
                return play_server
            if len(m3u_streams) == 0:
                # print(' No http ... server found in playlist_m3u !!! -EXIT-')
                return False


def check_alive_playlist_container(str_key, str_url):
    # playlist url?
    if str_url[-4:] == '.m3u' or str_url[-4:] == '.pls':  # or url[-5:] == '.m3u8' or url[-5:] == '.xspf':
        # take first from the list
        is_playlist_server = GRecorder.playlist_m3u(str_url, str_key)

        if not is_playlist_server == '':
            if GNet.is_server_alive(str_url, str_key):
                str_url = is_playlist_server
            else:
                print('   --> playlist_server server failed, no recording')
            return str_url
    else:
        GNet.is_server_alive(str_url, str_key)
        return False


def record(ini_key, url):
    stream_suffix = GNet.stream_filetype_url(url, ini_key)  # ret and write in content-type dict
    GRecorder.current_song_dict[ini_key] = GRecorder.unknown_title_name
    GIni.start_stop_recording[ini_key] = 'start'
    # GIni.start_stop_recording[ini_key] = 'stop'            # init it here, should be set via user interface
    GIni.start_stop_recording[ini_key + '_adv'] = 'start_from_here'  # MUST be set or a key error in record def:

    dir_save = GBase.radio_base_dir + '//' + ini_key

    threading.Thread(target=GRecorder.ghetto_recorder_display_title,
                     args=(url, ini_key),
                     daemon=True).start()
    threading.Thread(target=GRecorder.ghetto_recorder_head,
                     args=(dir_save, stream_suffix, ini_key),
                     daemon=True).start()
    threading.Thread(target=GRecorder.ghetto_recorder_tail,
                     args=(url, ini_key, dir_save, stream_suffix),
                     daemon=True).start()
    threading.Thread(target=GRecorder.get_metadata_from_stream_loop,
                     args=(url, ini_key),
                     daemon=True).start()

    # ################################## end ########################################
    # this version ends here. no loop
