from datetime import datetime
from jcore.exceptions import MissingRequiredParameterException

class RawMessage():
    inner: str = "RawMessage"
    line: str
    channel: str
    id: str
    message_time: datetime
    __socket = None


    def __repr__(self):
        return f"[{self.inner}]: {self.line}"

    def set_socket(self, socket):
        self.__socket = socket

    async def _send(self, message_text: str):
        await self.__socket.send(self.channel, message_text)

    async def _send_action(self, message_text: str):
        await self.__socket.send(self.channel, f"/me {message_text}")

    async def _ban(self, user, reason: str = "not provided"):
        await self.__socket.send(self.channel, f"/ban {user} {reason}")
    
    async def _unban(self, user):
        await self.__socket.send(self.channel, f"/unban {user}")

    async def _clear(self):
        await self.__socket.send(self.channel, f"/clear")

    async def _commercial(self, seconds: int = 30):
        await self.__socket.send(self.channel, f"/commercial {seconds}")
    
    async def _delete(self):
        await self.__socket.send(self.channel, f"/delete {self.id}")

    async def _emote_only(self):
        await self.__socket.send(self.channel, f"/emoteonly")
    
    async def _emote_only_off(self):
        await self.__socket.send(self.channel, f"/emoteonlyoff")

    async def _followers(self, duration:str):
        await self.__socket.send(self.channel, f"/followers {duration}")
    
    async def _followers_off(self):
        await self.__socket.send(self.channel, f"/followersoff")
    
    async def _host(self, channel: str = ""):
        await self.__socket.send(self.channel, f"/host {channel}")
    
    async def _host_off(self):
        await self.__socket.send(self.channel, f"/unhost")

    async def _marker(self, description: str = "undefined"):
        await self.__socket.send(self.channel, f"/marker {description}")

    async def _raid(self, channel: str = ""):
        await self.__socket.send(self.channel, f"/raid {channel}")
    
    async def _raid_off(self):
        await self.__socket.send(self.channel, f"/unraid")

    async def _slow(self, seconds: int = 2):
        await self.__socket.send(self.channel, f"/slow {seconds}")
    
    async def _slow_off(self):
        await self.__socket.send(self.channel, f"/slowoff")

    async def _subscribers(self):
        await self.__socket.send(self.channel, f"/subscribers")
    
    async def _subscribers_off(self):
        await self.__socket.send(self.channel, f"/subscribersoff")

    async def _timeout(self, user, duration:int = 0, reason: str = "not provided"):
        await self.__socket.send(self.channel, f"/timeout {user} {duration} {reason}")
    
    async def _untimeout(self, user):
        await self.__socket.send(self.channel, f"/untimeout {user}")

    async def _unique_chat(self):
        await self.__socket.send(self.channel, f"/uniquechat")
    
    async def _unique_chat_off(self):
        await self.__socket.send(self.channel, f"/uniquechatoff")
    
    

class Message(RawMessage):
    message: str
    inner:str = "Message"
    pass

    def __repr__(self):
        return f"[{self.inner}]: {self.message}"



# Twitch IRC: Membership | https://dev.twitch.tv/docs/irc/membership

class Join(RawMessage):
    inner:str = "Join"
    user:str
    pass

    def __repr__(self):
        return f"[{self.inner}]: `{self.user}` joined channel: `{self.channel}` => {self.line}"

    async def send(self, message_text: str):
        """Send a message to the chat"""
        await self._send(message_text)

    async def send_action(self, message_text: str):
        """Send an 'action' message to the chat"""
        await self._send_action(message_text)

    

class Mode(RawMessage):
    inner:str = "Mode"
    pass

class Names(RawMessage):
    inner:str = "Names"
    pass

class Part(RawMessage):
    inner:str = "Part"
    user:str
    pass

    def __repr__(self):
        return f"[{self.inner}]: `{self.user}` departed channel: `{self.channel}` => {self.line}"

    async def send(self, message_text: str):
        """Send a message to the chat"""
        await self._send(message_text)

    async def send_action(self, message_text: str):
        """Send an 'action' message to the chat"""
        await self._send_action(message_text)


