import os
import threading
from time import sleep
from flask import jsonify, request, flash, redirect, url_for

import eisenradio.lib.ghetto_recorder as ghetto
from eisenradio.lib.eisdb import get_db_connection, status_read_status_set, get_download_dir, get_db_smaller
from eisenradio.api import ghettoApi


first_run_index = True
listen_btn = False

status_listen_btn_dict = {}  # {table id 15: 1 } on
status_record_btn_dict = {}
radios_in_view_dict = {}
ghettoApi.init_lis_btn_dict(status_listen_btn_dict)
ghettoApi.init_rec_btn_dict(status_record_btn_dict)
ghettoApi.init_radios_in_view(radios_in_view_dict)

active_streamer_dict = {}

last_btn_id = None  # current button pressed, or btn predecessor / to redraw, if next is pressed / first is null->err
listen_last_url = None
combo_master_timer = 0
progress_master_percent = 0

active_displays = {}
eisen_threads = []


def enum_radios():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return posts


def index_first_run(posts):
    global first_run_index
    if first_run_index:
        first_run_index = False
        check_write_protected()
        ghetto.GBase.pool.submit(progress_timer)

        for row in posts:
            # init btn not pressed
            status_listen_btn_dict[row['id']] = 0
            status_record_btn_dict[row['id']] = 0
            # api
            radios_in_view_dict[row['id']] = status_read_status_set(False, 'posts', 'title', row['id'])


def curr_radio_listen():
    current_station = ''
    current_table_id = ''
    for key_table_id, val in status_listen_btn_dict.items():
        if val:
            current_station = status_read_status_set(False, 'posts', 'title', key_table_id)
            current_table_id = key_table_id
    return current_station, current_table_id


def index_posts_clicked(post_request):
    # this version does not have a relay server
    global listen_btn
    global last_btn_id
    global listen_last_url

    try:
        button_list = post_request['name'].split('_')
    except KeyError:
        return
    table_id = button_list[1]
    button = button_list[0]
    current_station = ''

    if button == 'Listen':  # turn values, update button status dict

        try:
            # new radio not yet in dict, deactivate till restart, buttons have no function
            rv = status_listen_btn_dict[int(table_id)]
            rv_station_lis = status_read_status_set(False, 'posts', 'title', table_id)
        except KeyError:
            return False
        if status_listen_btn_dict[int(table_id)]:  # button was down
            status_listen_btn_dict[int(table_id)] = 0
            dispatch_master(int(table_id), 'Listen', 0)
            if not last_btn_id == table_id:
                return jsonify({'result': 'auto_click, no_audio_action', 'table_ident': current_station,
                                'radio_table_id': table_id, 'class_val': post_request['class_val']})
        else:
            status_listen_btn_dict[int(table_id)] = 1  # button just pressed, register state, new station

            if not last_btn_id == table_id:  # other btn pressed
                if listen_btn:  # was playing before actual btn
                    switch_btn = last_btn_id  # press abandoned btn, play new url
                    last_btn_id = table_id
                    listen_last_url = query_radio_url(table_id)  # radio url
                    dispatch_master(int(table_id), 'Listen', 1)
                    current_station = status_read_status_set(False, 'posts', 'title', table_id)
                    # trigger auto_click
                    return jsonify(
                        {'former_button_to_switch': switch_btn,
                         'query_url': listen_last_url,
                         'if not last_btn_id == table_id': '------ last_btn_id --------',
                         'result': 'activate_audio', 'table_ident': current_station, 'radio_table_id': table_id,
                         'class_val': post_request['class_val']})

            dispatch_master(int(table_id), 'Listen', 1)

        listen_last_url = query_radio_url(table_id)  # radio url
        last_btn_id = table_id

        listen_btn = False
        for val in status_listen_btn_dict:
            if status_listen_btn_dict[val]:
                listen_btn = True
                break

        if listen_btn:
            current_station = status_read_status_set(False, 'posts', 'title', table_id)
            return jsonify(
                {'result': 'activate_audio', 'former_button_to_switch': False, 'buttons': button,
                 'query_url': listen_last_url,
                 'table_ident': current_station, 'radio_table_id': table_id, 'class_val': post_request['class_val']})
        else:
            listen_last_url = ''
            return jsonify(
                {'result': 'deactivate_audio', 'former_button_to_switch': False, 'buttons': button,
                 'query_url': listen_last_url,
                 'table_ident': current_station, 'radio_table_id': table_id, 'class_val': post_request['class_val']})

    if button == 'Record':
        try:
            rv = status_record_btn_dict[int(table_id)]
        except KeyError:
            return False

        conn = get_db_connection()
        rec_station = status_read_status_set(False, 'posts', 'title', table_id)
        conn.close()

        if status_record_btn_dict[int(table_id)]:
            del active_streamer_dict[rec_station]
            status_record_btn_dict[int(table_id)] = 0
            dispatch_master(int(table_id), 'Record', 0)
        else:
            active_streamer_dict[rec_station] = str(table_id)
            status_record_btn_dict[int(table_id)] = 1
            dispatch_master(int(table_id), 'Record', 1)

    """make combo box with anchor jumper"""
    json_str = ''
    for streamer_name, streamer_id in active_streamer_dict.items():
        json_str = json_str + str(streamer_name) + '=' + str(streamer_id) + ','
    if not json_str:
        json_str = str('empty_json')

    return jsonify(
        {'result': 'no_audio_result',
         'buttons': button, 'rec_btn_id': table_id, 'streamer': json_str,
         'former_button_to_switch': False,
         'query_url': listen_last_url,
         'radio_table_id': table_id, 'class_val': post_request['class_val']})


