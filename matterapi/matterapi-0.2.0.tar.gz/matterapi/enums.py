from enum import Enum


class PluginStatusState(str, Enum):
    NOTRUNNING = "NotRunning"
    STARTING = "Starting"
    RUNNING = "Running"
    FAILEDTOSTART = "FailedToStart"
    FAILEDTOSTAYRUNNING = "FailedToStayRunning"
    STOPPING = "Stopping"

    def __str__(self) -> str:
        return str(self.value)


class SidebarCategoryType(str, Enum):
    CHANNELS = "channels"
    CUSTOM = "custom"
    DIRECT_MESSAGES = "direct_messages"
    FAVORITES = "favorites"

    def __str__(self) -> str:
        return str(self.value)


class SidebarCategoryWithChannelsType(str, Enum):
    CHANNELS = "channels"
    CUSTOM = "custom"
    DIRECT_MESSAGES = "direct_messages"
    FAVORITES = "favorites"

    def __str__(self) -> str:
        return str(self.value)


class UploadSessionType(str, Enum):
    ATTACHMENT = "attachment"
    IMPORT_ = "import"

    def __str__(self) -> str:
        return str(self.value)


class PostMetadataEmbedsItemType(str, Enum):
    IMAGE = "image"
    MESSAGE_ATTACHMENT = "message_attachment"
    OPENGRAPH = "opengraph"
    LINK = "link"

    def __str__(self) -> str:
        return str(self.value)
