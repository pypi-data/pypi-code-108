import asyncio
from asyncio import StreamReader, StreamWriter
from concurrent.futures import ProcessPoolExecutor
from jcore.exceptions import JarvisException
#import socket
import traceback
import uuid
import logging


from datetime import datetime
from jcore.helpers import Settings
from .messageparser import parse_line

executor = ProcessPoolExecutor(2)


INTERVAL = 0.001
JOIN_LIMIT = 10

class Socket():
    """A wrapper for the low-level core library socket interface, 
    and customised to facilitate communication with the Twitch IRC API."""
    __message_counter:dict
    last_check:datetime
    primary_socket: bool
    log:logging
    reader: StreamReader
    writer: StreamWriter

    def __init__(self, client, command_activator: str, primary_socket:bool = False):
        self.__name = uuid.uuid4().hex[:8]
        self.log = logging.getLogger(f"{__name__} [{self.__name}]")
        self.client = client
        self.command_activator = command_activator
        self.active = True
        self.__channels = {}

        self.buffer = ""
        # self.socket = None
        config = Settings().get_all_settings()
        self.nick = config["nick"]
        self.token = config["token"]
        self.loop = asyncio.get_event_loop()
        self.__message_counter = {}
        self.last_check = datetime.now()
        self.primary_socket = primary_socket

    def set_channels(self, channels: list):
        for channel in channels:
            self.__channels[channel] = {"active": False, "message_counter": 0, "activation_failures": 0, "banned": False}
        

    def reset_message_counter(self):
        for channel in self.__channels:
            self.__channels[channel]["message_counter"] = 0
        self.last_check = datetime.now()
    
    @property
    def name(self) -> str:
        return self.__name

    @property
    def channel_list(self) -> list:
        outlist= []
        for key in self.__channels:
            outlist.append(key)
        return outlist
        

    @property
    def message_counter(self) -> dict:
        outdict = {}
        for key, values in self.__channels.items():
            outdict[key] = values["message_counter"]
        return outdict
    
    @property
    def total_messages(self) -> int:
        m = 0
        for k,v in self.__channels.items():
            m += v["message_counter"]
        return m
    
    @property
    def average_messages(self) -> float:
        return float(self.total_messages) / float(self.current_connections)

    @property
    def current_connections(self) -> int:
        return len(self.__channels)
    
    @property
    def inactive_connections(self) -> list:
        outlist = []
        for channel, values in self.__channels.items():
            if not values["active"]:
                outlist.append(channel)
        return outlist

    @property
    def banned_channels(self) -> list:
        outlist = []
        for channel, values in self.__channels.items():
            if values["banned"]:
                outlist.append(channel)
        return outlist

    @property
    def has_inactive_connections(self) -> bool:
        return len(self.inactive_connections) > 0


    async def connect(self):
        self.active = True
        if len(self.__channels) == 0: 
            raise Exception("Channels list hasn't been set.")
        self.log.info(f"Initialising connection to: {self.channel_list}")
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reader,self.writer = await asyncio.open_connection(host="irc.chat.twitch.tv", port=6667)
        
        # await self.loop.run_in_executor(executor, self.socket.connect, ("irc.chat.twitch.tv", 6667))
        await self._send_raw(f"PASS {self.token}")
        await self._send_raw(f"NICK {self.nick}")
        await self._send_raw("CAP REQ :twitch.tv/membership")
        await self._send_raw("CAP REQ :twitch.tv/tags")
        await self._send_raw("CAP REQ :twitch.tv/commands")

        counter = 1

        for channel in self.__channels:
            if counter % JOIN_LIMIT == 0:
                self.log.debug("Pausing join requests, standby...")
                await asyncio.sleep(5)
            counter += 1
            await self._join(channel)
            self.__message_counter[channel] = 0
        self.last_ping = datetime.now()
        self.log.info(f"Socket engaged.")


    async def disconnect(self):
        try:
            self.log.info(f"departing channels")
            self.active = False
            try:
                tasks = []
                for channel in self.__channels:
                    if self.writer:
                        tasks.append(self._part(channel))
                asyncio.gather(*tasks, loop=self.loop)
            except Exception as e:
                self.log.critical(f"Suppressing a caught an exception in `Socket.disconnect()` [Parting channel]. Details below\n{type(e)}: {traceback.format_exc()}")
            try:
                self.writer.close()
                # self.socket.close()
            except Exception as e:
                self.log.critical(f"Suppressing a caught an exception in `Socket.disconnect()` [closing socket]. Details below\n{type(e)}: {traceback.format_exc()}")
        except Exception:
            self.log.critical(f"Failed to correctly disconnect from channel")
        

    async def reconnect(self):
        self.log.info(f"Reconnect detected!")
        await self.disconnect()
        self.log.info(f"Waiting 10s to reconnect.")
        await asyncio.sleep(10)
        self.log.info(f"Reconnecting, standby...")
        await self.connect()


    async def _join(self, channel):
        await self._send_raw(f"JOIN #{channel} ")

    async def _part(self, channel):
        await self._send_raw(f"PART #{channel} ")

    async def join_channel(self, channel):
        self.log.info(f"Sending request to join channel `{channel}`")
        try:
            self.__channels[channel] = {"active": False, "message_counter": 0, "activation_failures": 3, "banned": False}
            await self._join(channel)
            await asyncio.sleep(2)
        except JarvisException as ex:
            self.log.error(f"An error occurred when attemting to leave the channel `{channel}`\nDetails below\n{type(ex)}: {traceback.format_exc()}")
            return
        if self.__channels[channel]["active"]:
            self.log.info(f"Successfully joined channel `{channel}`")
        else:
            self.log.warning(f"There was an issue adding the channel `{channel}`, check the logs for any further details.")

    
    async def depart_channel(self, channel):
        self.log.info(f"Sending request to leave channel `{channel}`")
        try:
            self.__channels.pop(channel)
            await self._part(channel)
        except JarvisException as ex:
            self.log.error(f"An error occurred when attemting to leave the channel `{channel}`\nDetails below\n{type(ex)}: {traceback.format_exc()}")
            return
        if channel not in self.__channels:
            self.log.info(f"Successfully departed channel `{channel}`")
        else:
            self.log.warning(f"There was an issue removing the channel `{channel}`, check the logs for any further details.")


    def has_channel(self, channel) -> bool:
        return channel in self.__channels 

    
    async def health_check(self):
        counter_limit = 3
        counter = 0
        for channel, values in self.__channels.items():
            if not values["active"] and values["activation_failures"] < 3:
                if not values["banned"]:
                    self.log.warn(f"Channel `{channel}` was found to be inactive. resending join request.")
                    await self._part(channel)
                    await self._join(channel)
                else:
                    self.log.warn(f"You're banned from channel `{channel}` - will not reinitiate connected to this channel.")
                values["activation_failures"] += 1
                counter += 1
                if counter > counter_limit:
                    return


    async def send(self, channel: str, message: str):
        self.log.info(f"Sent ({channel}): {message}")
        await self._send_raw(f"PRIVMSG #{channel.lower()} :{message}")

    async def _send_raw(self, message: str):
        try:
            if message[:4] == "PASS":
                self.log.debug(f" < PASS ****")
            else:
                self.log.debug(f" < {message}")
            self.writer.write((f"{message}\r\n").encode('utf-8'))
            # self.socket.send((f"{message}\r\n").encode('utf-8'))
            await asyncio.sleep(INTERVAL)
        except BrokenPipeError:
            self.log.critical(f"Broken pipe identified. Triggering reconnection '{message}'")
            await self.reconnect()
        except OSError:
            self.log.critical(f"Socket is closed and must be reopened to send the message '{message}'")


    async def run(self):
        try:
            while self.active:
                await self.__process_stream_message()
            try:
                self.writer.close()
                # self.socket.close()
            except Exception as e:
                self.log.critical(f"Suppressing a caught an exception while attempting to close the socket in `Socket.run()`. Details below\n{type(e)}: {traceback.format_exc()}")
        finally: 
            self.log.info(f"Closing socket.")
            if (self.writer):
                # if (self.socket):
                await self.disconnect()


    def __activate_channel(self, channel):
        self.__channels[channel]["active"] = True
        self.__channels[channel]["activation_failures"] = 0

    async def __process_stream_message(self):
        if not self.active:
            return
        try:
            if self.reader.at_eof():
                self.log.warn("recieved EOF from server, will attempt to reconnect socket. Standby...")
                await self.reconnect()
            else:
                self.buffer += (await self.reader.readline()).decode()
            # self.buffer = self.buffer + (await self.loop.sock_recv(self.socket, 1024)).decode()
        except ConnectionAbortedError as e:
            self.log.info(f"Socket connection has Closed\nDetails below\n{type(e)}: {traceback.format_exc()}")
            if self.active:
                await self.reconnect()
        except UnicodeDecodeError as e:
            self.log.warning(f"Unicode Decode error detected, possible issue with the buffer.\nBuffer: [{self.buffer}]\n\nDetails below\n{type(e)}: {traceback.format_exc()}\n\nRegenerating buffer...")
            self.buffer = ""
            self.log.info(f"Buffer regeneration completed.")
        except OSError as e:
            self.log.warning(f"OSError detected, socket issue identitfied. Attempting to recover socket. Details below\n{type(e)}: {traceback.format_exc()}")
            if self.active:
                await self.reconnect()

        temp = self.buffer.split("\n")
        self.buffer = temp.pop()
        for line in temp:
            self.log.debug(f" > {line.strip()}")
            if ("PING :tmi.twitch.tv" in line): # Keep Alive Mechanism
                await self._send_raw("PONG :tmi.twitch.tv")
                self.last_ping = datetime.now()
                continue
            self.loop.create_task(self.__process_line(line))
            await asyncio.sleep(INTERVAL)

    async def __process_line(self, line_text):
        message = parse_line(line_text, self.command_activator)
        message.set_socket(self)
        self.loop.create_task(self.client._scb_on_raw(message))

        if message.inner == "Message":
            self.loop.create_task(self.client._scb_on_message(message))
        elif message.inner == "Join":
            self.loop.create_task(self.client._scb_on_join(message))
        elif message.inner == "Mode":
            self.loop.create_task(self.client._scb_on_mode(message))
        elif message.inner == "Names":
            self.__activate_channel(message.channel)
            self.loop.create_task(self.client._scb_on_names(message))
        elif message.inner == "Part":
            self.loop.create_task(self.client._scb_on_part(message))
        elif message.inner == "ClearChat":
            self.loop.create_task(self.client._scb_on_clearchat(message))
        elif message.inner == "ClearMessage":
            self.loop.create_task(self.client._scb_on_clearmessage(message))
        elif message.inner == "HostTarget":
            self.loop.create_task(self.client._scb_on_hosttarget(message))
        elif message.inner == "Notice":
            if message.message_id == "msg_channel_suspended":
                self.__channels[message.channel]["activation_failures"] = 1000
                self.log.warn(f"Channel `{message.channel}` has been deleted or deactivated, a connection will not be retried. Please remove this channel from your channel list.")
            if message.message_id == "msg_banned":
                self.__channels[message.channel]["banned"] = True
                self.log.warn(f"Channel `{message.channel}` has banned you. Please remove this channel from your channel list.")
            self.loop.create_task(self.client._scb_on_notice(message))
        elif message.inner == "Reconnect":
            self.loop.create_task(self.client._scb_on_reconnect(message))
        elif message.inner == "RoomState":
            self.loop.create_task(self.client._scb_on_roomstate(message))
        elif message.inner == "UserState":
            self.loop.create_task(self.client._scb_on_userstate(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "GlobalUserState":
            self.loop.create_task(self.client._scb_on_globaluserstate(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "UserNotice":
            self.loop.create_task(self.client._scb_on_usernotice(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "RitualUserNotice":
            self.loop.create_task(self.client._scb_on_ritual_usernotice(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "BitBadgeUpgradeUserNotice":
            self.loop.create_task(self.client._scb_on_bitbadgeupgrade_usernotice(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "RaidUserNotice":
            self.loop.create_task(self.client._scb_on_raid_usernotice(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "Whisper" and self.primary_socket:
            self.log.info(f"[WHISPER]: ({message.display_name}) {message.message_text}")
            self.loop.create_task(self.client._scb_on_whisper(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "SubscriberUserNotice":
            if message.display_name.lower() != self.nick.lower():
                self.loop.create_task(self.client._scb_on_subscriber_usernotice(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "GiftedSubscriberUserNotice":
            if message.display_name.lower() != self.nick.lower():
                self.loop.create_task(self.client._scb_on_giftedsubscriber_usernotice(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "PrivateMessage":
            if message.display_name.lower() != self.nick.lower():
                self.log.info(f"[CHAT].[{message.channel}]: ({message.display_name}) {message.message_text}")
                self.loop.create_task(self.client._scb_on_privmessage(message))
            self.__message_counter[message.channel] += 1
        elif message.inner == "CommandMessage":
            if message.display_name.lower() != self.nick.lower():
                self.log.info(f"[CMD].[{message.channel}]: ({message.display_name}) {message.message_text}")
                self.loop.create_task(self.client._scb_on_command(message))
            self.__message_counter[message.channel] += 1
        await asyncio.sleep(INTERVAL)
        