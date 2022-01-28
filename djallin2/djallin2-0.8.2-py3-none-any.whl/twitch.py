#!/usr/bin/env python3

import asyncio
import copy
import json
import logging
import os
import platform
import random
import re
import secrets
import signal
import socket
import ssl
import threading
import traceback
import typing
from pathlib import Path

import dateutil.parser
import pkg_resources
import requests
import toml
import tomlkit
import websockets

from . import OAuth2Receiver, SoundServer, StatTracker

ssl_context = ssl.create_default_context()
sleep_event = threading.Event()

# TODO: this is gonna take ahwile to integrate
shutdown_event = threading.Event()


ready_msg = r'''
 ____  _____    _    ______   __
|  _ \| ____|  / \  |  _ \ \ / /
| |_) |  _|   / _ \ | | | \ V / 
|  _ <| |___ / ___ \| |_| || |  
|_| \_\_____/_/   \_\____/ |_|                                  
'''

crash_msg = r'''
  ____ ____      _    ____  _   _ 
 / ___|  _ \    / \  / ___|| | | |
| |   | |_) |  / _ \ \___ \| |_| |
| |___|  _ <  / ___ \ ___) |  _  |
 \____|_| \_\/_/   \_\____/|_| |_|
'''

dead_msg = r'''
 ____  _____    _    ____         __
|  _ \| ____|  / \  |  _ \   _   / /
| | | |  _|   / _ \ | | | | (_) | | 
| |_| | |___ / ___ \| |_| |  _  | | 
|____/|_____/_/   \_\____/  (_) | | 
                                 \_\
'''


def validate_token(oauth_token):
    """
    Check token status with twitch
    Raises on connection error or unexpected status code from twitch
    :param oauth_token: user token
    :return: validation response if valid or None
    """
    logging.info('Phoning Papa Bezos...')
    try:
        resp = requests.get('https://id.twitch.tv/oauth2/validate',
                            headers={'Authorization': 'OAuth ' + oauth_token})
    except Exception as err:
        err_msg = f'Error contacting Twitch, internet issues? {err}'
        logging.critical(err_msg)
        raise RuntimeError(err_msg) from err

    if resp.status_code == 200:
        resp = resp.json()
        need = {'channel:read:redemptions', 'chat:read'}
        has = set(resp['scopes'])
        missing = need - has
        if missing:
            logging.warning(f'Token is missing required scopes: {missing}. Throwing it out.')
            return None
        elif resp['expires_in'] < 60*24*2:
            logging.warning('Token is expiring soon, requesting a new one')
            return None
        return resp
    elif resp.status_code == 401:
        return None
    else:
        err_msg = f'Unrecognized status code during token check: {resp.status_code}, unsure how to proceed.'
        logging.critical(err_msg)
        raise RuntimeError(err_msg)


