from __future__ import unicode_literals

import asyncio
import random
import string
import time
from copy import deepcopy

from channels.exceptions import ChannelFull
from channels.layers import BaseChannelLayer


class AsyncInMemoryChannelLayer(BaseChannelLayer):
    """
    In-memory channel layer implementation
    """

    def __init__(
            self,
            expiry=60,
            group_expiry=3600,
            capacity=1000,
            channel_capacity=None,
            **kwargs
    ):
        super().__init__(
            expiry=expiry,
            capacity=capacity,
            channel_capacity=channel_capacity,
            **kwargs
        )
        self.channels = {}
        self.groups = {}
        self.group_expiry = group_expiry

    ### Channel layer API ###

    extensions = ["groups", "flush"]

    async def send(self, channel, message):
        """
        Send a message onto a (general or specific) channel.
        """
        # Typecheck
        assert isinstance(message, dict), "message is not a dict"
        assert self.valid_channel_name(channel), "Channel name not valid"
        # If it's a process-local channel, strip off local part and stick full name in message
        assert "__asgi_channel__" not in message

        queue = self.channels.setdefault(channel, asyncio.Queue())
        # Are we full
        if self.capacity and (queue.qsize() >= self.capacity):
            # raise ChannelFull(channel)
            queue.empty()

        # Add message
        await queue.put((time.time() + self.expiry, deepcopy(message)))

    async def receive(self, channel):
        """
        Receive the first message that arrives on the channel.
        If more than one coroutine waits on the same channel, a random one
        of the waiting coroutines will get the result.
        """
        assert self.valid_channel_name(channel)
        self._clean_expired()

        queue = self.channels.setdefault(channel, asyncio.Queue())

        # Do a plain direct receive
        _, message = await queue.get()

        # Delete if empty
        if queue.empty():
            del self.channels[channel]

        return message

    async def new_channel(self, prefix="specific."):
        """
        Returns a new channel name that can be used by something in our
        process as a specific channel.
        """
        return "%s.inmemory!%s" % (
            prefix,
            "".join(random.choice(string.ascii_letters) for i in range(12)),
        )

    ### Expire cleanup ###

    def _clean_expired(self):
        """
        Goes through all messages and groups and removes those that are expired.
        Any channel with an expired message is removed from all groups.
        """
        # Channel cleanup
        for channel, queue in list(self.channels.items()):
            remove = False
            # See if it's expired
            while not queue.empty() and queue._queue[0][0] < time.time():
                queue.get_nowait()
                remove = True
            # Any removal prompts group discard
            if remove:
                self._remove_from_groups(channel)
            # Is the channel now empty and needs deleting?
            if not queue:
                del self.channels[channel]

        # Group Expiration
        timeout = int(time.time()) - self.group_expiry
        for group in self.groups:
            for channel in list(self.groups.get(group, set())):
                # If join time is older than group_expiry end the group membership
                if (
                        self.groups[group][channel]
                        and int(self.groups[group][channel]) < timeout
                ):
                    # Delete from group
                    del self.groups[group][channel]

    ### Flush extension ###

    async def flush(self):
        self.channels = {}
        self.groups = {}

    async def close(self):
        # Nothing to go
        pass

    def _remove_from_groups(self, channel):
        """
        Removes a channel from all groups. Used when a message on it expires.
        """
        for channels in self.groups.values():
            if channel in channels:
                del channels[channel]

    ### Groups extension ###

    async def group_add(self, group, channel):
        """
        Adds the channel name to a group.
        """
        # Check the inputs
        assert self.valid_group_name(group), "Group name not valid"
        assert self.valid_channel_name(channel), "Channel name not valid"
        # Add to group dict
        self.groups.setdefault(group, {})
        self.groups[group][channel] = time.time()

    async def group_discard(self, group, channel):
        # Both should be text and valid
        assert self.valid_channel_name(channel), "Invalid channel name"
        assert self.valid_group_name(group), "Invalid group name"
        # Remove from group set
        if group in self.groups:
            if channel in self.groups[group]:
                del self.groups[group][channel]
            if not self.groups[group]:
                del self.groups[group]

    async def group_send(self, group, message):
        # Check types
        assert isinstance(message, dict), "Message is not a dict"
        assert self.valid_group_name(group), "Invalid group name"
        # Run clean
        self._clean_expired()
        # Send to each channel
        for channel in self.groups.get(group, set()):
            try:
                await self.send(channel, message)
            except ChannelFull:
                pass