class Whisper(RawMessage):
    inner: str = "Whisper"
    badges: dict
    color: str
    display_name: str
    emotes: list
    user_id: str
    message_text: str
    channel: str
    pass

    def __repr__(self):
        return f"[{self.inner}]: {self.display_name} => {self.message_text}"

    async def reply(self, message_text:str):
        """Send a reply to the user that whispered you.

        Parameters
        ----------
            - `message_text` [str]: message to send user

        Raises
        ------
            - `MissingRequiredParameterException`

        """
        if message_text == "" or message_text is None:
            raise MissingRequiredParameterException("parameter `message_text` is required")
        await self._send(f"/w {self.display_name.lower()} {message_text}")




# Twitch IRC: Commands & Tags | 
# https://dev.twitch.tv/docs/irc/commands & https://dev.twitch.tv/docs/irc/tags

class ClearChat(RawMessage):
    inner: str = "ClearChat"
    target_all: bool
    ban_duration: int
    channel: str
    
    def __repr__(self):
        return f"""[CLEARCHAT]:
Ban Duration: {self.ban_duration}
Channel: {self.channel}
"""

class ClearMessage(Message):
    inner: str = "ClearMessage"
    login: str
    target_message_id: str
    pass

class HostTarget(RawMessage):
    inner: str = "HostTarget"
    number_of_viewers: int
    pass

class Notice(Message):
    inner: str = "Notice"
    message_id: str
    pass

class Reconnect(RawMessage):
    inner: str = "Reconnect"
    pass

class RoomState(RawMessage):
    inner: str = "RoomState"
    emote_only: bool
    follower_only: bool
    r9k: bool
    slow: int
    subs_only: bool
    channel: str
    
    def __repr__(self):
        return f"""[ROOMSTATE]:
Emote Only?: {self.emote_only}
Follower Only?: {self.follower_only}
R9K?: {self.r9k}
Slow Interval: {self.slow}
Subs Only?: {self.subs_only}
Channel: {self.channel}
"""



class UserState(RawMessage):
    """
    Sends user-state data when a user joins a channel or sends a PRIVMSG to a channel.

    info: https://dev.twitch.tv/docs/irc/tags#userstate-twitch-tags
    """
    inner: str = "UserState"
    badge_info: str
    badges: list
    color: str
    display_name: str
    emote_set: list
    mod: bool
    channel: str


    def __repr__(self):
        return f"""[USERSTATE]:
Badge info: {self.badge_info}
Badges: {self.badges}
Display Name: {self.display_name}
Emote Set: {self.emote_set}
Mod?: {self.mod}
Channel: {self.channel}
"""

class GlobalUserState(RawMessage):
    """
    On successful login, provides data about the current 
    logged-in user through IRC tags. It is sent after successfully 
    authenticating (sending a PASS/NICK command).

    info: https://dev.twitch.tv/docs/irc/tags#globaluserstate-twitch-tags
    """
    inner: str = "GlobalUserState"
    badge_info: dict
    badges: dict
    color: str
    display_name: str
    emote_set: list
    user_id: str
    pass
    