def build_and_validate_listener_conf(config):
    """
    Check configuration shape and prep listener data
    :param config: config file data
    :return: listener configuration
    """
    # First, find all the chat and point listeners. then unkink all the links
    listener_conf = {
        'chat': {k: v for k, v in config.get('chat', {}).items() if 'link' not in v},
        'points': {k: v for k, v in config.get('points', {}).items() if 'link' not in v}
    }

    section = None
    name = None
    try:
        for section in listener_conf.keys():
            for name, conf in {k: v for k, v in config.get(section, {}).items() if 'link' in v}.items():
                source = conf['link'].split('.')
                # keys set in the linker override the linkee but I'm not gonna announce that
                instance = listener_conf[source[0]][source[1]] | conf
                instance.pop('link', None)
                instance.pop('link', None)
                if section == 'points':
                    instance.pop('who', None)
                    instance.pop('command', None)
                listener_conf[section][name] = instance
    except Exception as err:
        logging.critical(f'Error reconstructing link for {section}.{name}: {err}')
        raise

    # Ok, cool. Do some rough type validation
    # UGH you can't make a union of one type and you can't run isinstace with None
    # and it's not clear how to make NoneType
    key_types = {
        'points': {
            'target': (str,),
            'random': (int,),
            'priority': (bool,),
            'stats': (bool,),
            'name': (str,),
            'nonblock': (bool,),
            'custom': (str,),
        },
        'chat': {
            'names': (list, type(None)),
            'badges': (list, type(None)),
            'target': (str,),
            'command': (str,),
            'command_mode': (str,),
            'random': (int, type(None)),
            'priority': (bool,),
            'stats': (bool,),
            'nonblock': (bool,),
            'custom': (str,),
        }
    }
    try:
        for section in listener_conf.keys():
            for name, conf in listener_conf[section].items():
                for k, t in key_types[section].items():
                    if k in conf:
                        if not isinstance(conf[k], t):
                            msg = f'Expected {k} in {section}.{name} to be {t} but got {type(conf[k])}'
                            logging.critical(msg)
                            raise RuntimeError(msg)
                # Types look good, do any formatting
                # just sandblast our config blob
                user_config = copy.deepcopy(conf)
                conf.clear()

                conf['entry_name'] = name

                if section == 'points':
                    conf['name'] = user_config['name'].strip().lower()

                if 'custom' in user_config and user_config.keys() - {'custom', 'name'}:
                    msg = f'Error in {section}.{name}, custom does not support additional settings'
                    logging.critical(msg)
                    raise RuntimeError(msg)
                elif 'custom' in user_config:
                    # that's all you get!
                    # ... and your points name
                    # Good news, read_text does newline conversion, it seems.
                    conf['custom'] = user_config['custom']
                    continue
                else:
                    conf['custom'] = None

                conf['target'] = Path(user_config['target'])
                # I guess we should raise if it's missing
                if not conf['target'].exists():
                    msg = f'Error in {section}.{name}, target {conf["target"]} does not exist'
                    logging.critical(msg)
                    raise RuntimeError(msg)

                conf['target_is_file'] = conf['target'].is_file()

                if conf['target_is_file']:
                    conf['target_file_list'] = []
                else:
                    conf['target_file_list'] = [_ for _ in conf['target'].glob('*.mp3')]

                conf['stats'] = user_config.get('stats', False)
                conf['nonblock'] = user_config.get('nonblock', False)

                conf['random_mode'] = user_config.get('random', 0)
                if conf['random_mode'] not in {0, 1, 2}:
                    conf['random'] = 0

                conf['priority'] = user_config.get('priority', False)

                if section == 'chat':
                    conf['name_set'] = set(user_config.get('names', []))
                    conf['badge_set'] = set(user_config.get('badges', []))
                    conf['command_mode'] = user_config.get('command_mode', 'start')
                    if conf['command_mode'] not in {'start', 'contains', 'regex', 'regex_find'}:
                        msg = f'Unrecognized command mode {conf["command_mode"]}'
                        logging.critical(msg)
                        raise RuntimeError(msg)
                    elif conf['command_mode'] == 'contains' and \
                            (conf['random_mode'] != 2 and not conf['target_is_file']):
                        msg = f'"contains" mode cannot be used unless "random" is 2 or "target" is a single file'
                        logging.critical(msg)
                        raise RuntimeError(msg)
                    elif conf['command_mode'] in {'regex', 'regex_find'}:
                        conf['command'] = re.compile(user_config['command'])
                    else:
                        conf['command'] = user_config['command']

    except Exception as err:
        logging.critical(f'Error validating config for {section}.{name}: {err}')
        raise

    return listener_conf


def build_listeners(listener_conf, sound_server, stat_server):
    chat_functions = []
    points_functions = {}
    try:
        for section in [k for k, v in listener_conf.items() if v]:
            for name, conf in sorted(listener_conf[section].items()):
                conf['sound_server'] = sound_server
                conf['stat_server'] = stat_server
                if section == 'chat':
                    chat_functions.append(chat_listener_factory(conf))
                elif section == 'points':
                    points_functions[conf['name']] = points_listener_factory(conf)
                else:
                    raise RuntimeError(f'Error building listeners, no known section {section}')
    except Exception as err:
        logging.critical(f'Error building listener for {section}.{name}: {err}')
        raise

    return chat_functions, points_functions


# message_filter = re.compile(r"""["'/\\<>:|?*\s]""")
message_filter = re.compile(r'\W')


def do_message_filter(message):
    return message_filter.sub('', message) if message else ''


