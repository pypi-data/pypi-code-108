import jcore
from jcore.message import *

class Module():
    name : str

    def __init__(self, name):
        self.name = name

    def get_name(self):
        if self.name is None:
            return "undefined"
        return self.name


    async def on_raw(self, message: RawMessage): 
        """Invoked when a RawMessage message is sent to the bot."""
        pass

    async def on_join(self, message: Join): 
        """Invoked when a Join message is sent to the bot."""
        pass

    async def on_part(self, message: Part): 
        """Invoked when a Part message is sent to the bot."""
        pass

    async def on_mode(self, message: Mode): 
        """Invoked when a Mode message is sent to the bot."""
        pass

    async def on_names(self, message: Names): 
        """Invoked when a Names message is sent to the bot."""
        pass

    async def on_clearchat(self, message: ClearChat): 
        """Invoked when a ClearChat message is sent to the bot."""
        pass

    async def on_clearmessage(self, message: ClearMessage): 
        """Invoked when a ClearMessage message is sent to the bot."""
        pass

    async def on_hosttarget(self, message: HostTarget): 
        """Invoked when a HostTarget message is sent to the bot."""
        pass

    async def on_notice(self, message: Notice): 
        """Invoked when a Notice message is sent to the bot."""
        pass

    async def on_reconnect(self, message: Reconnect): 
        """Invoked when a Reconnect message is sent to the bot."""
        pass

    async def on_roomstate(self, message: RoomState): 
        """Invoked when a RoomState message is sent to the bot."""
        pass

    async def on_userstate(self, message: UserState): 
        """Invoked when a UserState message is sent to the bot."""
        pass

    async def on_globaluserstate(self, message: GlobalUserState): 
        """Invoked when a GlobalUserState message is sent to the bot."""
        pass

    async def on_privmessage(self, message: PrivateMessage): 
        """Invoked when a PrivateMessage message is sent to the bot."""
        pass

    async def on_usernotice(self, message: UserNotice): 
        """Invoked when a UserNotice message is sent to the bot."""
        pass

    async def on_ritual_usernotice(self, message: RitualUserNotice): 
        """Invoked when a RitualUserNotice message is sent to the bot."""
        pass

    async def on_bitbadgeupgrade_usernotice(self, message: BitBadgeUpgradeUserNotice): 
        """Invoked when a BitBadgeUpgradeUserNotice message is sent to the bot."""
        pass

    async def on_raid_usernotice(self, message: RaidUserNotice): 
        """Invoked when a RaidUserNotice message is sent to the bot."""
        pass

    async def on_subscriber_usernotice(self, message: SubscriberUserNotice): 
        """Invoked when a SubscriberUserNotice message is sent to the bot."""
        pass

    async def on_giftedsubscriber_usernotice(self, message: GiftedSubscriberUserNotice): 
        """Invoked when a GiftedSubscriberUserNotice message is sent to the bot."""
        pass

    async def on_whisper(self, message: Whisper): 
        """Invoked when a Whisper message is sent to the bot."""
        pass

    async def on_command(self, message: CommandMessage): 
        """Invoked when a CommandMessage message is sent to the bot."""
        pass

    async def on_heartbeat(self): 
        """Invoked periodically by the bot as a status check."""
        pass