class PrivateMessage(RawMessage):
    """
    Sends a message to a channel. 
    A regular Twitch chat message.

    info: https://dev.twitch.tv/docs/irc/tags#privmsg-twitch-tags
    """
    inner: str = "PrivateMessage"
    badge_info: dict
    badges: dict
    bits: int
    color: str
    display_name: str
    emotes: list
    mod: bool
    sub: bool
    room_id: str
    sent_timestamp: datetime
    user_id: str
    message_text: str
    channel: str
    
    def __repr__(self):
        return f"""[PRIVMSG]:
Badge info: {self.badge_info}
Badges: {self.badges}
Bits: {self.bits}
Color: {self.color}
Display Name: {self.display_name}
Emotes: {self.emotes}
ID: {self.id}
Mod?: {self.mod}
Sub?: {self.sub}
Room-ID: {self.room_id}
Sent Timestamp: {self.sent_timestamp}
User-ID: {self.user_id}
Channel: {self.channel}
Message Text: {self.message_text}
"""


    async def send(self, message_text: str):
        """Send a message to the chat"""
        await self._send(message_text)

    async def send_action(self, message_text: str):
        """Send an 'action' message to the chat"""
        await self._send_action(message_text)

    async def ban(self, user: str, reason: str = "not provided"):
        """Ban a user from the chat  
        
        Required Scope: `channel:moderate`

        Parameters
        ----------
            - `user` [str]: username of the user to ban
            - `reason` [str] (optional): reason for the ban

        Raises
        ------
            - `MissingRequiredParameterException`
        """
        if user == "" or user is None:
            raise MissingRequiredParameterException("parameter `user` is required")
        await self._ban(user, reason)
    
    async def unban(self, user: str):
        """Un-Ban a user from the chat  
        
        Required Scope: `channel:moderate`

        Parameters:
        -----------
            - `user`: username of the user to un-ban

        Raises
        ------
            - `MissingRequiredParameterException`
        """
        if user == "" or user is None:
            raise MissingRequiredParameterException("parameter `user` is required")
        await self._unban(user)

    async def clear(self):
        """Clear messages for all users from chat.
        
        Required Scope: `channel:moderate`"""
        await self._clear()

    async def commercial(self, seconds: int = 30):
        """Roll commercial for Affiliates and Partners
        
        Required Scope: `channel_commercial`
        
        Parameters:
        -----------
            - `seconds` (optional): run a commercial for {30|60|90|120|150|180} seconds | Default 30"""
        await self._commercial(seconds)
    
    async def delete(self):
        """Delete the message from chat for all users
        
        Required Scope: `channel:moderate`"""
        await self._delete()

    async def emote_only(self):
        """Enable "emote only" mode for chat.
        
        Required Scope: `channel:moderate`"""
        await self._emote_only()
    
    async def emote_only_off(self):
        """Disable "emote only" mode for chat
        
        Required Scope: `channel:moderate`"""
        await self._emote_only_off()

    async def followers(self, duration:str = ""):
        """Enable "follower only" mode for chat.

        Required Scope: `channel:moderate`

        Parameters
        ----------
            - `duration` (optional): minimum number of minutes a user must follow 
            the channel before they are able to send messages.
        """
        await self._followers(duration)
    
    async def followers_off(self):
        """Disable "follower only" mode for chat.
        
        Required Scope: `channel:moderate`"""
        await self._followers_off()
    
    async def host(self, channel: str):
        """Enable hosting for another channel
        
        Required Scope: `channel_editor`
        
        Parameters
        ----------
            - `channel`: the channel to host.
            
        Raises
        ------
            - `MissingRequiredParameterException`
        """

        if channel == "" or channel is None:
            raise MissingRequiredParameterException("parameter `channel` is required")
        await self._host(channel)
    
    async def host_off(self):
        """Disable hosting of another channel  
        
        Required Scope: `channel_editor`
        """
        await self._host_off()

    async def marker(self, description: str = "undefined"):
        """Adds a stream marker (with an optional description, max 140 characters) 
        at the current timestamp.  
        
        Required Scope: `channel_editor`

        Parameters
        ----------
            - `description` (optional): description, max 140 characters.
        """
        await self._marker(description)

    async def raid(self, channel: str = ""):
        """Start a raid on another channel when the stream ends
        
        Required Scope: `channel_editor`
        
        Parameters
        ----------
            - `channel`: the channel to raid.
            
        Raises
        ------
            - `MissingRequiredParameterException`
        """

        if channel == "" or channel is None:
            raise MissingRequiredParameterException("parameter `channel` is required")
        await self._raid(channel)
    
    async def raid_off(self):
        """Disable or cancel the raid on another channel  
        
        Required Scope: `channel_editor`
        """
        await self._raid_off()

    async def slow(self, seconds: int = 2):
        """Limit how frequently users can send messages in Chat
        
        Required Scope: `channel:moderate`
        
        Parameters
        ----------
            - `seconds` (optional): the minimum number of seconds between messages."""
        await self._slow(seconds)
    
    async def slow_off(self):
        """Turn off slow mode
        
        Required Scope: `channel:moderate`"""
        await self._slow_off()

    async def subscribers(self):
        """Restrict chat to subscribers  
        
        Required Scope: `channel:moderate`"""
        await self._subscribers()
    
    async def subscribers_off(self):
        """Turn off subscriber-only mode
        
        Required Scope: `channel:moderate`"""
        await self._subscribers_off()

    async def timeout(self, user, duration:int = 0, reason: str = "not provided"):
        """Temporarily ban a user from Chat
        
        Required Scope: `channel:moderate`

        Parameters
        ----------
            - `user` [str]: username of the user to ban
            - `duration [int] (optional): the number of seconds to ban the user for 
            - `reason` [str] (optional): reason for the ban

        Raises
        ------
            - `MissingRequiredParameterException`
        
        """
        if user == "" or user is None:
            raise MissingRequiredParameterException("parameter `user` is required")
        await self._timeout(user, duration, reason)
    
    async def untimeout(self, user):
        """Remove a timeout on a user
        
        Required Scope: `channel:moderate`

        Parameters
        ----------
            - `user` [str]: username of the user to ban

        Raises
        ------
            - `MissingRequiredParameterException`
        
        """
        if user == "" or user is None:
            raise MissingRequiredParameterException("parameter `user` is required")
        await self._untimeout(user)

    async def unique_chat(self):
        """Prevent users from sending duplicate messages in Chat
        
        Required Scope: `channel:moderate`
        """
        await self._unique_chat()
    
    async def unique_chat_off(self):
        """Turn off unique-chat mode
        
        Required Scope: `channel:moderate`
        """
        await self._unique_chat_off()

    async def whisper(self, user: str,  message_text:str):
        """Send a whisper to a user.

        Parameters
        ----------
            - `user` [str]: username of the user to ban
            - `message_text` [str]: message to send user

        Raises
        ------
            - `MissingRequiredParameterException`
        
        """
        if user == "" or user is None:
            raise MissingRequiredParameterException("parameter `user` is required")
        if message_text == "" or message_text is None:
            raise MissingRequiredParameterException("parameter `message_text` is required")
        await self._send(f"/w {user.lower()} {message_text}")