# FIXME: do sanitization here?
def do_sound_req(*, nonblock: bool, entry_name: str, message: str, priority: bool, random_mode: int,
                 sound_server: SoundServer.SoundServer, stat_server: StatTracker.StatTracker,
                 stats: bool, sub_index: int = 0, target: Path, target_file_list: list, target_is_file: bool,
                 timestamp: int, user: str, **kwargs):
    request = None
    # We could switch to if len(list) == 1 but that would technically clobber a directory with one file
    if target_is_file:
        request = SoundServer.SoundRequest(50 if priority else 100, timestamp, sub_index,
                                           target, not nonblock)
    elif random_mode == 2 or (random_mode == 1 and message == 'random'):
        request = SoundServer.SoundRequest(50 if priority else 100, timestamp, sub_index,
                                           random.choice(target_file_list), not nonblock)
    else:
        fname = message + '.mp3'
        selected_file = target / fname
        if selected_file.exists():
            request = SoundServer.SoundRequest(50 if priority else 100, timestamp, sub_index,
                                               selected_file, not nonblock)
        else:
            logging.error(f'{fname} does not exist')
    if request is not None:
        sound_server.enqueue(request)
        if stats:
            stat_server.submit('chat', user, entry_name, timestamp, message)
        return True
    return False


def chat_listener_factory(config: dict) -> typing.Callable[..., bool]:
    """
    Build chat listener
    :param config:
        entry_name: str,
        sound_server: SoundServer.SoundServer,
        stat_track: bool,
        stat_server: StatTracker.StatTracker,
        badge_set: set,
        name_set: set,
        target: Path,
        target_is_file: bool,
        target_file_list: list,
        command: str,
        command_mode: str
        custom: str
        random_mode: int,
        priority: bool,
        nonblock: bool
    :return: chat listener function
    """
    if config['custom']:
        # WOW galaxy brain problem.
        # You need to expose a scope object or the function disappears (but not in the debugger!!)
        # Short version, writes to the default locals() get tossed by the interpreter
        # AND you need to expose the config as a global because FOR SOME REASON
        # the local variables won't be available to functions in the exec block at call time??
        # https://stackoverflow.com/a/24734880
        locals = {}
        exec(config['custom'],
             {'config': config, 'SoundRequest': SoundServer.SoundRequest, 'do_message_filter': do_message_filter},
             locals)
        return locals['listener']
    else:
        def listener(*, badges: dict, tags: dict, timestamp: int, user: str, user_display: str, message: str, **kwargs) -> bool:
            """
            Checks various filters against the request and queues a sound.
            :param badges: User badge map. badge (str): version (str)
            :param tags: Twitch message tags. tag (str): value (str)
            :param timestamp: Message timestamp (ms)
            :param user: Username of the message sender, lowercase
            :param user_display: User's display name
            :param message: Chat message - !!NOT SANITIZED!!
            :return: bool indicating if it fired. Stops processing listeners if True
            """
            if config['command_mode'] == 'start' and message.startswith(config['command']):
                if (not config['badge_set'] and not config['name_set']) \
                        or badges.keys() & config['badge_set'] \
                        or user in config['name_set']:
                    message = message_filter.sub('', message[len(config['command']):])
                    return do_sound_req(**config, user=user, message=message, timestamp=timestamp)
            elif config['command_mode'] == 'contains' and config['command'] in message:
                if (not config['badge_set'] and not config['name_set']) \
                        or badges.keys() & config['badge_set'] \
                        or user in config['name_set']:
                    # ehh let's just mess up the message string
                    return do_sound_req(**config, user=user, message='__contains_mode_no_message', timestamp=timestamp)
            elif config['command_mode'] == 'regex' and (match := config['command'].match(message)) is not None:
                if (not config['badge_set'] and not config['name_set']) \
                        or badges.keys() & config['badge_set'] \
                        or user in config['name_set']:
                    if not match.groups():
                        do_sound_req(**config, user=user, message='__regex_no_capture', timestamp=timestamp)
                    else:
                        for sub_idx, san_match in enumerate((message_filter.sub('', _) for _ in match.groups() if _)):
                            do_sound_req(**config, user=user, message=san_match, timestamp=timestamp, sub_index=sub_idx)
                    # Making a decision here, you matched the regex, you count as fired.
                    return True
            # Switch to regex for repeating captures? Can't seem to get the syntax right though for use with match()
            elif config['command_mode'] == 'regex_find' and (match := config['command'].findall(message)) is not None:
                if (not config['badge_set'] and not config['name_set']) \
                        or badges.keys() & config['badge_set'] \
                        or user in config['name_set']:
                    for sub_idx, san_match in enumerate(filter(None, (message_filter.sub('', _) for _ in match))):
                        do_sound_req(**config, user=user, message=san_match, timestamp=timestamp, sub_index=sub_idx)
                    # Making a decision here, you matched the regex, you count as fired.
                    return True

        return listener