# class InMemoryChannelLayer(BaseChannelLayer):
#     """
#     In-memory channel layer implementation
#     """
#
#     def __init__(
#             self,
#             expiry=60,
#             group_expiry=86400,
#             capacity=10000,
#             channel_capacity=None,
#             **kwargs
#     ):
#         super().__init__(
#             expiry=expiry,
#             capacity=capacity,
#             channel_capacity=channel_capacity,
#             **kwargs
#         )
#         self.channels = {}
#         self.groups = {}
#         self.group_expiry = group_expiry
#
#     ### Channel layer API ###
#
#     extensions = ["groups", "flush"]
#
#     def send(self, channel, message):
#         """
#         Send a message onto a (general or specific) channel.
#         """
#         # Typecheck
#         assert isinstance(message, dict), "message is not a dict"
#         assert self.valid_channel_name(channel), "Channel name not valid"
#         # If it's a process-local channel, strip off local part and stick full name in message
#         assert "__asgi_channel__" not in message
#
#         queue = self.channels.setdefault(channel, asyncio.Queue())
#         # Are we full
#         if queue.qsize() >= self.capacity:
#             raise ChannelFull(channel)
#
#         # Add message
#         queue.put((time.time() + self.expiry, deepcopy(message)))
#
#     def receive(self, channel):
#         """
#         Receive the first message that arrives on the channel.
#         If more than one coroutine waits on the same channel, a random one
#         of the waiting coroutines will get the result.
#         """
#         assert self.valid_channel_name(channel)
#         self._clean_expired()
#
#         queue = self.channels.setdefault(channel, asyncio.Queue())
#
#         # Do a plain direct receive
#         _, message = queue.get()
#
#         # Delete if empty
#         if queue.empty():
#             del self.channels[channel]
#
#         return message
#
#     def new_channel(self, prefix="specific."):
#         """
#         Returns a new channel name that can be used by something in our
#         process as a specific channel.
#         """
#         return "%s.inmemory!%s" % (
#             prefix,
#             "".join(random.choice(string.ascii_letters) for i in range(12)),
#         )
#
#     ### Expire cleanup ###
#
#     def _clean_expired(self):
#         """
#         Goes through all messages and groups and removes those that are expired.
#         Any channel with an expired message is removed from all groups.
#         """
#         # Channel cleanup
#         for channel, queue in list(self.channels.items()):
#             remove = False
#             # See if it's expired
#             while not queue.empty() and queue._queue[0][0] < time.time():
#                 queue.get_nowait()
#                 remove = True
#             # Any removal prompts group discard
#             if remove:
#                 self._remove_from_groups(channel)
#             # Is the channel now empty and needs deleting?
#             if not queue:
#                 del self.channels[channel]
#
#         # Group Expiration
#         timeout = int(time.time()) - self.group_expiry
#         for group in self.groups:
#             for channel in list(self.groups.get(group, set())):
#                 # If join time is older than group_expiry end the group membership
#                 if (
#                         self.groups[group][channel]
#                         and int(self.groups[group][channel]) < timeout
#                 ):
#                     # Delete from group
#                     del self.groups[group][channel]
#
#     ### Flush extension ###
#
#     def flush(self):
#         self.channels = {}
#         self.groups = {}
#
#     def close(self):
#         # Nothing to go
#         pass
#
#     def _remove_from_groups(self, channel):
#         """
#         Removes a channel from all groups. Used when a message on it expires.
#         """
#         for channels in self.groups.values():
#             if channel in channels:
#                 del channels[channel]
#
#     ### Groups extension ###
#
#     def group_add(self, group, channel):
#         """
#         Adds the channel name to a group.
#         """
#         # Check the inputs
#         assert self.valid_group_name(group), "Group name not valid"
#         assert self.valid_channel_name(channel), "Channel name not valid"
#         # Add to group dict
#         self.groups.setdefault(group, {})
#         self.groups[group][channel] = time.time()
#
#     def group_discard(self, group, channel):
#         # Both should be text and valid
#         assert self.valid_channel_name(channel), "Invalid channel name"
#         assert self.valid_group_name(group), "Invalid group name"
#         # Remove from group set
#         if group in self.groups:
#             if channel in self.groups[group]:
#                 del self.groups[group][channel]
#             if not self.groups[group]:
#                 del self.groups[group]
#
#     def group_send(self, group, message):
#         # Check types
#         assert isinstance(message, dict), "Message is not a dict"
#         assert self.valid_group_name(group), "Invalid group name"
#         # Run clean
#         self._clean_expired()
#         # Send to each channel
#         for channel in self.groups.get(group, set()):
#             try:
#                 self.send(channel, message)
#             except ChannelFull:
#                 pass
