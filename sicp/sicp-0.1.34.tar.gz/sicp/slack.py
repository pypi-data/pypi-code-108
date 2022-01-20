from __future__ import annotations

import enum
from collections import defaultdict
from dataclasses import dataclass
from json import load
from typing import List, Optional, Union

import click
from npyscreen import (
    ActionControllerSimple,
    FormBaseNew,
    FormMuttActiveTraditional,
    MultiLineAction,
    NPSAppManaged,
)
from tqdm import tqdm

from sicp.slack_export import slack_export


@click.group()
def slack():
    """
    Interact with the Slackbot
    """


class SlackViewer(NPSAppManaged):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.curr_conversation = None
        self.curr_thread = None
        self.curr_message = None

    def onStart(self):
        self.registerForm("MAIN", ConversationListForm())
        self.registerForm("CONVERSATION", ConversationForm())
        self.registerForm("THREAD", ThreadForm())


class ConversationSelector(MultiLineAction):
    def display_value(self, conversation):
        return f"{conversation.name} ({len(conversation.messages)} messages)"

    def actionHighlighted(self, conversation, key_press):
        self.find_parent_app().curr_conversation = conversation
        self.find_parent_app().curr_message = None
        self.find_parent_app().switchForm("CONVERSATION")


class ConversationListForm(FormBaseNew):
    def create(self):
        self.conversation_selectors = self.add(
            ConversationSelector, name="conversations", values=[]
        )

    def beforeEditing(self):
        self.conversation_selectors.values = sorted(
            (c for c in self.find_parent_app().data.values() if c.messages),
            key=lambda c: len(c.messages),
            reverse=True,
        )


class MessageSelector(MultiLineAction):
    def actionHighlighted(self, result, key_press):
        if isinstance(result, SearchResult):
            if isinstance(result.link, MessageThreadData):
                self.find_parent_app().curr_thread = result.link
                self.find_parent_app().curr_message = result.message
                self.find_parent_app().switchForm("THREAD")
            elif isinstance(result.link, Message):
                self.find_parent_app().curr_conversation = result.link.conversation
                self.find_parent_app().curr_message = result.link
                self.find_parent_app().switchForm("CONVERSATION")


class ConversationActionController(ActionControllerSimple):
    def create(self):
        self.add_action(".*", self.clear_status, False)
        self.add_action("^/.*", self.set_search, False)
        self.add_action("^:.*", self.handle_action, False)

    def set_search(self, command_line, widget_proxy, live):
        needle = command_line[1:]
        self.parent.wMain.values = (
            self.parent.find_parent_app().curr_conversation.filter_messages(
                needle, self.parent.wMain.width
            )
        )
        self.parent.wMain.display()

    def handle_action(self, command_line, widget_proxy, live):
        action = command_line[1:]
        if action == "b" or action == "back":
            self.parent.find_parent_app().switchFormPrevious()
        elif action == "q" or action == "quit":
            raise KeyboardInterrupt
        else:
            self.parent.wStatus2.value = "Unknown command: " + action
            self.parent.wStatus2.display()

    def clear_status(self, command_line, widget_proxy, live):
        self.parent.wStatus2.value = ""
        self.parent.wStatus2.display()


class ConversationForm(FormMuttActiveTraditional):
    MAIN_WIDGET_CLASS = MessageSelector
    COMMAND_WIDGET_NAME = "cmd:"
    ACTION_CONTROLLER = ConversationActionController

    def beforeEditing(self):
        self.wStatus1.value = self.find_parent_app().curr_conversation.name
        self.wMain.values = self.find_parent_app().curr_conversation.filter_messages(
            None,
            self.wMain.width,
        )
        if self.find_parent_app().curr_message:
            self.wMain.cursor_line = min(
                i
                for i, result in enumerate(self.wMain.values)
                if result.message == self.find_parent_app().curr_message
            )
            self.find_parent_app().curr_message = None


class ThreadForm(FormMuttActiveTraditional):
    MAIN_WIDGET_CLASS = MessageSelector
    COMMAND_WIDGET_NAME = "cmd:"
    ACTION_CONTROLLER = ConversationActionController

    def beforeEditing(self):
        self.wStatus1.value = self.find_parent_app().curr_conversation.name
        self.wMain.values = [
            line
            for message in self.find_parent_app().curr_thread.messages
            for line in message.lines(
                width=self.wMain.width, context=MessageContext.THREAD
            )
        ]
        if self.find_parent_app().curr_message:
            self.wMain.cursor_line = min(
                i
                for i, result in enumerate(self.wMain.values)
                if result.message == self.find_parent_app().curr_message
            )
            self.find_parent_app().curr_message = None


class MessageContext(enum.Enum):
    SEARCH_RESULT = enum.auto()
    CONVERSATION = enum.auto()
    THREAD = enum.auto()