def points_listener_factory(config: dict) -> typing.Callable[..., None]:
    """
    Build points responder
    :param config:
        entry_name: str,
        sound_server: SoundServer.SoundServer,
        stat_track: bool,
        stat_server: StatTracker.StatTracker,
        target: Path,
        target_is_file: bool,
        target_file_list: list,
        random_mode: int,
        priority: bool,
        nonblock: bool
        custom: str
    :return: Points responder
    """
    if config['custom']:
        locals = {}
        exec(config['custom'],
             {'config': config, 'SoundRequest': SoundServer.SoundRequest, 'do_message_filter': do_message_filter},
             locals)
        return locals['listener']
    else:
        def listener(user: str, user_display: str, timestamp: int, reward: dict, message: typing.Optional[str], **kwargs) -> None:
            """
            Reads a points redemption and does whatever it needs to do
            :param user: Username of the sender, lowercase
            :param user_display: User's display name
            :param timestamp: Message timestamp (ms)
            :param message: Reward input or None - !!NOT SANITIZED!!
            :param reward: Redemption data from twitch - https://dev.twitch.tv/docs/pubsub#example-channel-points-event-message
            :return: None
            """
            message = message_filter.sub('', message) if message else ''
            do_sound_req(**config, user=user, message=message, timestamp=timestamp)
        return listener


def do_token_work(config_file: Path):
    """
    Check token stuff, potentially update config file
    :param config_file: Path to conf
    :return: token, server validation data
    """
    config = tomlkit.loads(config_file.read_text())

    ready = False
    if config.get('token'):
        # check if it's good
        validation_response = validate_token(config['token'])
        if validation_response is not None:
            ready = True
        else:
            # BE GONE FROM ME SHITTY TOKEN
            config['token'] = ''
            logging.info('Deleting old token')
            config_file.write_text(tomlkit.dumps(config))

    if not ready:
        oauth_url = 'https://id.twitch.tv/oauth2/authorize'
        # set force_verify to make twitch prompt for authorization every time
        oauth_params = {'response_type': 'token',
                        'client_id': 'r50bzaj62mdvoo3nojyfuqeewxlj23',
                        'redirect_uri': 'http://localhost:42069',
                        'scope': 'channel:read:redemptions chat:read'}

        def url_callback(url):
            logging.error(f'Opening browser, if nothing happens, go to {url}')
            logging.warning('Waiting for token response. '
                            'If the application does not respond, check the documentation for manual authorization.')

        try:
            oauth_response = OAuth2Receiver.get_oauth_code(('localhost', 42069), oauth_url, oauth_params,
                                                           True, url_callback, 300)
        except TimeoutError as err:
            msg = 'Browser response not received, manual authorization required.'
            logging.critical(msg)
            raise RuntimeError(msg) from err
        except Exception as err:
            msg = 'OAuth listener failed, manual authorization required.'
            logging.critical(msg)
            raise RuntimeError(msg) from err

        config['token'] = oauth_response['access_token']
        validation_response = validate_token(config['token'])
        if validation_response is None:
            msg = "New token is bad???"
            logging.critical(msg)
            raise RuntimeError(msg)
        logging.info('Saving new token')
        config_file.write_text(tomlkit.dumps(config))

    return config['token'], validation_response