class UserNotice(PrivateMessage):
    """
    Sends a notice to the user when any of the following events occurs:

    - Subscription, resubscription, or gift subscription to a channel.
    - Incoming raid to a channel. Raid is a Twitch tool that allows broadcasters to send their viewers to another channel, to help support and grow other members in the community.)
    - Channel ritual. Many channels have special rituals to celebrate viewer milestones when they are shared. The rituals notice extends the sharing of these messages to other viewer milestones (initially, a new viewer chatting for the first time).

    info: https://dev.twitch.tv/docs/irc/tags#usernotice-twitch-tags
    """
    inner: str = "UserNotice"
    login: str
    msg_id: str
    system_message: str
    
    def __repr__(self):
        return f"""[UserNotice]:
Badge info: {self.badge_info}
Badges: {self.badges}
Bits: {self.bits}
Color: {self.color}
Display Name: {self.display_name}
Emotes: {self.emotes}
ID: {self.id}
Mod?: {self.mod}
Sub?: {self.sub}
Room-ID: {self.room_id}
Sent Timestamp: {self.sent_timestamp}
User-ID: {self.user_id}
Channel: {self.channel}
Message Text: {self.message_text}
Login: {self.login}
System Message: {self.system_message}
"""



class RitualUserNotice(UserNotice):
    inner: str = "RitualUserNotice"
    ritual_name: str
    pass