def query_radio_url(table_id):
    str_url = status_read_status_set(
        False, 'posts', 'content', table_id)
    return str_url


def set_radio_path(table_id):
    radio_path = status_read_status_set(
        False, 'posts', 'download_path', table_id)
    ghetto.GBase.radio_base_dir = radio_path


def dispatch_master(table_id, button, status):
    set_radio_path(table_id)
    str_radio = status_read_status_set(
        False, 'posts', 'title', table_id)

    if button == 'Listen':
        dispatch_listen_btn(str_radio, table_id, status)

    elif button == 'Record':
        dispatch_record_btn(str_radio, table_id, status)


def dispatch_listen_btn(str_radio, table_id, listen_status):

    if listen_status:
        ghetto.GRecorder.listen_active_dict[str_radio] = True  # later needed for relay

        if not status_record_btn_dict[table_id]:  # recorder not started / index_posts_ajax()
            ghetto.GRecorder.record_active_dict[str_radio] = False  # pass record write, else key error (to fix)
            dispatch_record_title(table_id, False, True)  # start title grabber
            # ---org------------------ Baustelle ----- listen record as one stream (cors pb.) http server
            # dispatch_record_title(table_id, True, False)
    if not listen_status:
        ghetto.GRecorder.listen_active_dict[str_radio] = False
        if not status_record_btn_dict[table_id]:
            dispatch_recorder_stop(table_id)


def dispatch_record_btn(str_radio, table_id, record_status):

    if record_status:
        ghetto.GRecorder.record_active_dict[str_radio] = True

        if not status_listen_btn_dict[table_id]:  # listen not started / index_posts_ajax()
            ghetto.GRecorder.listen_active_dict[str_radio] = False
        dispatch_record_title(table_id, True, False)

    else:
        ghetto.GRecorder.record_active_dict[str_radio] = False
        dispatch_recorder_stop(table_id)


def dispatch_recorder_stop(table_id):

    str_radio = status_read_status_set(
        False, 'posts', 'title', table_id)
    # stop recorder threads
    ghetto.GBase.dict_exit[str_radio] = True
    try:
        del active_displays[table_id]
        sleep(2)
        if status_listen_btn_dict[table_id]:
            dispatch_record_title(table_id, False, True)
    except KeyError:
        pass


def dispatch_record_title(table_id, record, title):

    str_radio = status_read_status_set(
        False, 'posts', 'title', table_id)
    str_url = status_read_status_set(
        False, 'posts', 'content', table_id)

    ghetto.GBase.dict_exit[str_radio] = False
    # test for alive, container docker or snap, and playlist / data_base_auto
    str_checked_url_m3u = ghetto.check_alive_playlist_container(str_radio, str_url)
    if str_checked_url_m3u:
        # replace m3u with real url in database
        conn = get_db_connection()
        print('UPDATE posts SET content = ? WHERE id = ?', (str(str_checked_url_m3u), str(table_id)))
        conn.execute('UPDATE posts SET content = ? WHERE id = ?', (str(str_checked_url_m3u), str(table_id)))
        conn.commit()
        conn.close()
        str_url = str_checked_url_m3u
    # start threads
    try:
        print(ghetto.GBase.dict_error[str_radio])  # show connection error in display
    except KeyError:
        # no error, no key exists

        if title:
            thread = threading.Thread(target=ghetto.GRecorder.get_metadata_from_stream_loop, args=(str_url, str_radio),
                                      daemon=True)
            eisen_threads.append(thread)
            thread.start()
            """ thread_title"""
        elif record:
            thread = threading.Thread(name=table_id, target=ghetto.record, args=(str_radio, str_url), daemon=True)
            eisen_threads.append(thread)
            thread.start()
            """ thread_record"""
        thread = threading.Thread(target=display_write_db, args=(str_radio, table_id), daemon=True)
        eisen_threads.append(thread)
        thread.start()
        return True
    else:
        """show error on display"""
        active_displays[table_id] = ghetto.GBase.dict_error[str_radio]
        ghetto.GBase.dict_exit[str_radio] = True
        return False