def chat_listener(config, server_validation, chat_functions):
    retry_count = 0
    while True:
        message_buffer = []
        leftovers = b''
        partial_read = False
        try:
            # port to websocket?
            #  I don't like that the websocket library has an FAQ section for "why is it slow"
            # Need to see what a network disconnect looks like
            #  MacOS, baby. this just keeps working if you turn the network off and on
            with socket.create_connection(('irc.chat.twitch.tv', 6697)) as sock:
                sock.setblocking(True)  # The docs DON'T say it DOESN'T work on windows
                with ssl_context.wrap_socket(sock, server_hostname='irc.chat.twitch.tv') as ssock:
                    ssock.send('PASS oauth:{}\r\nNICK {}\r\n'.format(config['token'],
                                                                     server_validation['login']).encode('utf-8'))
                    # ":tmi.twitch.tv NOTICE * :Login authentication failed" on bad oauth. idk about expired
                    # We should expect a "GLHF!" otherwise in the first response
                    sleep_event.wait(0.2)
                    login_status = ssock.recv(512)
                    if b'GLHF!' not in login_status:
                        err_str = f'Failed to login to chat: {login_status}'
                        logging.critical(err_str)
                        raise RuntimeError(err_str)

                    ssock.send('CAP REQ :twitch.tv/tags\r\n'.encode('utf-8'))
                    sleep_event.wait(0.2)
                    cap_add_status = ssock.recv(512).decode('utf-8').strip()
                    if cap_add_status != ':tmi.twitch.tv CAP * ACK :twitch.tv/tags':
                        err_str = f'Failed to activate tag cap: {cap_add_status}'
                        logging.critical(err_str)
                        raise RuntimeError(err_str)

                    ssock.send('JOIN #{}\r\n'.format(server_validation['login']).encode('utf-8'))
                    sleep_event.wait(0.2)
                    join_status = ssock.recv(512)
                    if b'.tmi.twitch.tv JOIN #' not in join_status:
                        err_str = f'Failed to join chat: {join_status}'
                        logging.critical(err_str)
                        raise RuntimeError(err_str)
                    # Sometimes it's just late but there's not much I can do about it, I don't want to accidentally
                    #  suck up some partial message :/
                    if b'End of /NAMES list' not in join_status:
                        join_status = ssock.recv(512)
                        if b'End of /NAMES list' not in join_status:
                            err_str = f'Failed to get name listing?: {join_status}'
                            logging.critical(err_str)
                            raise RuntimeError(err_str)
                    logging.info('Connected to chat!')
                    while True:
                        # Ok, here's the problem.
                        #  The buffer could be backed up enough that we receive a partial message.
                        # The original version did a regex split on \r\n and always popped off the last entry
                        # And combined it with the next received buffer
                        # I question how well that worked, but it was also a nonblocking recv
                        # So that's probably why it pegs a core.
                        # Yikes, we might cut a multibyte character in half with a partial read. Is that a raise?
                        # Let's not decode until after we've processed linebreaks
                        msg = ssock.recv(4096)
                        logging.debug(msg)
                        if not len(msg):
                            # you literally can't send zero bytes. We got hung up on.
                            # Strange that is is, seemingly, the only way to find out besides a fileno of -1
                            raise ConnectionError('Connection closed')
                        if partial_read:
                            msg = leftovers + msg
                        # max twitch message len is 512 MAYBE
                        # It's IRC in that it's mostly IRC-shaped
                        # Tags bump that significantly
                        partial_read = not msg.endswith(b'\r\n')
                        message_buffer = msg.split(b'\r\n')
                        # NOTE: we seem to be getting b'' off the end of the split because lol wtf?????
                        if partial_read:
                            leftovers = message_buffer.pop()
                        for msg in message_buffer:
                            msg = msg.decode('utf-8')
                            # We, in theory, shouldn't be able to get an empty message anymore.
                            # You PROBABLY can't send \r\n in twitch chat lol
                            if msg:
                                # safe parsing seems tricky.
                                # PRIVMSG's tmi string is much more complicated than the regular tmi string
                                # splitting on space up to 5 blocks seems safe. we should only be receiving PRIVMSG and PING
                                # @tags tmi_string privmsg #channel :msg
                                # PING tmi_string
                                components = msg.split(' ', maxsplit=4)
                                if components[0] == 'PING':
                                    logging.info('Responding to chat ping')
                                    ssock.send('PONG\r\n'.encode('utf-8'))
                                    # congrats, we made it 5 minutes without dying!
                                    retry_count = 0
                                elif len(components) == 5 and components[2] == 'PRIVMSG':
                                    tags = {k: v for k, v in [x.split('=') for x in components[0][1:].split(';')]}
                                    badges = {} if not tags.get('badges') else \
                                        {k: v for k, v in [x.split('/') for x in tags['badges'].split(',')]}
                                    timestamp = int(tags['tmi-sent-ts'])
                                    sender = components[1][1:].split('!', maxsplit=1)[0].lower()
                                    # display-name can be empty
                                    sender_display = sender if not tags.get('display-name') else tags['display-name']
                                    message = components[4][1:]
                                    logging.info(f'{sender}: {message}')
                                    # badges: dict, tags: dict, timestamp: int, sender: str, sender_display: str, message: str, **kwargs
                                    for func in chat_functions:
                                        try:
                                            if func(badges=badges,
                                                    tags=tags,
                                                    timestamp=timestamp,
                                                    user=sender,
                                                    user_display=sender_display,
                                                    message=message):
                                                break
                                        except Exception as err:
                                            # FIXME? this isn't a reconnect-level issue, but it's still a problem.
                                            logging.error(f'Error in message scanner loop: {err}')
                                            logging.error(traceback.format_exc())
                                else:
                                    logging.error(f'Mystery message from twitch, probably fine: {msg}')
        except Exception as err:
            logging.error(crash_msg)
            logging.error(f'Got {err}')
            logging.error(traceback.format_exc())
            logging.error(f'Lost {len(message_buffer) + partial_read} messages :(')
            retry_count += 1
            if retry_count >= 3:
                logging.critical('Too many chat failures!%s', dead_msg)
                # FIXME: jank way to trigger shutdown on failure
                #  unless we want to raise System Exit
                shutdown_event.set()
                raise RuntimeError('Too many chat failures') from err
        sleep_event.wait(2**retry_count)