@dataclass
class Conversation:
    id: str
    name: str
    messages: List[Message]

    def filter_messages(self, needle, width):
        messages = self.messages
        if not needle:
            return [
                line
                for m in messages
                if not m.thread_data or m == m.thread_data.root
                for line in m.lines(width, context=MessageContext.CONVERSATION)
            ]

        values = []
        for i, m in enumerate(messages):
            if needle in m.data["text"]:
                values.append("")
                if i > 0:
                    values.append(
                        SearchResult(
                            "...",
                            messages[i - 1],
                            messages[i - 1].link(MessageContext.SEARCH_RESULT),
                        )
                    )
                    values.extend(
                        messages[i - 1].lines(
                            width, context=MessageContext.SEARCH_RESULT
                        )
                    )
                values.extend(
                    messages[i].lines(width, context=MessageContext.SEARCH_RESULT)
                )
                if i + 1 != len(messages):
                    values.extend(
                        messages[i + 1].lines(
                            width, context=MessageContext.SEARCH_RESULT
                        )
                    )
                    values.append(
                        SearchResult(
                            "...",
                            messages[i + 1],
                            messages[i + 1].link(MessageContext.SEARCH_RESULT),
                        )
                    )
                values.append("")
        return values


@dataclass
class SearchResult:
    value: str
    message: Message
    link: Union[Message, MessageThreadData, None]

    def __str__(self):
        return self.value


@dataclass
class Message:
    id: str
    data: dict
    thread_data: Optional[MessageThreadData]
    conversation: Conversation

    def thread_ts(self) -> Optional[str]:
        if "permalink" in self.data and "thread_ts" in self.data["permalink"]:
            return self.data["permalink"].split("thread_ts=")[-1]

    def str(self, context: MessageContext):
        if self.thread_data:
            if self.thread_data.thread_index:
                if context == MessageContext.THREAD:
                    return (
                        f"{self.data['user']}: "
                        f"[{self.thread_data.thread_index + 1} / {len(self.thread_data.messages)}] "
                        f"{self.data['text']}"
                    )
                else:
                    return (
                        f"{self.data['user']}: "
                        f"({self.thread_data.thread_index + 1} of {len(self.thread_data.messages)} replies) "
                        f"{self.data['text']}"
                    )
            else:
                return (
                    f"{self.data['user']}: "
                    f"({len(self.thread_data.messages)} replies) "
                    f"{self.data['text']}"
                )

        return f"{self.data['user']}: {self.data['text']}"

    def lines(self, width, context: MessageContext, indent=12):
        width -= indent
        raw = self.str(context)
        out = []
        for part in raw.split("\n"):
            for i in range(0, len(part), width):
                out.append(" " * (4 if out else 0) + part[i : i + width])

        out = [SearchResult(line, self, self.link(context)) for line in out]
        return out

    def link(self, context: MessageContext):
        # clicking a message in a conversation should open its thread
        if context == MessageContext.CONVERSATION and self.thread_data:
            return self.thread_data

        # if a search yields a reply within a thread, we should open that thread directly
        if (
            context == MessageContext.SEARCH_RESULT
            and self.thread_data
            and self.thread_data.thread_index
        ):
            return self.thread_data

        # if a message outside a thread (or a thread root) is in a search, clicks should open it
        if context == MessageContext.SEARCH_RESULT:
            return self


@dataclass
class MessageThreadData:
    id: str
    root: Message
    messages: List[Message]
    thread_index: int


def user_name(user) -> str:
    profile = user["profile"]
    return profile.get("real_name", profile["display_name"])


@slack.command()
@click.option("--json", type=click.File("r"), required=True)
def view(json):
    """
    View a JSON export of all Slack messages
    """
    data = load(json)

    users = {user["id"]: user for user in data.pop("_users", [])}

    conversations = {}

    # prepare lookups
    for c_id, c in tqdm(data.items()):
        ts_lookup = {}
        thread_lookup = defaultdict(list)
        messages = []
        conversation = Conversation(c_id, c["name"], messages)

        for msg in c["messages"]:
            for user_id, user in users.items():
                msg["text"] = msg["text"].replace(
                    f"<@{user_id}>",
                    "@" + user_name(user),
                )
            for channel_id, channel in data.items():
                msg["text"] = msg["text"].replace(
                    f"<#{channel_id}>", "#" + channel["name"]
                )
                msg["text"] = msg["text"].replace(
                    f"<#{channel_id}|{channel['name']}>", "#" + channel["name"]
                )
            if msg["user"] in users:
                msg["user"] = user_name(users[msg["user"]])
            message = Message(msg["ts"], msg, None, conversation)
            messages.append(message)
            ts_lookup[message.id] = message
            thread_lookup[message.thread_ts()].append(message)

        for msg in messages:
            if msg.thread_ts():
                msg.thread_data = MessageThreadData(
                    msg.thread_ts(),
                    ts_lookup[msg.thread_ts()],
                    thread_lookup[msg.thread_ts()],
                    thread_lookup[msg.thread_ts()].index(msg),
                )

        conversations[c_id] = conversation

    SlackViewer(conversations).run()


slack.add_command(click.command()(slack_export), "export")