class BitBadgeUpgradeUserNotice(UserNotice):
    inner: str = "BitBadgeUpgradeUserNotice"
    threshold: int
    pass

class RaidUserNotice(UserNotice):
    """
    A UserNotice Object for Raids
    """
    inner: str = "RaidUserNotice"
    raider_display_name: str
    raider_login: str
    viewer_count: int

class SubscriberUserNotice(UserNotice):
    """
    A UserNotice Object for Subscription or Re-subscription Events
    """
    inner: str = "SubscriberUserNotice"
    cumulative_months: int
    share_streak: bool
    streak_months: int
    sub_plan: str
    sub_plan_name: str

    def __repr__(self):
        return f"""[{self.inner}]:
Badge info: {self.badge_info}
Badges: {self.badges}
Bits: {self.bits}
Color: {self.color}
Display Name: {self.display_name}
Emotes: {self.emotes}
ID: {self.id}
Mod?: {self.mod}
Sub?: {self.sub}
Room-ID: {self.room_id}
Sent Timestamp: {self.sent_timestamp}
User-ID: {self.user_id}
Channel: {self.channel}
Message Text: {self.message_text}
Login: {self.login}
System Message: {self.system_message}
Cumulative months: {self.cumulative_months}
Share Streak: {self.share_streak}
Streak Months: {self.streak_months}
Sub Plan: {self.sub_plan}
Sub Plan Name: {self.sub_plan_name}
"""

class GiftedSubscriberUserNotice(UserNotice):
    """
    A UserNotice Object for Gifted Subs, included Anonyumous Gifts.
    """
    inner: str = "GiftedSubscriberUserNotice"
    cumulative_months: int
    anonymous: bool
    # active_promo: bool
    promo_gift_total: int
    promo_name: str
    mass_gift_count: int
    recipient_display_name: str
    recipient_id: str
    recipient_login: str
    sender_login: str
    sender_display_name: str
    sender_count: int
    sub_plan: str
    sub_plan_name: str

    def __repr__(self):
        return f"""[{self.inner}]:
Badge info: {self.badge_info}
Badges: {self.badges}
Bits: {self.bits}
Color: {self.color}
Display Name: {self.display_name}
Emotes: {self.emotes}
ID: {self.id}
Mod?: {self.mod}
Sub?: {self.sub}
Room-ID: {self.room_id}
Sent Timestamp: {self.sent_timestamp}
User-ID: {self.user_id}
Channel: {self.channel}
Message Text: {self.message_text}
Login: {self.login}
System Message: {self.system_message}
Anonymous Sub: {self.anonymous}
Promotion Gift Total: {self.promo_gift_total}
Promotion Name: {self.promo_name}
Mass Gift Count: {self.mass_gift_count}
Recipient Display Name: {self.recipient_display_name}
Recipient ID: {self.recipient_id}
Recipient Login: {self.recipient_login}
Sender Display Name: {self.sender_display_name}
Sender Login: {self.sender_login}
Sender Count: {self.sender_count}
Subscriber Plan: {self.sub_plan}
Subscriber Plan Name: {self.sub_plan_name}
"""



class CommandMessage(PrivateMessage):
    KEYWORD: str
    args: list    
    inner: str = "CommandMessage"
    args_len: int
    

    def __repr__(self):
        return f"""[PRIVMSG: Command]:
Badge info: {self.badge_info}
Badges: {self.badges}
Bits: {self.bits}
Color: {self.color}
Display Name: {self.display_name}
Emotes: {self.emotes}
ID: {self.id}
Mod?: {self.mod}
Sub?: {self.sub}
Room-ID: {self.room_id}
Sent Timestamp: {self.sent_timestamp}
User-ID: {self.user_id}
Channel: {self.channel}
Message Text: {self.message_text}
Keyword: {self.KEYWORD}
"""