async def points_ws_send_ping_in(time, wsock):
    await asyncio.sleep(time)
    if wsock.open:
        await wsock.send('{"type":"PING"}')


async def points_ws_reward_handler(message):
    pass


async def points_ws_listener(config, server_validation, points_functions):
    retry_count = 0
    loop = asyncio.get_running_loop()
    while True:
        try:
            async with websockets.connect('wss://pubsub-edge.twitch.tv', max_size=4096, ssl=ssl_context) as ws:
                nonce = secrets.token_urlsafe(16)
                await ws.send(json.dumps(
                    {'type': 'LISTEN',
                     'nonce': nonce,
                     'data': {
                         'topics': [f'channel-points-channel-v1.{server_validation["user_id"]}'],
                         'auth_token': config['token']
                     }}))
                response = json.loads(await ws.recv())
                if response['type'] == "RESPONSE":
                    if response['error']:
                        raise RuntimeError(f'LISTEN failed, twitch says: {response["error"]}')
                    if response.get('nonce') != nonce:
                        raise RuntimeError(f'LISTEN NONCE BAD: {response.get("nonce")} CONNECTION INTERFERENCE!?')
                # Well I guess that's it.
                # !WE! have to ping !TWITCH! which is weird
                # AND they're not websocket pings, so I can't use the helpers >:C
                loop.create_task(points_ws_send_ping_in(260 + random.randrange(-20, 20), ws))
                #loop.create_task(points_ws_send_ping_in(5, ws))
                # I could do something fancy if there was a dispatch here and every redemption went to a new task
                # FIXME: we never check for PONG arrival within 10 seconds??
                logging.info('Connected to PubSub')
                async for msg in ws:
                    # If we got sent bad json, idk what to tell you.
                    # I mean, a nicer error message would be cool but ehhhh
                    logging.debug(msg)
                    msg = json.loads(msg)
                    # We only asked for chat points, so we don't filter by topic
                    # twitch nests the actual message because topics!
                    if msg.get('type') == 'MESSAGE':
                        # nested json strings!
                        msg['data']['message'] = json.loads(msg['data']['message'])
                        if msg['data']['message']['type'] == 'reward-redeemed':
                            msg = msg['data']['message']
                            try:
                                redemption = msg['data']['redemption']
                                username = redemption['user']['login']
                                display_name = redemption['user'].get('display_name', username)
                                timestamp = int(dateutil.parser.parse(msg['data']['timestamp']).timestamp() * 1000)
                                what = redemption['reward']['title'].strip().lower()
                                logging.info(f'{display_name} redeemed "{what}"')
                                if what in points_functions:
                                    points_functions[what](user=username,
                                                           user_display=display_name,
                                                           timestamp=timestamp,
                                                           reward=redemption,
                                                           message=redemption.get('user_input'))
                                else:
                                    logging.error('But there is no function for it')
                            except Exception as err:
                                logging.error(f'Error in points redemption: {err}')
                                logging.error(traceback.format_exc())
                    elif msg.get('type') == 'PONG':
                        # Cool, got a ping response.
                        logging.info('Got PubSub PONG')
                        retry_count = 0
                        loop.create_task(points_ws_send_ping_in(260 + random.randrange(-20, 20), ws))
                    elif msg.get('type') == 'RECONNECT':
                        # Idk if there were messages in the queue or what will happen
                        logging.info('Twitch asked us to hangup')
                        retry_count += 1
                        await ws.close()
                    else:
                        logging.error(f'Unrecognized PubSub from twitch: {msg}')
        except Exception as err:
            logging.error(crash_msg)
            logging.error(f'Got {err}')
            logging.error(traceback.format_exc())
            retry_count += 1
            if retry_count >= 3:
                # FIXME: jank way to trigger shutdown on failure
                #  unless we want to raise System Exit
                shutdown_event.set()
                raise RuntimeError('Too many points failures') from err
        await asyncio.sleep(2**retry_count)