def display_write_dict():

    conn = get_db_connection()
    try:
        titles = conn.execute('SELECT id, display FROM posts').fetchall()
        for row in titles:
            table_id = row[0]
            title = row[1]
            if title is not None:
                active_displays[table_id] = title
    except KeyError:
        pass
    conn.close()


def display_write_db(radio, table_id):  # title to db for each radio; other thread can collect or pull it or else
    title = ''
    while not ghetto.GBase.dict_exit[radio]:

        try:
            title = ghetto.GRecorder.current_song_dict[radio]
        except KeyError:
            pass
        display_update_table(title, table_id)
        try:
            display_update_table(title, table_id)
        except Exception as e:
            print(e)
            pass

        for sec in range(5):
            sleep(1)
            if ghetto.GBase.dict_exit[radio]:
                title = 'Null'
                display_update_table(title, table_id)
                break


def display_update_table(title, table_id):

    conn = get_db_connection()
    try:
        conn.execute('UPDATE posts SET display = ? WHERE id = ? ;', (str(title), str(table_id)))   # parameter tuple
    except Exception as e:
        print(f' utf char prob. check lang. support display_update_table(): {e}')
    else:
        conn.commit()
        conn.close()
        display_write_dict()


def display_clean_titles():
    conn = get_db_connection()
    records = conn.execute('select id from posts').fetchall()
    for id_num in records:
        conn.execute('UPDATE posts SET display = ? WHERE id = ?', (None, id_num[0]))
    conn.commit()
    conn.close()


def progress_timer():

    global combo_master_timer   # combo in Tk/Tcl for drop-down dialog on ghetto_recorder package, first front-end
    global progress_master_percent   # separate for future us; go to single timer for each radio

    current_timer = 0
    while 1:

        if combo_master_timer:
            if int(combo_master_timer) <= -1:
                combo_time = 1
            else:
                combo_time = (int(combo_master_timer) * 60 * 60)  # * 60
            percent = progress_bar_percent(current_timer, combo_time)
            if percent:
                progress_master_percent = percent
            else:
                progress_master_percent = 0
                current_timer = 0

            if percent >= 100:
                found = 0
                for _ in ghetto.GBase.dict_exit:
                    found += 1
                if found:
                    for recorder in ghetto.GBase.dict_exit:
                        ghetto.GBase.dict_exit[recorder] = True

        if not combo_master_timer:
            current_timer = 0
            progress_master_percent = 0

        current_timer += 1
        sleep(1)


def progress_bar_percent(current_timer, max_value):
    if not max_value:
        return False
    # doing some math, p = (P * 100) / G, percent = (math.percentage value * 100) / base
    cur_percent = round((current_timer * 100) / max_value, 4)  # 0,0001 for 24h reaction to show
    return cur_percent


def print_request_values(values):
    for val in values:
        print(' -- start print --')
        print(f'\tval in request.form.values(): {val}')
        print(f'\trequest.data {request.data}')
        print(f'\trequest.form {request.form}')
        print(f'\trequest.values {request.values}')
        print(f'\trequest.form.to_dict() {request.form.to_dict()}')
        print(' -- end print --')


def check_write_protected():
    try:
        download_dir = os.path.abspath(get_download_dir())
    except TypeError:
        return
    if download_dir is None:
        flash('Can not write to folder! No folder specified.', 'danger')
        return redirect(url_for('eisenhome_bp.index'))
    if download_dir:
        write_file = download_dir + '/eisen_write_test'
        try:
            with open(write_file, 'wb') as record_file:
                record_file.write(b'\x03')
            os.remove(write_file)
        except OSError:    # master of desaster
            flash('Can not write to folder!.' + download_dir, 'danger')
            return redirect(url_for('eisenhome_bp.index'))
    if not download_dir:
        flash('Can not write to folder! no folder specified' + download_dir, 'danger')
        return redirect(url_for('eisenhome_bp.index'))