async def chat_ws_listener(login_username, oauth_token, chat_functions):
    retry_count = 0
    while retry_count <= 3:
        try:
            async with websockets.connect('wss://irc-ws.chat.twitch.tv:443', max_size=4096, ssl=ssl_context) as ws:
                # Well, either we DON'T need \r\n, or twitch is nice enough to forgive us
                await ws.send(f'PASS oauth:{oauth_token}\r\n')
                await ws.send(f'NICK {login_username}\r\n')
                response = await ws.recv()
                if 'GLHF!' not in response:
                    raise RuntimeError(f'Bad login response from twitch: {response}')
                await ws.send('CAP REQ :twitch.tv/tags\r\n')
                response = await ws.recv()
                if response != ':tmi.twitch.tv CAP * ACK :twitch.tv/tags\r\n':
                    raise RuntimeError(f'Unexpected cap add response from twitch: {response}')
                await ws.send(f'JOIN #{login_username}\r\n')
                response = await ws.recv()
                # ok, cool. the whole "stream message boundary disambiguity" issue is not at all fixed by websockets
                if '.tmi.twitch.tv JOIN #' in response:
                    if ':End of /NAMES list' not in response:
                        response = await ws.recv()
                        if ':End of /NAMES list' not in response:
                            raise RuntimeError(f'Join trailer not received from twitch: {response}')
                else:
                    raise RuntimeError(f'Unexpected join response from twitch: {response}')

                async for msg in ws:
                    components = msg.split(' ', maxsplit=4)
                    if components[0] == 'PING':
                        # congrats, we made it 5 minutes without dying!
                        retry_count = 0
                        logging.info('Responding to chat ping')
                        await ws.send('PONG')
                    elif len(components) == 5 and components[2] == 'PRIVMSG':
                        try:
                            tags = {k: v for k, v in [x.split('=') for x in components[0][1:].split(';')]}
                            badges = {} if not tags.get('badges') else \
                                {k: v for k, v in [x.split('/') for x in tags['badges'].split(',')]}
                            timestamp = int(tags['tmi-sent-ts'])
                            sender = components[1][1:].split('!', maxsplit=1)[0].lower()
                            # display-name can be empty
                            sender_display = sender if not tags.get('display-name') else tags['display-name']
                            message = components[4][1:-2]
                            logging.info(f'{sender}: {message}')
                        except Exception as err:
                            logging.error(f'Error parsing twitch message for listeners: {err}')
                            logging.error(traceback.format_exc())
                        # badges: dict, tags: dict, timestamp: int, sender: str, sender_display: str, message: str, **kwargs
                        for func in chat_functions:
                            try:
                                if func(badges, tags, timestamp, sender, sender_display, message):
                                    break
                            except Exception as err:
                                # FIXME? this isn't a reconnect-level issue, but it's still a problem.
                                logging.error(f'Error in message scanner loop: {err}')
                                logging.error(traceback.format_exc())
                    else:
                        logging.error(f'Mystery message from twitch, probably fine: {msg}')

        except Exception as err:
            logging.error(crash_msg)
            logging.error(f'Got {err}')
            logging.error(traceback.format_exc())
            retry_count += 1
            if retry_count >= 3:
                # FIXME: jank way to trigger shutdown on failure
                #  unless we want to raise System Exit
                shutdown_event.set()
                logging.critical('Too many chat failures!%s', dead_msg)
                raise
        await asyncio.sleep(2**retry_count)


def launch_system(config_file: Path, quiet: bool = False, debug: bool = False):
    """
    Do all the things
    :param config_file: Path to config file
    :param quiet: silence startup boop
    :param debug: debug flag
    """
    try:
        config = toml.loads(config_file.read_text())
    except Exception as err:
        logging.critical('Error loading configuration file: %s', err)
        raise

    # ugh we said paths would be relative to the conf file
    # We might as well chdir, this means we aren't logging/saving abspaths everywhere
    os.chdir(config_file.absolute().parent)

    logging.debug('Checking config')
    listener_conf = build_and_validate_listener_conf(copy.deepcopy(config))

    logging.debug(listener_conf)

    logging.debug('Doing token stuff')
    config['token'], server_validation = do_token_work(config_file)

    logging.debug('Attaching signal handlers')

    def handler(signum, frame):
        logging.critical(f'SIG{signum}: shutting down')
        shutdown_event.set()

    # On Windows, signal() can only be called with SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, SIGTERM, or SIGBREAK.
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    # Rumor has it SIGBREAK will happen on window close
    # OR NOT >:C I can't find a way to do it without win32 apis. Rude.

    logging.debug('Starting sound server')
    soundserver = SoundServer.SoundServer(shutdown_event)

    if not quiet:
        soundserver.enqueue(SoundServer.SoundRequest(
            0, 0, 0, Path(pkg_resources.resource_filename(__package__, 'internal/up.mp3')), False))

    logging.debug('Booting stats server')
    # uhhhhhhh base the name on the config... somehow? Generate one and write back?
    enable_stats = any('stats' in conf for section in listener_conf.values() for conf in section.values())
    if enable_stats:
        statserver = StatTracker.StatTracker(Path(config.get('stats_db', 'stats.sqlite')), shutdown_event)
    else:
        statserver = StatTracker.StubTracker()

    logging.debug('Attaching MORE signal handlers')
    if platform.system() == 'Windows':
        import win32api

        def win_handler(sig):
            logging.critical('Closing')
            shutdown_event.set()
            statserver.wait()
        win32api.SetConsoleCtrlHandler(win_handler, True)
    else:
        signal.signal(signal.SIGHUP, handler)

    chat_functions, points_functions = build_listeners(listener_conf, soundserver, statserver)

    chat_thread = None
    points_thread = None

    if chat_functions:
        # daemonize because I can't think of a nice way to integrate shutdown yet
        chat_thread = threading.Thread(target=chat_listener, args=(config, server_validation, chat_functions),
                                       name='chat', daemon=True)
        chat_thread.start()

    if points_functions:
        # I'm feeling the async creep. It'd be nice to convert the chat, sound, and stat systems to async
        # We're under the GIL so if anything we'd benefit from context switch reduction.
        # But that means user defined funcs will need to be async, and if they screw it up, it'll jam *everything*
        # Maybe we should scrap user funcs?
        # Could use different event loop threads, but then what was the point.
        #  Sound and stats could share a loop! But how do you properly flush stats on shutdown?
        # I should focus on getting point rewards working first.
        points_thread = threading.Thread(target=asyncio.run,
                                         args=(points_ws_listener(config, server_validation, points_functions),),
                                         kwargs={'debug': debug},
                                         name='points', daemon=True)
        points_thread.start()

    if not chat_functions and not points_functions:
        logging.critical('Nothing configured??')
        shutdown_event.set()
        if platform.system() == 'Windows':
            # Windows will close if we don't raise >:C
            raise RuntimeError('No chat or point listeners configured!')

    # TODO: Figure out shutdowns in the various bad spots
    #  (soundserver needing a fake(?) sound, chat listener, (eventually) points listnener)
    # LMFAO FREAKING WINDOWS threading.Event.wait can't be interrupted https://bugs.python.org/issue35935
    # But since they've been pouring effort into time.sleep to make it not garbage, that might work.
    if platform.system() == 'Windows':
        import time
        while not shutdown_event.is_set():
            time.sleep(5)
    else:
        shutdown_event.wait()

    if not quiet:
        soundserver.enqueue(SoundServer.SoundRequest(
            -1, -1, -1, Path(pkg_resources.resource_filename(__package__, 'internal/down.mp3')), False))

    # So here's the deal. If we raise and we're in windows, the terminal window's probably gonna close immediately
    # so we probably need to wrap this all in a try and if platforms == 'Windows' time.sleep(10) or something
