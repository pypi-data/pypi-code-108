from typing import ClassVar, Dict, List, Optional, Set

from .enums import (
    PluginStatusState,
    PostMetadataEmbedsItemType,
    SidebarCategoryType,
    SidebarCategoryWithChannelsType,
    UploadSessionType,
)
from .types import BaseArray, BaseConfig, BaseMapping, File


class UsersStats(BaseConfig):
    """
    Attributes:
        total_users_count (Optional[int]):
    """

    total_users_count: Optional[int] = None


class Team(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        create_at (Optional[int]): The time in milliseconds a team was created
        update_at (Optional[int]): The time in milliseconds a team was last
            updated
        delete_at (Optional[int]): The time in milliseconds a team was deleted
        display_name (Optional[str]):
        name (Optional[str]):
        description (Optional[str]):
        email (Optional[str]):
        type (Optional[str]):
        allowed_domains (Optional[str]):
        invite_id (Optional[str]):
        allow_open_invite (Optional[bool]):
        policy_id (Optional[str]): The data retention policy to which this team
            has been assigned. If no such policy exists, or the caller does not have
            the `sysconsole_read_compliance_data_retention` permission, this field
            will be null.
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    display_name: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    allowed_domains: Optional[str] = None
    invite_id: Optional[str] = None
    allow_open_invite: Optional[bool] = None
    policy_id: Optional[str] = None


class TeamStats(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]):
        total_member_count (Optional[int]):
        active_member_count (Optional[int]):
    """

    team_id: Optional[str] = None
    total_member_count: Optional[int] = None
    active_member_count: Optional[int] = None


class TeamExists(BaseConfig):
    """
    Attributes:
        exists (Optional[bool]):
    """

    exists: Optional[bool] = None


class Channel(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        create_at (Optional[int]): The time in milliseconds a channel was
            created
        update_at (Optional[int]): The time in milliseconds a channel was last
            updated
        delete_at (Optional[int]): The time in milliseconds a channel was
            deleted
        team_id (Optional[str]):
        type (Optional[str]):
        display_name (Optional[str]):
        name (Optional[str]):
        header (Optional[str]):
        purpose (Optional[str]):
        last_post_at (Optional[int]): The time in milliseconds of the last post
            of a channel
        total_msg_count (Optional[int]):
        extra_update_at (Optional[int]): Deprecated in Mattermost 5.0 release
        creator_id (Optional[str]):
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    team_id: Optional[str] = None
    type: Optional[str] = None
    display_name: Optional[str] = None
    name: Optional[str] = None
    header: Optional[str] = None
    purpose: Optional[str] = None
    last_post_at: Optional[int] = None
    total_msg_count: Optional[int] = None
    extra_update_at: Optional[int] = None
    creator_id: Optional[str] = None


class ChannelStats(BaseConfig):
    """
    Attributes:
        channel_id (Optional[str]):
        member_count (Optional[int]):
    """

    channel_id: Optional[str] = None
    member_count: Optional[int] = None


class ChannelWithTeamData(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        create_at (Optional[int]): The time in milliseconds a channel was
            created
        update_at (Optional[int]): The time in milliseconds a channel was last
            updated
        delete_at (Optional[int]): The time in milliseconds a channel was
            deleted
        team_id (Optional[str]):
        type (Optional[str]):
        display_name (Optional[str]):
        name (Optional[str]):
        header (Optional[str]):
        purpose (Optional[str]):
        last_post_at (Optional[int]): The time in milliseconds of the last post
            of a channel
        total_msg_count (Optional[int]):
        extra_update_at (Optional[int]): Deprecated in Mattermost 5.0 release
        creator_id (Optional[str]):
        team_display_name (Optional[str]): The display name of the team to which
            this channel belongs.
        team_name (Optional[str]): The name of the team to which this channel
            belongs.
        team_update_at (Optional[int]): The time at which the team to which this
            channel belongs was last updated.
        policy_id (Optional[str]): The data retention policy to which this team
            has been assigned. If no such policy exists, or the caller does not have
            the `sysconsole_read_compliance_data_retention` permission, this field
            will be null.
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    team_id: Optional[str] = None
    type: Optional[str] = None
    display_name: Optional[str] = None
    name: Optional[str] = None
    header: Optional[str] = None
    purpose: Optional[str] = None
    last_post_at: Optional[int] = None
    total_msg_count: Optional[int] = None
    extra_update_at: Optional[int] = None
    creator_id: Optional[str] = None
    team_display_name: Optional[str] = None
    team_name: Optional[str] = None
    team_update_at: Optional[int] = None
    policy_id: Optional[str] = None


class ChannelListWithTeamData(BaseArray):
    """"""

    __root__: List[ChannelWithTeamData]


class TeamMap(BaseConfig):
    """A mapping of teamIds to teams.

    Attributes:
        team_id (Optional[Team]):
    """

    team_id: Optional[Team] = None


class TeamMember(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]): The ID of the team this member belongs to.
        user_id (Optional[str]): The ID of the user this member relates to.
        roles (Optional[str]): The complete list of roles assigned to this team
            member, as a space-separated list of role names, including any roles
            granted implicitly through permissions schemes.
        delete_at (Optional[int]): The time in milliseconds that this team
            member was deleted.
        scheme_user (Optional[bool]): Whether this team member holds the default
            user role defined by the team's permissions scheme.
        scheme_admin (Optional[bool]): Whether this team member holds the
            default admin role defined by the team's permissions scheme.
        explicit_roles (Optional[str]): The list of roles explicitly assigned to
            this team member, as a space separated list of role names. This list
            does *not* include any roles granted implicitly through permissions
            schemes.
    """

    team_id: Optional[str] = None
    user_id: Optional[str] = None
    roles: Optional[str] = None
    delete_at: Optional[int] = None
    scheme_user: Optional[bool] = None
    scheme_admin: Optional[bool] = None
    explicit_roles: Optional[str] = None


class TeamUnread(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]):
        msg_count (Optional[int]):
        mention_count (Optional[int]):
    """

    team_id: Optional[str] = None
    msg_count: Optional[int] = None
    mention_count: Optional[int] = None


class ChannelUnread(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]):
        channel_id (Optional[str]):
        msg_count (Optional[int]):
        mention_count (Optional[int]):
    """

    team_id: Optional[str] = None
    channel_id: Optional[str] = None
    msg_count: Optional[int] = None
    mention_count: Optional[int] = None


class ChannelUnreadAt(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]): The ID of the team the channel belongs to.
        channel_id (Optional[str]): The ID of the channel the user has access
            to..
        msg_count (Optional[int]): No. of messages the user has already read.
        mention_count (Optional[int]): No. of mentions the user has within the
            unread posts of the channel.
        last_viewed_at (Optional[int]): time in milliseconds when the user last
            viewed the channel.
    """

    team_id: Optional[str] = None
    channel_id: Optional[str] = None
    msg_count: Optional[int] = None
    mention_count: Optional[int] = None
    last_viewed_at: Optional[int] = None


class Session(BaseConfig):
    """
    Attributes:
        create_at (Optional[int]): The time in milliseconds a session was
            created
        device_id (Optional[str]):
        expires_at (Optional[int]): The time in milliseconds a session will
            expire
        id (Optional[str]):
        is_oauth (Optional[bool]):
        last_activity_at (Optional[int]): The time in milliseconds of the last
            activity of a session
        props (Optional[Props]):
        roles (Optional[str]):
        team_members (Optional[List[TeamMember]]):
        token (Optional[str]):
        user_id (Optional[str]):
    """

    class Props(BaseConfig):
        """"""

    create_at: Optional[int] = None
    device_id: Optional[str] = None
    expires_at: Optional[int] = None
    id: Optional[str] = None
    is_oauth: Optional[bool] = None
    last_activity_at: Optional[int] = None
    props: Optional[Props] = None
    roles: Optional[str] = None
    team_members: Optional[List[TeamMember]] = None
    token: Optional[str] = None
    user_id: Optional[str] = None


class FileInfo(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique identifier for this file
        user_id (Optional[str]): The ID of the user that uploaded this file
        post_id (Optional[str]): If this file is attached to a post, the ID of
            that post
        create_at (Optional[int]): The time in milliseconds a file was created
        update_at (Optional[int]): The time in milliseconds a file was last
            updated
        delete_at (Optional[int]): The time in milliseconds a file was deleted
        name (Optional[str]): The name of the file
        extension (Optional[str]): The extension at the end of the file name
        size (Optional[int]): The size of the file in bytes
        mime_type (Optional[str]): The MIME type of the file
        width (Optional[int]): If this file is an image, the width of the file
        height (Optional[int]): If this file is an image, the height of the file
        has_preview_image (Optional[bool]): If this file is an image, whether or
            not it has a preview-sized version
    """

    id: Optional[str] = None
    user_id: Optional[str] = None
    post_id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    name: Optional[str] = None
    extension: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    has_preview_image: Optional[bool] = None


class Preference(BaseConfig):
    """
    Attributes:
        user_id (Optional[str]): The ID of the user that owns this preference
        category (Optional[str]):
        name (Optional[str]):
        value (Optional[str]):
    """

    user_id: Optional[str] = None
    category: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None


class UserAuthData(BaseConfig):
    """
    Attributes:
        auth_data (str): Service-specific authentication data
        auth_service (str): The authentication service such as "email",
            "gitlab", or "ldap"
    """

    auth_data: str
    auth_service: str


class IncomingWebhook(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique identifier for this incoming webhook
        create_at (Optional[int]): The time in milliseconds a incoming webhook
            was created
        update_at (Optional[int]): The time in milliseconds a incoming webhook
            was last updated
        delete_at (Optional[int]): The time in milliseconds a incoming webhook
            was deleted
        channel_id (Optional[str]): The ID of a public channel or private group
            that receives the webhook payloads
        description (Optional[str]): The description for this incoming webhook
        display_name (Optional[str]): The display name for this incoming webhook
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    channel_id: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None


class OutgoingWebhook(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique identifier for this outgoing webhook
        create_at (Optional[int]): The time in milliseconds a outgoing webhook
            was created
        update_at (Optional[int]): The time in milliseconds a outgoing webhook
            was last updated
        delete_at (Optional[int]): The time in milliseconds a outgoing webhook
            was deleted
        creator_id (Optional[str]): The Id of the user who created the webhook
        team_id (Optional[str]): The ID of the team that the webhook watchs
        channel_id (Optional[str]): The ID of a public channel that the webhook
            watchs
        description (Optional[str]): The description for this outgoing webhook
        display_name (Optional[str]): The display name for this outgoing webhook
        trigger_words (Optional[List[str]]): List of words for the webhook to
            trigger on
        trigger_when (Optional[int]): When to trigger the webhook, `0` when a
            trigger word is present at all and `1` if the message starts with a
            trigger word
        callback_urls (Optional[List[str]]): The URLs to POST the payloads to
            when the webhook is triggered
        content_type (Optional[str]): The format to POST the data in, either
            `application/json` or `application/x-www-form-urlencoded`
             Default: 'application/x-www-form-urlencoded'.
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    creator_id: Optional[str] = None
    team_id: Optional[str] = None
    channel_id: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    trigger_words: Optional[List[str]] = None
    trigger_when: Optional[int] = None
    callback_urls: Optional[List[str]] = None
    content_type: Optional[str] = "application/x-www-form-urlencoded"


class Reaction(BaseConfig):
    """
    Attributes:
        user_id (Optional[str]): The ID of the user that made this reaction
        post_id (Optional[str]): The ID of the post to which this reaction was
            made
        emoji_name (Optional[str]): The name of the emoji that was used for this
            reaction
        create_at (Optional[int]): The time in milliseconds this reaction was
            made
    """

    user_id: Optional[str] = None
    post_id: Optional[str] = None
    emoji_name: Optional[str] = None
    create_at: Optional[int] = None


class Emoji(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The ID of the emoji
        creator_id (Optional[str]): The ID of the user that made the emoji
        name (Optional[str]): The name of the emoji
        create_at (Optional[int]): The time in milliseconds the emoji was made
        update_at (Optional[int]): The time in milliseconds the emoji was last
            updated
        delete_at (Optional[int]): The time in milliseconds the emoji was
            deleted
    """

    id: Optional[str] = None
    creator_id: Optional[str] = None
    name: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None


class Command(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The ID of the slash command
        token (Optional[str]): The token which is used to verify the source of
            the payload
        create_at (Optional[int]): The time in milliseconds the command was
            created
        update_at (Optional[int]): The time in milliseconds the command was last
            updated
        delete_at (Optional[int]): The time in milliseconds the command was
            deleted, 0 if never deleted
        creator_id (Optional[str]): The user id for the commands creator
        team_id (Optional[str]): The team id for which this command is
            configured
        trigger (Optional[str]): The string that triggers this command
        method (Optional[str]): Is the trigger done with HTTP Get ('G') or HTTP
            Post ('P')
        username (Optional[str]): What is the username for the response post
        icon_url (Optional[str]): The url to find the icon for this users avatar
        auto_complete (Optional[bool]): Use auto complete for this command
        auto_complete_desc (Optional[str]): The description for this command
            shown when selecting the command
        auto_complete_hint (Optional[str]): The hint for this command
        display_name (Optional[str]): Display name for the command
        description (Optional[str]): Description for this command
        url (Optional[str]): The URL that is triggered
    """

    id: Optional[str] = None
    token: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    creator_id: Optional[str] = None
    team_id: Optional[str] = None
    trigger: Optional[str] = None
    method: Optional[str] = None
    username: Optional[str] = None
    icon_url: Optional[str] = None
    auto_complete: Optional[bool] = None
    auto_complete_desc: Optional[str] = None
    auto_complete_hint: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class AutocompleteSuggestion(BaseConfig):
    """
    Attributes:
        complete (Optional[str]): Completed suggestion
        suggestion (Optional[str]): Predicted text user might want to input
        hint (Optional[str]): Hint about suggested input
        description (Optional[str]): Description of the suggested command
        icon_data (Optional[str]): Base64 encoded svg image
    """

    complete: Optional[str] = None
    suggestion: Optional[str] = None
    hint: Optional[str] = None
    description: Optional[str] = None
    icon_data: Optional[str] = None


class SlackAttachmentField(BaseConfig):
    """
    Attributes:
        title (Optional[str]):
        value (Optional[str]): The value of the attachment, set as string but
            capable with golang interface
        short (Optional[bool]):
    """

    title: Optional[str] = None
    value: Optional[str] = None
    short: Optional[bool] = None


class StatusOK(BaseConfig):
    """
    Attributes:
        status (Optional[str]): Will contain "ok" if the request was successful
            and there was nothing else to return
    """

    status: Optional[str] = None


class OpenGraphImagesItem(BaseConfig):
    """Image object used in OpenGraph metadata of a webpage

    Attributes:
        url (Optional[str]):
        secure_url (Optional[str]):
        type (Optional[str]):
        width (Optional[int]):
        height (Optional[int]):
    """

    url: Optional[str] = None
    secure_url: Optional[str] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class OpenGraphVideosItem(BaseConfig):
    """Video object used in OpenGraph metadata of a webpage

    Attributes:
        url (Optional[str]):
        secure_url (Optional[str]):
        type (Optional[str]):
        width (Optional[int]):
        height (Optional[int]):
    """

    url: Optional[str] = None
    secure_url: Optional[str] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class OpenGraphAudiosItem(BaseConfig):
    """Audio object used in OpenGraph metadata of a webpage

    Attributes:
        url (Optional[str]):
        secure_url (Optional[str]):
        type (Optional[str]):
    """

    url: Optional[str] = None
    secure_url: Optional[str] = None
    type: Optional[str] = None


class ArticleAuthorsItem(BaseConfig):
    """
    Attributes:
        first_name (Optional[str]):
        last_name (Optional[str]):
        username (Optional[str]):
        gender (Optional[str]):
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    gender: Optional[str] = None


class BookAuthorsItem(BaseConfig):
    """
    Attributes:
        first_name (Optional[str]):
        last_name (Optional[str]):
        username (Optional[str]):
        gender (Optional[str]):
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    gender: Optional[str] = None


class OpenGraph(BaseConfig):
    """OpenGraph metadata of a webpage

    Attributes:
        type (Optional[str]):
        url (Optional[str]):
        title (Optional[str]):
        description (Optional[str]):
        determiner (Optional[str]):
        site_name (Optional[str]):
        locale (Optional[str]):
        locales_alternate (Optional[List[str]]):
        images (Optional[List[OpenGraphImagesItem]]):
        videos (Optional[List[OpenGraphVideosItem]]):
        audios (Optional[List[OpenGraphAudiosItem]]):
        article (Optional[Article]): Article object used in OpenGraph metadata
            of a webpage, if type is article
        book (Optional[Book]): Book object used in OpenGraph metadata of a
            webpage, if type is book
        profile (Optional[Profile]):
    """

    class Article(BaseConfig):
        """Article object used in OpenGraph metadata of a webpage, if type is
        article

            Attributes:
                published_time (Optional[str]):
                modified_time (Optional[str]):
                expiration_time (Optional[str]):
                section (Optional[str]):
                tags (Optional[List[str]]):
                authors (Optional[List[ArticleAuthorsItem]]):
        """

        published_time: Optional[str] = None
        modified_time: Optional[str] = None
        expiration_time: Optional[str] = None
        section: Optional[str] = None
        tags: Optional[List[str]] = None
        authors: Optional[List[ArticleAuthorsItem]] = None

    class Book(BaseConfig):
        """Book object used in OpenGraph metadata of a webpage, if type is book

        Attributes:
            isbn (Optional[str]):
            release_date (Optional[str]):
            tags (Optional[List[str]]):
            authors (Optional[List[BookAuthorsItem]]):
        """

        isbn: Optional[str] = None
        release_date: Optional[str] = None
        tags: Optional[List[str]] = None
        authors: Optional[List[BookAuthorsItem]] = None

    class Profile(BaseConfig):
        """
        Attributes:
            first_name (Optional[str]):
            last_name (Optional[str]):
            username (Optional[str]):
            gender (Optional[str]):
        """

        first_name: Optional[str] = None
        last_name: Optional[str] = None
        username: Optional[str] = None
        gender: Optional[str] = None

    type: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    determiner: Optional[str] = None
    site_name: Optional[str] = None
    locale: Optional[str] = None
    locales_alternate: Optional[List[str]] = None
    images: Optional[List[OpenGraphImagesItem]] = None
    videos: Optional[List[OpenGraphVideosItem]] = None
    audios: Optional[List[OpenGraphAudiosItem]] = None
    article: Optional[Article] = None
    book: Optional[Book] = None
    profile: Optional[Profile] = None


class Audit(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        create_at (Optional[int]): The time in milliseconds a audit was created
        user_id (Optional[str]):
        action (Optional[str]):
        extra_info (Optional[str]):
        ip_address (Optional[str]):
        session_id (Optional[str]):
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    user_id: Optional[str] = None
    action: Optional[str] = None
    extra_info: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None


class Config(BaseConfig):
    """
    Attributes:
        service_settings (Optional[ServiceSettings]):
        team_settings (Optional[TeamSettings]):
        sql_settings (Optional[SqlSettings]):
        log_settings (Optional[LogSettings]):
        password_settings (Optional[PasswordSettings]):
        file_settings (Optional[FileSettings]):
        email_settings (Optional[EmailSettings]):
        rate_limit_settings (Optional[RateLimitSettings]):
        privacy_settings (Optional[PrivacySettings]):
        support_settings (Optional[SupportSettings]):
        git_lab_settings (Optional[GitLabSettings]):
        google_settings (Optional[GoogleSettings]):
        office365_settings (Optional[Office365Settings]):
        ldap_settings (Optional[LdapSettings]):
        compliance_settings (Optional[ComplianceSettings]):
        localization_settings (Optional[LocalizationSettings]):
        saml_settings (Optional[SamlSettings]):
        native_app_settings (Optional[NativeAppSettings]):
        cluster_settings (Optional[ClusterSettings]):
        metrics_settings (Optional[MetricsSettings]):
        analytics_settings (Optional[AnalyticsSettings]):
    """

    class ServiceSettings(BaseConfig):
        """
        Attributes:
            site_url (Optional[str]):
            listen_address (Optional[str]):
            connection_security (Optional[str]):
            tls_cert_file (Optional[str]):
            tls_key_file (Optional[str]):
            use_lets_encrypt (Optional[bool]):
            lets_encrypt_certificate_cache_file (Optional[str]):
            forward80_to443 (Optional[bool]):
            read_timeout (Optional[int]):
            write_timeout (Optional[int]):
            maximum_login_attempts (Optional[int]):
            segment_developer_key (Optional[str]):
            google_developer_key (Optional[str]):
            enable_oauth_service_provider (Optional[bool]):
            enable_incoming_webhooks (Optional[bool]):
            enable_outgoing_webhooks (Optional[bool]):
            enable_commands (Optional[bool]):
            enable_only_admin_integrations (Optional[bool]):
            enable_post_username_override (Optional[bool]):
            enable_post_icon_override (Optional[bool]):
            enable_testing (Optional[bool]):
            enable_developer (Optional[bool]):
            enable_security_fix_alert (Optional[bool]):
            enable_insecure_outgoing_connections (Optional[bool]):
            enable_multifactor_authentication (Optional[bool]):
            enforce_multifactor_authentication (Optional[bool]):
            allow_cors_from (Optional[str]):
            session_length_web_in_days (Optional[int]):
            session_length_mobile_in_days (Optional[int]):
            session_length_sso_in_days (Optional[int]):
            session_cache_in_minutes (Optional[int]):
            websocket_secure_port (Optional[int]):
            websocket_port (Optional[int]):
            webserver_mode (Optional[str]):
            enable_custom_emoji (Optional[bool]):
            restrict_custom_emoji_creation (Optional[str]):
        """

        site_url: Optional[str] = None
        listen_address: Optional[str] = None
        connection_security: Optional[str] = None
        tls_cert_file: Optional[str] = None
        tls_key_file: Optional[str] = None
        use_lets_encrypt: Optional[bool] = None
        lets_encrypt_certificate_cache_file: Optional[str] = None
        forward80_to443: Optional[bool] = None
        read_timeout: Optional[int] = None
        write_timeout: Optional[int] = None
        maximum_login_attempts: Optional[int] = None
        segment_developer_key: Optional[str] = None
        google_developer_key: Optional[str] = None
        enable_oauth_service_provider: Optional[bool] = None
        enable_incoming_webhooks: Optional[bool] = None
        enable_outgoing_webhooks: Optional[bool] = None
        enable_commands: Optional[bool] = None
        enable_only_admin_integrations: Optional[bool] = None
        enable_post_username_override: Optional[bool] = None
        enable_post_icon_override: Optional[bool] = None
        enable_testing: Optional[bool] = None
        enable_developer: Optional[bool] = None
        enable_security_fix_alert: Optional[bool] = None
        enable_insecure_outgoing_connections: Optional[bool] = None
        enable_multifactor_authentication: Optional[bool] = None
        enforce_multifactor_authentication: Optional[bool] = None
        allow_cors_from: Optional[str] = None
        session_length_web_in_days: Optional[int] = None
        session_length_mobile_in_days: Optional[int] = None
        session_length_sso_in_days: Optional[int] = None
        session_cache_in_minutes: Optional[int] = None
        websocket_secure_port: Optional[int] = None
        websocket_port: Optional[int] = None
        webserver_mode: Optional[str] = None
        enable_custom_emoji: Optional[bool] = None
        restrict_custom_emoji_creation: Optional[str] = None

    class TeamSettings(BaseConfig):
        """
        Attributes:
            site_name (Optional[str]):
            max_users_per_team (Optional[int]):
            enable_team_creation (Optional[bool]):
            enable_user_creation (Optional[bool]):
            enable_open_server (Optional[bool]):
            restrict_creation_to_domains (Optional[str]):
            enable_custom_brand (Optional[bool]):
            custom_brand_text (Optional[str]):
            custom_description_text (Optional[str]):
            restrict_direct_message (Optional[str]):
            restrict_team_invite (Optional[str]):
            restrict_public_channel_management (Optional[str]):
            restrict_private_channel_management (Optional[str]):
            restrict_public_channel_creation (Optional[str]):
            restrict_private_channel_creation (Optional[str]):
            restrict_public_channel_deletion (Optional[str]):
            restrict_private_channel_deletion (Optional[str]):
            user_status_away_timeout (Optional[int]):
            max_channels_per_team (Optional[int]):
            max_notifications_per_channel (Optional[int]):
        """

        site_name: Optional[str] = None
        max_users_per_team: Optional[int] = None
        enable_team_creation: Optional[bool] = None
        enable_user_creation: Optional[bool] = None
        enable_open_server: Optional[bool] = None
        restrict_creation_to_domains: Optional[str] = None
        enable_custom_brand: Optional[bool] = None
        custom_brand_text: Optional[str] = None
        custom_description_text: Optional[str] = None
        restrict_direct_message: Optional[str] = None
        restrict_team_invite: Optional[str] = None
        restrict_public_channel_management: Optional[str] = None
        restrict_private_channel_management: Optional[str] = None
        restrict_public_channel_creation: Optional[str] = None
        restrict_private_channel_creation: Optional[str] = None
        restrict_public_channel_deletion: Optional[str] = None
        restrict_private_channel_deletion: Optional[str] = None
        user_status_away_timeout: Optional[int] = None
        max_channels_per_team: Optional[int] = None
        max_notifications_per_channel: Optional[int] = None

    class SqlSettings(BaseConfig):
        """
        Attributes:
            driver_name (Optional[str]):
            data_source (Optional[str]):
            data_source_replicas (Optional[List[str]]):
            max_idle_conns (Optional[int]):
            max_open_conns (Optional[int]):
            trace (Optional[bool]):
            at_rest_encrypt_key (Optional[str]):
        """

        driver_name: Optional[str] = None
        data_source: Optional[str] = None
        data_source_replicas: Optional[List[str]] = None
        max_idle_conns: Optional[int] = None
        max_open_conns: Optional[int] = None
        trace: Optional[bool] = None
        at_rest_encrypt_key: Optional[str] = None

    class LogSettings(BaseConfig):
        """
        Attributes:
            enable_console (Optional[bool]):
            console_level (Optional[str]):
            enable_file (Optional[bool]):
            file_level (Optional[str]):
            file_location (Optional[str]):
            enable_webhook_debugging (Optional[bool]):
            enable_diagnostics (Optional[bool]):
        """

        enable_console: Optional[bool] = None
        console_level: Optional[str] = None
        enable_file: Optional[bool] = None
        file_level: Optional[str] = None
        file_location: Optional[str] = None
        enable_webhook_debugging: Optional[bool] = None
        enable_diagnostics: Optional[bool] = None

    class PasswordSettings(BaseConfig):
        """
        Attributes:
            minimum_length (Optional[int]):
            lowercase (Optional[bool]):
            number (Optional[bool]):
            uppercase (Optional[bool]):
            symbol (Optional[bool]):
        """

        minimum_length: Optional[int] = None
        lowercase: Optional[bool] = None
        number: Optional[bool] = None
        uppercase: Optional[bool] = None
        symbol: Optional[bool] = None

    class FileSettings(BaseConfig):
        """
        Attributes:
            max_file_size (Optional[int]):
            driver_name (Optional[str]):
            directory (Optional[str]):
            enable_public_link (Optional[bool]):
            public_link_salt (Optional[str]):
            thumbnail_width (Optional[int]):
            thumbnail_height (Optional[int]):
            preview_width (Optional[int]):
            preview_height (Optional[int]):
            profile_width (Optional[int]):
            profile_height (Optional[int]):
            initial_font (Optional[str]):
            amazon_s3_access_key_id (Optional[str]):
            amazon_s3_secret_access_key (Optional[str]):
            amazon_s3_bucket (Optional[str]):
            amazon_s3_region (Optional[str]):
            amazon_s3_endpoint (Optional[str]):
            amazon_s3_ssl (Optional[bool]):
        """

        max_file_size: Optional[int] = None
        driver_name: Optional[str] = None
        directory: Optional[str] = None
        enable_public_link: Optional[bool] = None
        public_link_salt: Optional[str] = None
        thumbnail_width: Optional[int] = None
        thumbnail_height: Optional[int] = None
        preview_width: Optional[int] = None
        preview_height: Optional[int] = None
        profile_width: Optional[int] = None
        profile_height: Optional[int] = None
        initial_font: Optional[str] = None
        amazon_s3_access_key_id: Optional[str] = None
        amazon_s3_secret_access_key: Optional[str] = None
        amazon_s3_bucket: Optional[str] = None
        amazon_s3_region: Optional[str] = None
        amazon_s3_endpoint: Optional[str] = None
        amazon_s3_ssl: Optional[bool] = None

    class EmailSettings(BaseConfig):
        """
        Attributes:
            enable_sign_up_with_email (Optional[bool]):
            enable_sign_in_with_email (Optional[bool]):
            enable_sign_in_with_username (Optional[bool]):
            send_email_notifications (Optional[bool]):
            require_email_verification (Optional[bool]):
            feedback_name (Optional[str]):
            feedback_email (Optional[str]):
            feedback_organization (Optional[str]):
            smtp_username (Optional[str]):
            smtp_password (Optional[str]):
            smtp_server (Optional[str]):
            smtp_port (Optional[str]):
            connection_security (Optional[str]):
            invite_salt (Optional[str]):
            password_reset_salt (Optional[str]):
            send_push_notifications (Optional[bool]):
            push_notification_server (Optional[str]):
            push_notification_contents (Optional[str]):
            enable_email_batching (Optional[bool]):
            email_batching_buffer_size (Optional[int]):
            email_batching_interval (Optional[int]):
        """

        enable_sign_up_with_email: Optional[bool] = None
        enable_sign_in_with_email: Optional[bool] = None
        enable_sign_in_with_username: Optional[bool] = None
        send_email_notifications: Optional[bool] = None
        require_email_verification: Optional[bool] = None
        feedback_name: Optional[str] = None
        feedback_email: Optional[str] = None
        feedback_organization: Optional[str] = None
        smtp_username: Optional[str] = None
        smtp_password: Optional[str] = None
        smtp_server: Optional[str] = None
        smtp_port: Optional[str] = None
        connection_security: Optional[str] = None
        invite_salt: Optional[str] = None
        password_reset_salt: Optional[str] = None
        send_push_notifications: Optional[bool] = None
        push_notification_server: Optional[str] = None
        push_notification_contents: Optional[str] = None
        enable_email_batching: Optional[bool] = None
        email_batching_buffer_size: Optional[int] = None
        email_batching_interval: Optional[int] = None

    class RateLimitSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            per_sec (Optional[int]):
            max_burst (Optional[int]):
            memory_store_size (Optional[int]):
            vary_by_remote_addr (Optional[bool]):
            vary_by_header (Optional[str]):
        """

        enable: Optional[bool] = None
        per_sec: Optional[int] = None
        max_burst: Optional[int] = None
        memory_store_size: Optional[int] = None
        vary_by_remote_addr: Optional[bool] = None
        vary_by_header: Optional[str] = None

    class PrivacySettings(BaseConfig):
        """
        Attributes:
            show_email_address (Optional[bool]):
            show_full_name (Optional[bool]):
        """

        show_email_address: Optional[bool] = None
        show_full_name: Optional[bool] = None

    class SupportSettings(BaseConfig):
        """
        Attributes:
            terms_of_service_link (Optional[str]):
            privacy_policy_link (Optional[str]):
            about_link (Optional[str]):
            help_link (Optional[str]):
            report_aproblem_link (Optional[str]):
            support_email (Optional[str]):
        """

        terms_of_service_link: Optional[str] = None
        privacy_policy_link: Optional[str] = None
        about_link: Optional[str] = None
        help_link: Optional[str] = None
        report_aproblem_link: Optional[str] = None
        support_email: Optional[str] = None

    class GitLabSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            secret (Optional[str]):
            id (Optional[str]):
            scope (Optional[str]):
            auth_endpoint (Optional[str]):
            token_endpoint (Optional[str]):
            user_api_endpoint (Optional[str]):
        """

        enable: Optional[bool] = None
        secret: Optional[str] = None
        id: Optional[str] = None
        scope: Optional[str] = None
        auth_endpoint: Optional[str] = None
        token_endpoint: Optional[str] = None
        user_api_endpoint: Optional[str] = None

    class GoogleSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            secret (Optional[str]):
            id (Optional[str]):
            scope (Optional[str]):
            auth_endpoint (Optional[str]):
            token_endpoint (Optional[str]):
            user_api_endpoint (Optional[str]):
        """

        enable: Optional[bool] = None
        secret: Optional[str] = None
        id: Optional[str] = None
        scope: Optional[str] = None
        auth_endpoint: Optional[str] = None
        token_endpoint: Optional[str] = None
        user_api_endpoint: Optional[str] = None

    class Office365Settings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            secret (Optional[str]):
            id (Optional[str]):
            scope (Optional[str]):
            auth_endpoint (Optional[str]):
            token_endpoint (Optional[str]):
            user_api_endpoint (Optional[str]):
        """

        enable: Optional[bool] = None
        secret: Optional[str] = None
        id: Optional[str] = None
        scope: Optional[str] = None
        auth_endpoint: Optional[str] = None
        token_endpoint: Optional[str] = None
        user_api_endpoint: Optional[str] = None

    class LdapSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            ldap_server (Optional[str]):
            ldap_port (Optional[int]):
            connection_security (Optional[str]):
            base_dn (Optional[str]):
            bind_username (Optional[str]):
            bind_password (Optional[str]):
            user_filter (Optional[str]):
            first_name_attribute (Optional[str]):
            last_name_attribute (Optional[str]):
            email_attribute (Optional[str]):
            username_attribute (Optional[str]):
            nickname_attribute (Optional[str]):
            id_attribute (Optional[str]):
            position_attribute (Optional[str]):
            sync_interval_minutes (Optional[int]):
            skip_certificate_verification (Optional[bool]):
            query_timeout (Optional[int]):
            max_page_size (Optional[int]):
            login_field_name (Optional[str]):
        """

        enable: Optional[bool] = None
        ldap_server: Optional[str] = None
        ldap_port: Optional[int] = None
        connection_security: Optional[str] = None
        base_dn: Optional[str] = None
        bind_username: Optional[str] = None
        bind_password: Optional[str] = None
        user_filter: Optional[str] = None
        first_name_attribute: Optional[str] = None
        last_name_attribute: Optional[str] = None
        email_attribute: Optional[str] = None
        username_attribute: Optional[str] = None
        nickname_attribute: Optional[str] = None
        id_attribute: Optional[str] = None
        position_attribute: Optional[str] = None
        sync_interval_minutes: Optional[int] = None
        skip_certificate_verification: Optional[bool] = None
        query_timeout: Optional[int] = None
        max_page_size: Optional[int] = None
        login_field_name: Optional[str] = None

    class ComplianceSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            directory (Optional[str]):
            enable_daily (Optional[bool]):
        """

        enable: Optional[bool] = None
        directory: Optional[str] = None
        enable_daily: Optional[bool] = None

    class LocalizationSettings(BaseConfig):
        """
        Attributes:
            default_server_locale (Optional[str]):
            default_client_locale (Optional[str]):
            available_locales (Optional[str]):
        """

        default_server_locale: Optional[str] = None
        default_client_locale: Optional[str] = None
        available_locales: Optional[str] = None

    class SamlSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            verify (Optional[bool]):
            encrypt (Optional[bool]):
            idp_url (Optional[str]):
            idp_descriptor_url (Optional[str]):
            assertion_consumer_service_url (Optional[str]):
            idp_certificate_file (Optional[str]):
            public_certificate_file (Optional[str]):
            private_key_file (Optional[str]):
            first_name_attribute (Optional[str]):
            last_name_attribute (Optional[str]):
            email_attribute (Optional[str]):
            username_attribute (Optional[str]):
            nickname_attribute (Optional[str]):
            locale_attribute (Optional[str]):
            position_attribute (Optional[str]):
            login_button_text (Optional[str]):
        """

        enable: Optional[bool] = None
        verify: Optional[bool] = None
        encrypt: Optional[bool] = None
        idp_url: Optional[str] = None
        idp_descriptor_url: Optional[str] = None
        assertion_consumer_service_url: Optional[str] = None
        idp_certificate_file: Optional[str] = None
        public_certificate_file: Optional[str] = None
        private_key_file: Optional[str] = None
        first_name_attribute: Optional[str] = None
        last_name_attribute: Optional[str] = None
        email_attribute: Optional[str] = None
        username_attribute: Optional[str] = None
        nickname_attribute: Optional[str] = None
        locale_attribute: Optional[str] = None
        position_attribute: Optional[str] = None
        login_button_text: Optional[str] = None

    class NativeAppSettings(BaseConfig):
        """
        Attributes:
            app_download_link (Optional[str]):
            android_app_download_link (Optional[str]):
            ios_app_download_link (Optional[str]):
        """

        app_download_link: Optional[str] = None
        android_app_download_link: Optional[str] = None
        ios_app_download_link: Optional[str] = None

    class ClusterSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            inter_node_listen_address (Optional[str]):
            inter_node_urls (Optional[List[str]]):
        """

        enable: Optional[bool] = None
        inter_node_listen_address: Optional[str] = None
        inter_node_urls: Optional[List[str]] = None

    class MetricsSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            block_profile_rate (Optional[int]):
            listen_address (Optional[str]):
        """

        enable: Optional[bool] = None
        block_profile_rate: Optional[int] = None
        listen_address: Optional[str] = None

    class AnalyticsSettings(BaseConfig):
        """
        Attributes:
            max_users_for_statistics (Optional[int]):
        """

        max_users_for_statistics: Optional[int] = None

    service_settings: Optional[ServiceSettings] = None
    team_settings: Optional[TeamSettings] = None
    sql_settings: Optional[SqlSettings] = None
    log_settings: Optional[LogSettings] = None
    password_settings: Optional[PasswordSettings] = None
    file_settings: Optional[FileSettings] = None
    email_settings: Optional[EmailSettings] = None
    rate_limit_settings: Optional[RateLimitSettings] = None
    privacy_settings: Optional[PrivacySettings] = None
    support_settings: Optional[SupportSettings] = None
    git_lab_settings: Optional[GitLabSettings] = None
    google_settings: Optional[GoogleSettings] = None
    office365_settings: Optional[Office365Settings] = None
    ldap_settings: Optional[LdapSettings] = None
    compliance_settings: Optional[ComplianceSettings] = None
    localization_settings: Optional[LocalizationSettings] = None
    saml_settings: Optional[SamlSettings] = None
    native_app_settings: Optional[NativeAppSettings] = None
    cluster_settings: Optional[ClusterSettings] = None
    metrics_settings: Optional[MetricsSettings] = None
    analytics_settings: Optional[AnalyticsSettings] = None


class EnvironmentConfig(BaseConfig):
    """
    Attributes:
        service_settings (Optional[ServiceSettings]):
        team_settings (Optional[TeamSettings]):
        sql_settings (Optional[SqlSettings]):
        log_settings (Optional[LogSettings]):
        password_settings (Optional[PasswordSettings]):
        file_settings (Optional[FileSettings]):
        email_settings (Optional[EmailSettings]):
        rate_limit_settings (Optional[RateLimitSettings]):
        privacy_settings (Optional[PrivacySettings]):
        support_settings (Optional[SupportSettings]):
        git_lab_settings (Optional[GitLabSettings]):
        google_settings (Optional[GoogleSettings]):
        office365_settings (Optional[Office365Settings]):
        ldap_settings (Optional[LdapSettings]):
        compliance_settings (Optional[ComplianceSettings]):
        localization_settings (Optional[LocalizationSettings]):
        saml_settings (Optional[SamlSettings]):
        native_app_settings (Optional[NativeAppSettings]):
        cluster_settings (Optional[ClusterSettings]):
        metrics_settings (Optional[MetricsSettings]):
        analytics_settings (Optional[AnalyticsSettings]):
    """

    class ServiceSettings(BaseConfig):
        """
        Attributes:
            site_url (Optional[bool]):
            listen_address (Optional[bool]):
            connection_security (Optional[bool]):
            tls_cert_file (Optional[bool]):
            tls_key_file (Optional[bool]):
            use_lets_encrypt (Optional[bool]):
            lets_encrypt_certificate_cache_file (Optional[bool]):
            forward80_to443 (Optional[bool]):
            read_timeout (Optional[bool]):
            write_timeout (Optional[bool]):
            maximum_login_attempts (Optional[bool]):
            segment_developer_key (Optional[bool]):
            google_developer_key (Optional[bool]):
            enable_oauth_service_provider (Optional[bool]):
            enable_incoming_webhooks (Optional[bool]):
            enable_outgoing_webhooks (Optional[bool]):
            enable_commands (Optional[bool]):
            enable_only_admin_integrations (Optional[bool]):
            enable_post_username_override (Optional[bool]):
            enable_post_icon_override (Optional[bool]):
            enable_testing (Optional[bool]):
            enable_developer (Optional[bool]):
            enable_security_fix_alert (Optional[bool]):
            enable_insecure_outgoing_connections (Optional[bool]):
            enable_multifactor_authentication (Optional[bool]):
            enforce_multifactor_authentication (Optional[bool]):
            allow_cors_from (Optional[bool]):
            session_length_web_in_days (Optional[bool]):
            session_length_mobile_in_days (Optional[bool]):
            session_length_sso_in_days (Optional[bool]):
            session_cache_in_minutes (Optional[bool]):
            websocket_secure_port (Optional[bool]):
            websocket_port (Optional[bool]):
            webserver_mode (Optional[bool]):
            enable_custom_emoji (Optional[bool]):
            restrict_custom_emoji_creation (Optional[bool]):
        """

        site_url: Optional[bool] = None
        listen_address: Optional[bool] = None
        connection_security: Optional[bool] = None
        tls_cert_file: Optional[bool] = None
        tls_key_file: Optional[bool] = None
        use_lets_encrypt: Optional[bool] = None
        lets_encrypt_certificate_cache_file: Optional[bool] = None
        forward80_to443: Optional[bool] = None
        read_timeout: Optional[bool] = None
        write_timeout: Optional[bool] = None
        maximum_login_attempts: Optional[bool] = None
        segment_developer_key: Optional[bool] = None
        google_developer_key: Optional[bool] = None
        enable_oauth_service_provider: Optional[bool] = None
        enable_incoming_webhooks: Optional[bool] = None
        enable_outgoing_webhooks: Optional[bool] = None
        enable_commands: Optional[bool] = None
        enable_only_admin_integrations: Optional[bool] = None
        enable_post_username_override: Optional[bool] = None
        enable_post_icon_override: Optional[bool] = None
        enable_testing: Optional[bool] = None
        enable_developer: Optional[bool] = None
        enable_security_fix_alert: Optional[bool] = None
        enable_insecure_outgoing_connections: Optional[bool] = None
        enable_multifactor_authentication: Optional[bool] = None
        enforce_multifactor_authentication: Optional[bool] = None
        allow_cors_from: Optional[bool] = None
        session_length_web_in_days: Optional[bool] = None
        session_length_mobile_in_days: Optional[bool] = None
        session_length_sso_in_days: Optional[bool] = None
        session_cache_in_minutes: Optional[bool] = None
        websocket_secure_port: Optional[bool] = None
        websocket_port: Optional[bool] = None
        webserver_mode: Optional[bool] = None
        enable_custom_emoji: Optional[bool] = None
        restrict_custom_emoji_creation: Optional[bool] = None

    class TeamSettings(BaseConfig):
        """
        Attributes:
            site_name (Optional[bool]):
            max_users_per_team (Optional[bool]):
            enable_team_creation (Optional[bool]):
            enable_user_creation (Optional[bool]):
            enable_open_server (Optional[bool]):
            restrict_creation_to_domains (Optional[bool]):
            enable_custom_brand (Optional[bool]):
            custom_brand_text (Optional[bool]):
            custom_description_text (Optional[bool]):
            restrict_direct_message (Optional[bool]):
            restrict_team_invite (Optional[bool]):
            restrict_public_channel_management (Optional[bool]):
            restrict_private_channel_management (Optional[bool]):
            restrict_public_channel_creation (Optional[bool]):
            restrict_private_channel_creation (Optional[bool]):
            restrict_public_channel_deletion (Optional[bool]):
            restrict_private_channel_deletion (Optional[bool]):
            user_status_away_timeout (Optional[bool]):
            max_channels_per_team (Optional[bool]):
            max_notifications_per_channel (Optional[bool]):
        """

        site_name: Optional[bool] = None
        max_users_per_team: Optional[bool] = None
        enable_team_creation: Optional[bool] = None
        enable_user_creation: Optional[bool] = None
        enable_open_server: Optional[bool] = None
        restrict_creation_to_domains: Optional[bool] = None
        enable_custom_brand: Optional[bool] = None
        custom_brand_text: Optional[bool] = None
        custom_description_text: Optional[bool] = None
        restrict_direct_message: Optional[bool] = None
        restrict_team_invite: Optional[bool] = None
        restrict_public_channel_management: Optional[bool] = None
        restrict_private_channel_management: Optional[bool] = None
        restrict_public_channel_creation: Optional[bool] = None
        restrict_private_channel_creation: Optional[bool] = None
        restrict_public_channel_deletion: Optional[bool] = None
        restrict_private_channel_deletion: Optional[bool] = None
        user_status_away_timeout: Optional[bool] = None
        max_channels_per_team: Optional[bool] = None
        max_notifications_per_channel: Optional[bool] = None

    class SqlSettings(BaseConfig):
        """
        Attributes:
            driver_name (Optional[bool]):
            data_source (Optional[bool]):
            data_source_replicas (Optional[bool]):
            max_idle_conns (Optional[bool]):
            max_open_conns (Optional[bool]):
            trace (Optional[bool]):
            at_rest_encrypt_key (Optional[bool]):
        """

        driver_name: Optional[bool] = None
        data_source: Optional[bool] = None
        data_source_replicas: Optional[bool] = None
        max_idle_conns: Optional[bool] = None
        max_open_conns: Optional[bool] = None
        trace: Optional[bool] = None
        at_rest_encrypt_key: Optional[bool] = None

    class LogSettings(BaseConfig):
        """
        Attributes:
            enable_console (Optional[bool]):
            console_level (Optional[bool]):
            enable_file (Optional[bool]):
            file_level (Optional[bool]):
            file_location (Optional[bool]):
            enable_webhook_debugging (Optional[bool]):
            enable_diagnostics (Optional[bool]):
        """

        enable_console: Optional[bool] = None
        console_level: Optional[bool] = None
        enable_file: Optional[bool] = None
        file_level: Optional[bool] = None
        file_location: Optional[bool] = None
        enable_webhook_debugging: Optional[bool] = None
        enable_diagnostics: Optional[bool] = None

    class PasswordSettings(BaseConfig):
        """
        Attributes:
            minimum_length (Optional[bool]):
            lowercase (Optional[bool]):
            number (Optional[bool]):
            uppercase (Optional[bool]):
            symbol (Optional[bool]):
        """

        minimum_length: Optional[bool] = None
        lowercase: Optional[bool] = None
        number: Optional[bool] = None
        uppercase: Optional[bool] = None
        symbol: Optional[bool] = None

    class FileSettings(BaseConfig):
        """
        Attributes:
            max_file_size (Optional[bool]):
            driver_name (Optional[bool]):
            directory (Optional[bool]):
            enable_public_link (Optional[bool]):
            public_link_salt (Optional[bool]):
            thumbnail_width (Optional[bool]):
            thumbnail_height (Optional[bool]):
            preview_width (Optional[bool]):
            preview_height (Optional[bool]):
            profile_width (Optional[bool]):
            profile_height (Optional[bool]):
            initial_font (Optional[bool]):
            amazon_s3_access_key_id (Optional[bool]):
            amazon_s3_secret_access_key (Optional[bool]):
            amazon_s3_bucket (Optional[bool]):
            amazon_s3_region (Optional[bool]):
            amazon_s3_endpoint (Optional[bool]):
            amazon_s3_ssl (Optional[bool]):
        """

        max_file_size: Optional[bool] = None
        driver_name: Optional[bool] = None
        directory: Optional[bool] = None
        enable_public_link: Optional[bool] = None
        public_link_salt: Optional[bool] = None
        thumbnail_width: Optional[bool] = None
        thumbnail_height: Optional[bool] = None
        preview_width: Optional[bool] = None
        preview_height: Optional[bool] = None
        profile_width: Optional[bool] = None
        profile_height: Optional[bool] = None
        initial_font: Optional[bool] = None
        amazon_s3_access_key_id: Optional[bool] = None
        amazon_s3_secret_access_key: Optional[bool] = None
        amazon_s3_bucket: Optional[bool] = None
        amazon_s3_region: Optional[bool] = None
        amazon_s3_endpoint: Optional[bool] = None
        amazon_s3_ssl: Optional[bool] = None

    class EmailSettings(BaseConfig):
        """
        Attributes:
            enable_sign_up_with_email (Optional[bool]):
            enable_sign_in_with_email (Optional[bool]):
            enable_sign_in_with_username (Optional[bool]):
            send_email_notifications (Optional[bool]):
            require_email_verification (Optional[bool]):
            feedback_name (Optional[bool]):
            feedback_email (Optional[bool]):
            feedback_organization (Optional[bool]):
            smtp_username (Optional[bool]):
            smtp_password (Optional[bool]):
            smtp_server (Optional[bool]):
            smtp_port (Optional[bool]):
            connection_security (Optional[bool]):
            invite_salt (Optional[bool]):
            password_reset_salt (Optional[bool]):
            send_push_notifications (Optional[bool]):
            push_notification_server (Optional[bool]):
            push_notification_contents (Optional[bool]):
            enable_email_batching (Optional[bool]):
            email_batching_buffer_size (Optional[bool]):
            email_batching_interval (Optional[bool]):
        """

        enable_sign_up_with_email: Optional[bool] = None
        enable_sign_in_with_email: Optional[bool] = None
        enable_sign_in_with_username: Optional[bool] = None
        send_email_notifications: Optional[bool] = None
        require_email_verification: Optional[bool] = None
        feedback_name: Optional[bool] = None
        feedback_email: Optional[bool] = None
        feedback_organization: Optional[bool] = None
        smtp_username: Optional[bool] = None
        smtp_password: Optional[bool] = None
        smtp_server: Optional[bool] = None
        smtp_port: Optional[bool] = None
        connection_security: Optional[bool] = None
        invite_salt: Optional[bool] = None
        password_reset_salt: Optional[bool] = None
        send_push_notifications: Optional[bool] = None
        push_notification_server: Optional[bool] = None
        push_notification_contents: Optional[bool] = None
        enable_email_batching: Optional[bool] = None
        email_batching_buffer_size: Optional[bool] = None
        email_batching_interval: Optional[bool] = None

    class RateLimitSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            per_sec (Optional[bool]):
            max_burst (Optional[bool]):
            memory_store_size (Optional[bool]):
            vary_by_remote_addr (Optional[bool]):
            vary_by_header (Optional[bool]):
        """

        enable: Optional[bool] = None
        per_sec: Optional[bool] = None
        max_burst: Optional[bool] = None
        memory_store_size: Optional[bool] = None
        vary_by_remote_addr: Optional[bool] = None
        vary_by_header: Optional[bool] = None

    class PrivacySettings(BaseConfig):
        """
        Attributes:
            show_email_address (Optional[bool]):
            show_full_name (Optional[bool]):
        """

        show_email_address: Optional[bool] = None
        show_full_name: Optional[bool] = None

    class SupportSettings(BaseConfig):
        """
        Attributes:
            terms_of_service_link (Optional[bool]):
            privacy_policy_link (Optional[bool]):
            about_link (Optional[bool]):
            help_link (Optional[bool]):
            report_aproblem_link (Optional[bool]):
            support_email (Optional[bool]):
        """

        terms_of_service_link: Optional[bool] = None
        privacy_policy_link: Optional[bool] = None
        about_link: Optional[bool] = None
        help_link: Optional[bool] = None
        report_aproblem_link: Optional[bool] = None
        support_email: Optional[bool] = None

    class GitLabSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            secret (Optional[bool]):
            id (Optional[bool]):
            scope (Optional[bool]):
            auth_endpoint (Optional[bool]):
            token_endpoint (Optional[bool]):
            user_api_endpoint (Optional[bool]):
        """

        enable: Optional[bool] = None
        secret: Optional[bool] = None
        id: Optional[bool] = None
        scope: Optional[bool] = None
        auth_endpoint: Optional[bool] = None
        token_endpoint: Optional[bool] = None
        user_api_endpoint: Optional[bool] = None

    class GoogleSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            secret (Optional[bool]):
            id (Optional[bool]):
            scope (Optional[bool]):
            auth_endpoint (Optional[bool]):
            token_endpoint (Optional[bool]):
            user_api_endpoint (Optional[bool]):
        """

        enable: Optional[bool] = None
        secret: Optional[bool] = None
        id: Optional[bool] = None
        scope: Optional[bool] = None
        auth_endpoint: Optional[bool] = None
        token_endpoint: Optional[bool] = None
        user_api_endpoint: Optional[bool] = None

    class Office365Settings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            secret (Optional[bool]):
            id (Optional[bool]):
            scope (Optional[bool]):
            auth_endpoint (Optional[bool]):
            token_endpoint (Optional[bool]):
            user_api_endpoint (Optional[bool]):
        """

        enable: Optional[bool] = None
        secret: Optional[bool] = None
        id: Optional[bool] = None
        scope: Optional[bool] = None
        auth_endpoint: Optional[bool] = None
        token_endpoint: Optional[bool] = None
        user_api_endpoint: Optional[bool] = None

    class LdapSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            ldap_server (Optional[bool]):
            ldap_port (Optional[bool]):
            connection_security (Optional[bool]):
            base_dn (Optional[bool]):
            bind_username (Optional[bool]):
            bind_password (Optional[bool]):
            user_filter (Optional[bool]):
            first_name_attribute (Optional[bool]):
            last_name_attribute (Optional[bool]):
            email_attribute (Optional[bool]):
            username_attribute (Optional[bool]):
            nickname_attribute (Optional[bool]):
            id_attribute (Optional[bool]):
            position_attribute (Optional[bool]):
            sync_interval_minutes (Optional[bool]):
            skip_certificate_verification (Optional[bool]):
            query_timeout (Optional[bool]):
            max_page_size (Optional[bool]):
            login_field_name (Optional[bool]):
        """

        enable: Optional[bool] = None
        ldap_server: Optional[bool] = None
        ldap_port: Optional[bool] = None
        connection_security: Optional[bool] = None
        base_dn: Optional[bool] = None
        bind_username: Optional[bool] = None
        bind_password: Optional[bool] = None
        user_filter: Optional[bool] = None
        first_name_attribute: Optional[bool] = None
        last_name_attribute: Optional[bool] = None
        email_attribute: Optional[bool] = None
        username_attribute: Optional[bool] = None
        nickname_attribute: Optional[bool] = None
        id_attribute: Optional[bool] = None
        position_attribute: Optional[bool] = None
        sync_interval_minutes: Optional[bool] = None
        skip_certificate_verification: Optional[bool] = None
        query_timeout: Optional[bool] = None
        max_page_size: Optional[bool] = None
        login_field_name: Optional[bool] = None

    class ComplianceSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            directory (Optional[bool]):
            enable_daily (Optional[bool]):
        """

        enable: Optional[bool] = None
        directory: Optional[bool] = None
        enable_daily: Optional[bool] = None

    class LocalizationSettings(BaseConfig):
        """
        Attributes:
            default_server_locale (Optional[bool]):
            default_client_locale (Optional[bool]):
            available_locales (Optional[bool]):
        """

        default_server_locale: Optional[bool] = None
        default_client_locale: Optional[bool] = None
        available_locales: Optional[bool] = None

    class SamlSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            verify (Optional[bool]):
            encrypt (Optional[bool]):
            idp_url (Optional[bool]):
            idp_descriptor_url (Optional[bool]):
            assertion_consumer_service_url (Optional[bool]):
            idp_certificate_file (Optional[bool]):
            public_certificate_file (Optional[bool]):
            private_key_file (Optional[bool]):
            first_name_attribute (Optional[bool]):
            last_name_attribute (Optional[bool]):
            email_attribute (Optional[bool]):
            username_attribute (Optional[bool]):
            nickname_attribute (Optional[bool]):
            locale_attribute (Optional[bool]):
            position_attribute (Optional[bool]):
            login_button_text (Optional[bool]):
        """

        enable: Optional[bool] = None
        verify: Optional[bool] = None
        encrypt: Optional[bool] = None
        idp_url: Optional[bool] = None
        idp_descriptor_url: Optional[bool] = None
        assertion_consumer_service_url: Optional[bool] = None
        idp_certificate_file: Optional[bool] = None
        public_certificate_file: Optional[bool] = None
        private_key_file: Optional[bool] = None
        first_name_attribute: Optional[bool] = None
        last_name_attribute: Optional[bool] = None
        email_attribute: Optional[bool] = None
        username_attribute: Optional[bool] = None
        nickname_attribute: Optional[bool] = None
        locale_attribute: Optional[bool] = None
        position_attribute: Optional[bool] = None
        login_button_text: Optional[bool] = None

    class NativeAppSettings(BaseConfig):
        """
        Attributes:
            app_download_link (Optional[bool]):
            android_app_download_link (Optional[bool]):
            ios_app_download_link (Optional[bool]):
        """

        app_download_link: Optional[bool] = None
        android_app_download_link: Optional[bool] = None
        ios_app_download_link: Optional[bool] = None

    class ClusterSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            inter_node_listen_address (Optional[bool]):
            inter_node_urls (Optional[bool]):
        """

        enable: Optional[bool] = None
        inter_node_listen_address: Optional[bool] = None
        inter_node_urls: Optional[bool] = None

    class MetricsSettings(BaseConfig):
        """
        Attributes:
            enable (Optional[bool]):
            block_profile_rate (Optional[bool]):
            listen_address (Optional[bool]):
        """

        enable: Optional[bool] = None
        block_profile_rate: Optional[bool] = None
        listen_address: Optional[bool] = None

    class AnalyticsSettings(BaseConfig):
        """
        Attributes:
            max_users_for_statistics (Optional[bool]):
        """

        max_users_for_statistics: Optional[bool] = None

    service_settings: Optional[ServiceSettings] = None
    team_settings: Optional[TeamSettings] = None
    sql_settings: Optional[SqlSettings] = None
    log_settings: Optional[LogSettings] = None
    password_settings: Optional[PasswordSettings] = None
    file_settings: Optional[FileSettings] = None
    email_settings: Optional[EmailSettings] = None
    rate_limit_settings: Optional[RateLimitSettings] = None
    privacy_settings: Optional[PrivacySettings] = None
    support_settings: Optional[SupportSettings] = None
    git_lab_settings: Optional[GitLabSettings] = None
    google_settings: Optional[GoogleSettings] = None
    office365_settings: Optional[Office365Settings] = None
    ldap_settings: Optional[LdapSettings] = None
    compliance_settings: Optional[ComplianceSettings] = None
    localization_settings: Optional[LocalizationSettings] = None
    saml_settings: Optional[SamlSettings] = None
    native_app_settings: Optional[NativeAppSettings] = None
    cluster_settings: Optional[ClusterSettings] = None
    metrics_settings: Optional[MetricsSettings] = None
    analytics_settings: Optional[AnalyticsSettings] = None


class SamlCertificateStatus(BaseConfig):
    """
    Attributes:
        idp_certificate_file (Optional[bool]): Status is good when `true`
        public_certificate_file (Optional[bool]): Status is good when `true`
        private_key_file (Optional[bool]): Status is good when `true`
    """

    idp_certificate_file: Optional[bool] = None
    public_certificate_file: Optional[bool] = None
    private_key_file: Optional[bool] = None


class Compliance(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        create_at (Optional[int]):
        user_id (Optional[str]):
        status (Optional[str]):
        count (Optional[int]):
        desc (Optional[str]):
        type (Optional[str]):
        start_at (Optional[int]):
        end_at (Optional[int]):
        keywords (Optional[str]):
        emails (Optional[str]):
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    user_id: Optional[str] = None
    status: Optional[str] = None
    count: Optional[int] = None
    desc: Optional[str] = None
    type: Optional[str] = None
    start_at: Optional[int] = None
    end_at: Optional[int] = None
    keywords: Optional[str] = None
    emails: Optional[str] = None


class ClusterInfo(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique ID for the node
        version (Optional[str]): The server version the node is on
        config_hash (Optional[str]): The hash of the configuartion file the node
            is using
        internode_url (Optional[str]): The URL used to communicate with those
            node from other nodes
        hostname (Optional[str]): The hostname for this node
        last_ping (Optional[int]): The time of the last ping to this node
        is_alive (Optional[bool]): Whether or not the node is alive and well
    """

    id: Optional[str] = None
    version: Optional[str] = None
    config_hash: Optional[str] = None
    internode_url: Optional[str] = None
    hostname: Optional[str] = None
    last_ping: Optional[int] = None
    is_alive: Optional[bool] = None


class AppError(BaseConfig):
    """
    Attributes:
        status_code (Optional[int]):
        id (Optional[str]):
        message (Optional[str]):
        request_id (Optional[str]):
    """

    status_code: Optional[int] = None
    id: Optional[str] = None
    message: Optional[str] = None
    request_id: Optional[str] = None


class Status(BaseConfig):
    """
    Attributes:
        user_id (Optional[str]):
        status (Optional[str]):
        manual (Optional[bool]):
        last_activity_at (Optional[int]):
    """

    user_id: Optional[str] = None
    status: Optional[str] = None
    manual: Optional[bool] = None
    last_activity_at: Optional[int] = None


class OAuthApp(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The client id of the application
        client_secret (Optional[str]): The client secret of the application
        name (Optional[str]): The name of the client application
        description (Optional[str]): A short description of the application
        icon_url (Optional[str]): A URL to an icon to display with the
            application
        callback_urls (Optional[List[str]]): A list of callback URLs for the
            appliation
        homepage (Optional[str]): A link to the website of the application
        is_trusted (Optional[bool]): Set this to `true` to skip asking users for
            permission
        create_at (Optional[int]): The time of registration for the application
        update_at (Optional[int]): The last time of update for the application
    """

    id: Optional[str] = None
    client_secret: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    callback_urls: Optional[List[str]] = None
    homepage: Optional[str] = None
    is_trusted: Optional[bool] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None


class Job(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique id of the job
        type (Optional[str]): The type of job
        create_at (Optional[int]): The time at which the job was created
        start_at (Optional[int]): The time at which the job was started
        last_activity_at (Optional[int]): The last time at which the job had
            activity
        status (Optional[str]): The status of the job
        progress (Optional[int]): The progress (as a percentage) of the job
        data (Optional[Data]): A freeform data field containing additional
            information about the job
    """

    class Data(BaseConfig):
        """A freeform data field containing additional information about the job"""

    id: Optional[str] = None
    type: Optional[str] = None
    create_at: Optional[int] = None
    start_at: Optional[int] = None
    last_activity_at: Optional[int] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    data: Optional[Data] = None


class UserAccessToken(BaseConfig):
    """
    Attributes:
        id (Optional[str]): Unique identifier for the token
        token (Optional[str]): The token used for authentication
        user_id (Optional[str]): The user the token authenticates for
        description (Optional[str]): A description of the token usage
    """

    id: Optional[str] = None
    token: Optional[str] = None
    user_id: Optional[str] = None
    description: Optional[str] = None


class UserAccessTokenSanitized(BaseConfig):
    """
    Attributes:
        id (Optional[str]): Unique identifier for the token
        user_id (Optional[str]): The user the token authenticates for
        description (Optional[str]): A description of the token usage
        is_active (Optional[bool]): Indicates whether the token is active
    """

    id: Optional[str] = None
    user_id: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class GlobalDataRetentionPolicy(BaseConfig):
    """
    Attributes:
        message_deletion_enabled (Optional[bool]): Indicates whether data
            retention policy deletion of messages is enabled globally.
        file_deletion_enabled (Optional[bool]): Indicates whether data retention
            policy deletion of file attachments is enabled globally.
        message_retention_cutoff (Optional[int]): The current server timestamp
            before which messages should be deleted.
        file_retention_cutoff (Optional[int]): The current server timestamp
            before which files should be deleted.
    """

    message_deletion_enabled: Optional[bool] = None
    file_deletion_enabled: Optional[bool] = None
    message_retention_cutoff: Optional[int] = None
    file_retention_cutoff: Optional[int] = None


class DataRetentionPolicyWithoutId(BaseConfig):
    """
    Attributes:
        display_name (Optional[str]): The display name for this retention
            policy.
        post_duration (Optional[int]): The number of days a message will be
            retained before being deleted by this policy. If this value is less than
            0, the policy has infinite retention (i.e. messages are never deleted).
    """

    display_name: Optional[str] = None
    post_duration: Optional[int] = None


class DataRetentionPolicy(BaseConfig):
    """
    Attributes:
        display_name (Optional[str]): The display name for this retention
            policy.
        post_duration (Optional[int]): The number of days a message will be
            retained before being deleted by this policy. If this value is less than
            0, the policy has infinite retention (i.e. messages are never deleted).
        id (Optional[str]): The ID of this retention policy.
    """

    display_name: Optional[str] = None
    post_duration: Optional[int] = None
    id: Optional[str] = None


class DataRetentionPolicyWithTeamAndChannelCounts(BaseConfig):
    """
    Attributes:
        display_name (Optional[str]): The display name for this retention
            policy.
        post_duration (Optional[int]): The number of days a message will be
            retained before being deleted by this policy. If this value is less than
            0, the policy has infinite retention (i.e. messages are never deleted).
        id (Optional[str]): The ID of this retention policy.
        team_count (Optional[int]): The number of teams to which this policy is
            applied.
        channel_count (Optional[int]): The number of channels to which this
            policy is applied.
    """

    display_name: Optional[str] = None
    post_duration: Optional[int] = None
    id: Optional[str] = None
    team_count: Optional[int] = None
    channel_count: Optional[int] = None


class DataRetentionPolicyWithTeamAndChannelIds(BaseConfig):
    """
    Attributes:
        display_name (Optional[str]): The display name for this retention
            policy.
        post_duration (Optional[int]): The number of days a message will be
            retained before being deleted by this policy. If this value is less than
            0, the policy has infinite retention (i.e. messages are never deleted).
        team_ids (Optional[List[str]]): The IDs of the teams to which this
            policy should be applied.
        channel_ids (Optional[List[str]]): The IDs of the channels to which this
            policy should be applied.
    """

    display_name: Optional[str] = None
    post_duration: Optional[int] = None
    team_ids: Optional[List[str]] = None
    channel_ids: Optional[List[str]] = None


class DataRetentionPolicyCreate(BaseConfig):
    """
    Attributes:
        display_name (Optional[str]): The display name for this retention
            policy.
        post_duration (Optional[int]): The number of days a message will be
            retained before being deleted by this policy. If this value is less than
            0, the policy has infinite retention (i.e. messages are never deleted).
        team_ids (Optional[List[str]]): The IDs of the teams to which this
            policy should be applied.
        channel_ids (Optional[List[str]]): The IDs of the channels to which this
            policy should be applied.
    """

    display_name: Optional[str] = None
    post_duration: Optional[int] = None
    team_ids: Optional[List[str]] = None
    channel_ids: Optional[List[str]] = None


class DataRetentionPolicyForTeam(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]): The team ID.
        post_duration (Optional[int]): The number of days a message will be
            retained before being deleted by this policy.
    """

    team_id: Optional[str] = None
    post_duration: Optional[int] = None


class RetentionPolicyForTeamList(BaseConfig):
    """
    Attributes:
        policies (Optional[List[DataRetentionPolicyForTeam]]): The list of team
            policies.
        total_count (Optional[int]): The total number of team policies.
    """

    policies: Optional[List[DataRetentionPolicyForTeam]] = None
    total_count: Optional[int] = None


class DataRetentionPolicyForChannel(BaseConfig):
    """
    Attributes:
        channel_id (Optional[str]): The channel ID.
        post_duration (Optional[int]): The number of days a message will be
            retained before being deleted by this policy.
    """

    channel_id: Optional[str] = None
    post_duration: Optional[int] = None


class RetentionPolicyForChannelList(BaseConfig):
    """
    Attributes:
        policies (Optional[List[DataRetentionPolicyForChannel]]): The list of
            channel policies.
        total_count (Optional[int]): The total number of channel policies.
    """

    policies: Optional[List[DataRetentionPolicyForChannel]] = None
    total_count: Optional[int] = None


class UserNotifyProps(BaseConfig):
    """
    Attributes:
        email (Optional[bool]): Set to "true" to enable email notifications,
            "false" to disable. Defaults to "true".
        push (Optional[str]): Set to "all" to receive push notifications for all
            activity, "mention" for mentions and direct messages only, and "none" to
            disable. Defaults to "mention".
        desktop (Optional[str]): Set to "all" to receive desktop notifications
            for all activity, "mention" for mentions and direct messages only, and
            "none" to disable. Defaults to "all".
        desktop_sound (Optional[bool]): Set to "true" to enable sound on desktop
            notifications, "false" to disable. Defaults to "true".
        mention_keys (Optional[str]): A comma-separated list of words to count
            as mentions. Defaults to username and @username.
        channel (Optional[bool]): Set to "true" to enable channel-wide
            notifications (@channel, @all, etc.), "false" to disable. Defaults to
            "true".
        first_name (Optional[bool]): Set to "true" to enable mentions for first
            name. Defaults to "true" if a first name is set, "false" otherwise.
    """

    email: Optional[bool] = None
    push: Optional[str] = None
    desktop: Optional[str] = None
    desktop_sound: Optional[bool] = None
    mention_keys: Optional[str] = None
    channel: Optional[bool] = None
    first_name: Optional[bool] = None


class Timezone(BaseConfig):
    """
    Attributes:
        use_automatic_timezone (Optional[bool]): Set to "true" to use the
            browser/system timezone, "false" to set manually. Defaults to "true".
        manual_timezone (Optional[str]): Value when setting manually the
            timezone, i.e. "Europe/Berlin".
        automatic_timezone (Optional[str]): This value is set automatically when
            the "useAutomaticTimezone" is set to "true".
    """

    use_automatic_timezone: Optional[bool] = None
    manual_timezone: Optional[str] = None
    automatic_timezone: Optional[str] = None


class ChannelNotifyProps(BaseConfig):
    """
    Attributes:
        email (Optional[bool]): Set to "true" to enable email notifications,
            "false" to disable, or "default" to use the global user notification
            setting.
        push (Optional[str]): Set to "all" to receive push notifications for all
            activity, "mention" for mentions and direct messages only, "none" to
            disable, or "default" to use the global user notification setting.
        desktop (Optional[str]): Set to "all" to receive desktop notifications
            for all activity, "mention" for mentions and direct messages only,
            "none" to disable, or "default" to use the global user notification
            setting.
        mark_unread (Optional[str]): Set to "all" to mark the channel unread for
            any new message, "mention" to mark unread for new mentions only.
            Defaults to "all".
    """

    email: Optional[bool] = None
    push: Optional[str] = None
    desktop: Optional[str] = None
    mark_unread: Optional[str] = None


class PluginManifest(BaseConfig):
    """
    Attributes:
        id (Optional[str]): Globally unique identifier that represents the
            plugin.
        name (Optional[str]): Name of the plugin.
        description (Optional[str]): Description of what the plugin is and does.
        version (Optional[str]): Version number of the plugin.
        min_server_version (Optional[str]): The minimum Mattermost server
            version required for the plugin.

            Available as server version 5.6.
        backend (Optional[Backend]): Deprecated in Mattermost 5.2 release.
        server (Optional[Server]):
        webapp (Optional[Webapp]):
        settings_schema (Optional[SettingsSchema]): Settings schema used to
            define the System Console UI for the plugin.
    """

    class Backend(BaseConfig):
        """Deprecated in Mattermost 5.2 release.

        Attributes:
            executable (Optional[str]): Path to the executable binary.
        """

        executable: Optional[str] = None

    class Server(BaseConfig):
        """
        Attributes:
            executables (Optional[Executables]): Paths to executable binaries,
                specifying multiple entry points for different platforms when bundled
                together in a single plugin.
            executable (Optional[str]): Path to the executable binary.
        """

        class Executables(BaseConfig):
            """Paths to executable binaries, specifying multiple entry points for
            different platforms when bundled together in a single plugin.

                Attributes:
                    linux_amd64 (Optional[str]):
                    darwin_amd64 (Optional[str]):
                    windows_amd64 (Optional[str]):
            """

            linux_amd64: Optional[str] = None
            darwin_amd64: Optional[str] = None
            windows_amd64: Optional[str] = None

        executables: Optional[Executables] = None
        executable: Optional[str] = None

    class Webapp(BaseConfig):
        """
        Attributes:
            bundle_path (Optional[str]): Path to the webapp JavaScript bundle.
        """

        bundle_path: Optional[str] = None

    class SettingsSchema(BaseConfig):
        """Settings schema used to define the System Console UI for the plugin."""

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    min_server_version: Optional[str] = None
    backend: Optional[Backend] = None
    server: Optional[Server] = None
    webapp: Optional[Webapp] = None
    settings_schema: Optional[SettingsSchema] = None


class MarketplacePlugin(BaseConfig):
    """
    Attributes:
        homepage_url (Optional[str]): URL that leads to the homepage of the
            plugin.
        icon_data (Optional[str]): Base64 encoding of a plugin icon SVG.
        download_url (Optional[str]): URL to download the plugin.
        release_notes_url (Optional[str]): URL that leads to the release notes
            of the plugin.
        labels (Optional[List[str]]): A list of the plugin labels.
        signature (Optional[str]): Base64 encoded signature of the plugin.
        manifest (Optional[PluginManifest]):
        installed_version (Optional[str]): Version number of the already
            installed plugin, if any.
    """

    homepage_url: Optional[str] = None
    icon_data: Optional[str] = None
    download_url: Optional[str] = None
    release_notes_url: Optional[str] = None
    labels: Optional[List[str]] = None
    signature: Optional[str] = None
    manifest: Optional[PluginManifest] = None
    installed_version: Optional[str] = None


class PushNotification(BaseConfig):
    """
    Attributes:
        ack_id (Optional[str]):
        platform (Optional[str]):
        server_id (Optional[str]):
        device_id (Optional[str]):
        post_id (Optional[str]):
        category (Optional[str]):
        sound (Optional[str]):
        message (Optional[str]):
        badge (Optional[float]):
        cont_ava (Optional[float]):
        team_id (Optional[str]):
        channel_id (Optional[str]):
        root_id (Optional[str]):
        channel_name (Optional[str]):
        type (Optional[str]):
        sender_id (Optional[str]):
        sender_name (Optional[str]):
        override_username (Optional[str]):
        override_icon_url (Optional[str]):
        from_webhook (Optional[str]):
        version (Optional[str]):
        is_id_loaded (Optional[bool]):
    """

    ack_id: Optional[str] = None
    platform: Optional[str] = None
    server_id: Optional[str] = None
    device_id: Optional[str] = None
    post_id: Optional[str] = None
    category: Optional[str] = None
    sound: Optional[str] = None
    message: Optional[str] = None
    badge: Optional[float] = None
    cont_ava: Optional[float] = None
    team_id: Optional[str] = None
    channel_id: Optional[str] = None
    root_id: Optional[str] = None
    channel_name: Optional[str] = None
    type: Optional[str] = None
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    override_username: Optional[str] = None
    override_icon_url: Optional[str] = None
    from_webhook: Optional[str] = None
    version: Optional[str] = None
    is_id_loaded: Optional[bool] = None


class PluginStatus(BaseConfig):
    """
    Attributes:
        plugin_id (Optional[str]): Globally unique identifier that represents
            the plugin.
        name (Optional[str]): Name of the plugin.
        description (Optional[str]): Description of what the plugin is and does.
        version (Optional[str]): Version number of the plugin.
        cluster_id (Optional[str]): ID of the cluster in which plugin is running
        plugin_path (Optional[str]): Path to the plugin on the server
        state (Optional[PluginStatusState]): State of the plugin
    """

    plugin_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    cluster_id: Optional[str] = None
    plugin_path: Optional[str] = None
    state: Optional[PluginStatusState] = None


class PluginManifestWebapp(BaseConfig):
    """
    Attributes:
        id (Optional[str]): Globally unique identifier that represents the
            plugin.
        version (Optional[str]): Version number of the plugin.
        webapp (Optional[Webapp]):
    """

    class Webapp(BaseConfig):
        """
        Attributes:
            bundle_path (Optional[str]): Path to the webapp JavaScript bundle.
        """

        bundle_path: Optional[str] = None

    id: Optional[str] = None
    version: Optional[str] = None
    webapp: Optional[Webapp] = None


class Role(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique identifier of the role.
        name (Optional[str]): The unique name of the role, used when assigning
            roles to users/groups in contexts.
        display_name (Optional[str]): The human readable name for the role.
        description (Optional[str]): A human readable description of the role.
        permissions (Optional[List[str]]): A list of the unique names of the
            permissions this role grants.
        scheme_managed (Optional[bool]): indicates if this role is managed by a
            scheme (true), or is a custom stand-alone role (false).
    """

    id: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    scheme_managed: Optional[bool] = None


class Scheme(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique identifier of the scheme.
        name (Optional[str]): The human readable name for the scheme.
        description (Optional[str]): A human readable description of the scheme.
        create_at (Optional[int]): The time at which the scheme was created.
        update_at (Optional[int]): The time at which the scheme was last
            updated.
        delete_at (Optional[int]): The time at which the scheme was deleted.
        scope (Optional[str]): The scope to which this scheme can be applied,
            either "team" or "channel".
        default_team_admin_role (Optional[str]): The id of the default team
            admin role for this scheme.
        default_team_user_role (Optional[str]): The id of the default team user
            role for this scheme.
        default_channel_admin_role (Optional[str]): The id of the default
            channel admin role for this scheme.
        default_channel_user_role (Optional[str]): The id of the default channel
            user role for this scheme.
    """

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    scope: Optional[str] = None
    default_team_admin_role: Optional[str] = None
    default_team_user_role: Optional[str] = None
    default_channel_admin_role: Optional[str] = None
    default_channel_user_role: Optional[str] = None


class TermsOfService(BaseConfig):
    """
    Attributes:
        id (Optional[str]): The unique identifier of the terms of service.
        create_at (Optional[int]): The time at which the terms of service was
            created.
        user_id (Optional[str]): The unique identifier of the user who created
            these terms of service.
        text (Optional[str]): The text of terms of service. Supports Markdown.
    """

    id: Optional[str] = None
    create_at: Optional[int] = None
    user_id: Optional[str] = None
    text: Optional[str] = None


class UserTermsOfService(BaseConfig):
    """
    Attributes:
        user_id (Optional[str]): The unique identifier of the user who performed
            this terms of service action.
        terms_of_service_id (Optional[str]): The unique identifier of the terms
            of service the action was performed on.
        create_at (Optional[int]): The time in milliseconds that this action was
            performed.
    """

    user_id: Optional[str] = None
    terms_of_service_id: Optional[str] = None
    create_at: Optional[int] = None


class PostIdToReactionsMap(BaseMapping):
    """"""

    __root__: Dict[str, List[Reaction]]


class AddOn(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        name (Optional[str]):
        display_name (Optional[str]):
        price_per_seat (Optional[str]):
    """

    id: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    price_per_seat: Optional[str] = None


class PaymentSetupIntent(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        client_secret (Optional[str]):
    """

    id: Optional[str] = None
    client_secret: Optional[str] = None


class PaymentMethod(BaseConfig):
    """
    Attributes:
        type (Optional[str]):
        last_four (Optional[int]):
        exp_month (Optional[int]):
        exp_year (Optional[int]):
        card_brand (Optional[str]):
        name (Optional[str]):
    """

    type: Optional[str] = None
    last_four: Optional[int] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    card_brand: Optional[str] = None
    name: Optional[str] = None


class Address(BaseConfig):
    """
    Attributes:
        city (Optional[str]):
        country (Optional[str]):
        line1 (Optional[str]):
        line2 (Optional[str]):
        postal_code (Optional[str]):
        state (Optional[str]):
    """

    city: Optional[str] = None
    country: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None


class CloudCustomer(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        creator_id (Optional[str]):
        create_at (Optional[int]):
        email (Optional[str]):
        name (Optional[str]):
        num_employees (Optional[str]):
        contact_first_name (Optional[str]):
        contact_last_name (Optional[str]):
        billing_address (Optional[Address]):
        company_address (Optional[Address]):
        payment_method (Optional[PaymentMethod]):
    """

    id: Optional[str] = None
    creator_id: Optional[str] = None
    create_at: Optional[int] = None
    email: Optional[str] = None
    name: Optional[str] = None
    num_employees: Optional[str] = None
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    billing_address: Optional[Address] = None
    company_address: Optional[Address] = None
    payment_method: Optional[PaymentMethod] = None


class Subscription(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        customer_id (Optional[str]):
        product_id (Optional[str]):
        add_ons (Optional[List[str]]):
        start_at (Optional[int]):
        end_at (Optional[int]):
        create_at (Optional[int]):
        seats (Optional[int]):
        dns (Optional[str]):
    """

    id: Optional[str] = None
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    add_ons: Optional[List[str]] = None
    start_at: Optional[int] = None
    end_at: Optional[int] = None
    create_at: Optional[int] = None
    seats: Optional[int] = None
    dns: Optional[str] = None


class SubscriptionStats(BaseConfig):
    """
    Attributes:
        remaining_seats (Optional[int]):
        is_paid_tier (Optional[str]):
    """

    remaining_seats: Optional[int] = None
    is_paid_tier: Optional[str] = None


class InvoiceLineItem(BaseConfig):
    """
    Attributes:
        price_id (Optional[str]):
        total (Optional[int]):
        quantity (Optional[int]):
        price_per_unit (Optional[int]):
        description (Optional[str]):
        metadata (Optional[List[str]]):
    """

    price_id: Optional[str] = None
    total: Optional[int] = None
    quantity: Optional[int] = None
    price_per_unit: Optional[int] = None
    description: Optional[str] = None
    metadata: Optional[List[str]] = None


class Group(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        name (Optional[str]):
        display_name (Optional[str]):
        description (Optional[str]):
        source (Optional[str]):
        remote_id (Optional[str]):
        create_at (Optional[int]):
        update_at (Optional[int]):
        delete_at (Optional[int]):
        has_syncables (Optional[bool]):
    """

    id: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    remote_id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    has_syncables: Optional[bool] = None


class GroupSyncableTeam(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]):
        group_id (Optional[str]):
        auto_add (Optional[bool]):
        create_at (Optional[int]):
        delete_at (Optional[int]):
        update_at (Optional[int]):
    """

    team_id: Optional[str] = None
    group_id: Optional[str] = None
    auto_add: Optional[bool] = None
    create_at: Optional[int] = None
    delete_at: Optional[int] = None
    update_at: Optional[int] = None


class GroupSyncableChannel(BaseConfig):
    """
    Attributes:
        channel_id (Optional[str]):
        group_id (Optional[str]):
        auto_add (Optional[bool]):
        create_at (Optional[int]):
        delete_at (Optional[int]):
        update_at (Optional[int]):
    """

    channel_id: Optional[str] = None
    group_id: Optional[str] = None
    auto_add: Optional[bool] = None
    create_at: Optional[int] = None
    delete_at: Optional[int] = None
    update_at: Optional[int] = None


class GroupSyncableTeams(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]):
        team_display_name (Optional[str]):
        team_type (Optional[str]):
        group_id (Optional[str]):
        auto_add (Optional[bool]):
        create_at (Optional[int]):
        delete_at (Optional[int]):
        update_at (Optional[int]):
    """

    team_id: Optional[str] = None
    team_display_name: Optional[str] = None
    team_type: Optional[str] = None
    group_id: Optional[str] = None
    auto_add: Optional[bool] = None
    create_at: Optional[int] = None
    delete_at: Optional[int] = None
    update_at: Optional[int] = None


class GroupSyncableChannels(BaseConfig):
    """
    Attributes:
        channel_id (Optional[str]):
        channel_display_name (Optional[str]):
        channel_type (Optional[str]):
        team_id (Optional[str]):
        team_display_name (Optional[str]):
        team_type (Optional[str]):
        group_id (Optional[str]):
        auto_add (Optional[bool]):
        create_at (Optional[int]):
        delete_at (Optional[int]):
        update_at (Optional[int]):
    """

    channel_id: Optional[str] = None
    channel_display_name: Optional[str] = None
    channel_type: Optional[str] = None
    team_id: Optional[str] = None
    team_display_name: Optional[str] = None
    team_type: Optional[str] = None
    group_id: Optional[str] = None
    auto_add: Optional[bool] = None
    create_at: Optional[int] = None
    delete_at: Optional[int] = None
    update_at: Optional[int] = None


class ChannelModeratedRole(BaseConfig):
    """
    Attributes:
        value (Optional[bool]):
        enabled (Optional[bool]):
    """

    value: Optional[bool] = None
    enabled: Optional[bool] = None


class ChannelModeratedRolesPatch(BaseConfig):
    """
    Attributes:
        guests (Optional[bool]):
        members (Optional[bool]):
    """

    guests: Optional[bool] = None
    members: Optional[bool] = None


class ChannelModerationPatch(BaseConfig):
    """
    Attributes:
        name (Optional[str]):
        roles (Optional[ChannelModeratedRolesPatch]):
    """

    name: Optional[str] = None
    roles: Optional[ChannelModeratedRolesPatch] = None


class ChannelMemberCountByGroup(BaseConfig):
    """An object describing group member information in a channel

    Attributes:
        group_id (Optional[str]): ID of the group
        channel_member_count (Optional[float]): Total number of group members in
            the channel
        channel_member_timezones_count (Optional[float]): Total number of unique
            timezones for the group members in the channel
    """

    group_id: Optional[str] = None
    channel_member_count: Optional[float] = None
    channel_member_timezones_count: Optional[float] = None


class LDAPGroup(BaseConfig):
    """A LDAP group

    Attributes:
        has_syncables (Optional[bool]):
        mattermost_group_id (Optional[str]):
        primary_key (Optional[str]):
        name (Optional[str]):
    """

    has_syncables: Optional[bool] = None
    mattermost_group_id: Optional[str] = None
    primary_key: Optional[str] = None
    name: Optional[str] = None


class SidebarCategory(BaseConfig):
    """User's sidebar category

    Attributes:
        id (Optional[str]):
        user_id (Optional[str]):
        team_id (Optional[str]):
        display_name (Optional[str]):
        type (Optional[SidebarCategoryType]):
    """

    id: Optional[str] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    display_name: Optional[str] = None
    type: Optional[SidebarCategoryType] = None


class SidebarCategoryWithChannels(BaseConfig):
    """User's sidebar category with it's channels

    Attributes:
        id (Optional[str]):
        user_id (Optional[str]):
        team_id (Optional[str]):
        display_name (Optional[str]):
        type (Optional[SidebarCategoryWithChannelsType]):
        channel_ids (Optional[List[str]]):
    """

    id: Optional[str] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    display_name: Optional[str] = None
    type: Optional[SidebarCategoryWithChannelsType] = None
    channel_ids: Optional[List[str]] = None


class OrderedSidebarCategories(BaseConfig):
    """List of user's categories with their channels

    Attributes:
        order (Optional[List[str]]):
        categories (Optional[List[SidebarCategoryWithChannels]]):
    """

    order: Optional[List[str]] = None
    categories: Optional[List[SidebarCategoryWithChannels]] = None


class Bot(BaseConfig):
    """A bot account

    Attributes:
        user_id (Optional[str]): The user id of the associated user entry.
        create_at (Optional[int]): The time in milliseconds a bot was created
        update_at (Optional[int]): The time in milliseconds a bot was last
            updated
        delete_at (Optional[int]): The time in milliseconds a bot was deleted
        username (Optional[str]):
        display_name (Optional[str]):
        description (Optional[str]):
        owner_id (Optional[str]): The user id of the user that currently owns
            this bot.
    """

    user_id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None


class Server_Busy(BaseConfig):
    """
    Attributes:
        busy (Optional[bool]): True if the server is marked as busy (under high
            load)
        expires (Optional[int]): timestamp - number of seconds since Jan 1, 1970
            UTC.
    """

    busy: Optional[bool] = None
    expires: Optional[int] = None


class GroupWithSchemeAdmin(BaseConfig):
    """group augmented with scheme admin information

    Attributes:
        group (Optional[Group]):
        scheme_admin (Optional[bool]):
    """

    group: Optional[Group] = None
    scheme_admin: Optional[bool] = None


class GroupsAssociatedToChannels(BaseMapping):
    """a map of channel id(s) to the set of groups that constrain the
    corresponding channel in a team

    """

    __root__: Dict[str, List[GroupWithSchemeAdmin]]


class OrphanedRecord(BaseConfig):
    """an object containing information about an orphaned record.

    Attributes:
        parent_id (Optional[str]): the id of the parent relation (table) entry.
        child_id (Optional[str]): the id of the child relation (table) entry.
    """

    parent_id: Optional[str] = None
    child_id: Optional[str] = None


class RelationalIntegrityCheckData(BaseConfig):
    """an object containing the results of a relational integrity check.

    Attributes:
        parent_name (Optional[str]): the name of the parent relation (table).
        child_name (Optional[str]): the name of the child relation (table).
        parent_id_attr (Optional[str]): the name of the attribute (column)
            containing the parent id.
        child_id_attr (Optional[str]): the name of the attribute (column)
            containing the child id.
        records (Optional[List[OrphanedRecord]]): the list of orphaned records
            found.
    """

    parent_name: Optional[str] = None
    child_name: Optional[str] = None
    parent_id_attr: Optional[str] = None
    child_id_attr: Optional[str] = None
    records: Optional[List[OrphanedRecord]] = None


class IntegrityCheckResult(BaseConfig):
    """an object with the result of the integrity check.

    Attributes:
        data (Optional[RelationalIntegrityCheckData]): an object containing the
            results of a relational integrity check.
        err (Optional[str]): a string value set in case of error.
    """

    data: Optional[RelationalIntegrityCheckData] = None
    err: Optional[str] = None


class UploadSession(BaseConfig):
    """an object containing information used to keep track of a file upload.

    Attributes:
        id (Optional[str]): The unique identifier for the upload.
        type (Optional[UploadSessionType]): The type of the upload.
        create_at (Optional[int]): The time the upload was created in
            milliseconds.
        user_id (Optional[str]): The ID of the user performing the upload.
        channel_id (Optional[str]): The ID of the channel to upload to.
        filename (Optional[str]): The name of the file to upload.
        file_size (Optional[int]): The size of the file to upload in bytes.
        file_offset (Optional[int]): The amount of data uploaded in bytes.
    """

    id: Optional[str] = None
    type: Optional[UploadSessionType] = None
    create_at: Optional[int] = None
    user_id: Optional[str] = None
    channel_id: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    file_offset: Optional[int] = None


class Notice(BaseConfig):
    """
    Attributes:
        id (Optional[str]): Notice ID
        sys_admin_only (Optional[bool]): Does this notice apply only to
            sysadmins
        team_admin_only (Optional[bool]): Does this notice apply only to team
            admins
        action (Optional[str]): Optional action to perform on action button
            click. (defaults to closing the notice)
        action_param (Optional[str]): Optional action parameter.
            Example: {"action": "url", actionParam: "/console/some-page"}
        action_text (Optional[str]): Optional override for the action button
            text (defaults to OK)
        description (Optional[str]): Notice content. Use {{Mattermost}} instead
            of plain text to support white-labeling. Text supports Markdown.
        image (Optional[str]): URL of image to display
        title (Optional[str]): Notice title. Use {{Mattermost}} instead of plain
            text to support white-labeling. Text supports Markdown.
    """

    id: Optional[str] = None
    sys_admin_only: Optional[bool] = None
    team_admin_only: Optional[bool] = None
    action: Optional[str] = None
    action_param: Optional[str] = None
    action_text: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    title: Optional[str] = None


class SharedChannel(BaseConfig):
    """
    Attributes:
        id (Optional[str]): Channel id of the shared channel
        team_id (Optional[str]):
        home (Optional[bool]): Is this the home cluster for the shared channel
        readonly (Optional[bool]): Is this shared channel shared as read only
        name (Optional[str]): Channel name as it is shared (may be different
            than original channel name)
        display_name (Optional[str]): Channel display name as it appears locally
        purpose (Optional[str]):
        header (Optional[str]):
        creator_id (Optional[str]): Id of the user that shared the channel
        create_at (Optional[int]): Time in milliseconds that the channel was
            shared
        update_at (Optional[int]): Time in milliseconds that the shared channel
            record was last updated
        remote_id (Optional[str]): Id of the remote cluster where the shared
            channel is homed
    """

    id: Optional[str] = None
    team_id: Optional[str] = None
    home: Optional[bool] = None
    readonly: Optional[bool] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    purpose: Optional[str] = None
    header: Optional[str] = None
    creator_id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    remote_id: Optional[str] = None


class RemoteClusterInfo(BaseConfig):
    """
    Attributes:
        display_name (Optional[str]): The display name for the remote cluster
        create_at (Optional[int]): The time in milliseconds a remote cluster was
            created
        last_ping_at (Optional[int]): The time in milliseconds a remote cluster
            was last pinged successfully
    """

    display_name: Optional[str] = None
    create_at: Optional[int] = None
    last_ping_at: Optional[int] = None


class SystemStatusResponse(BaseConfig):
    """
    Attributes:
        android_latest_version (Optional[str]): Latest Android version supported
        android_min_version (Optional[str]): Minimum Android version supported
        desktop_latest_version (Optional[str]): Latest desktop version supported
        desktop_min_version (Optional[str]): Minimum desktop version supported
        ios_latest_version (Optional[str]): Latest iOS version supported
        ios_min_version (Optional[str]): Minimum iOS version supported
        database_status (Optional[str]): Status of database ("OK" or
            "UNHEALTHY"). Included when get_server_status parameter set.
        filestore_status (Optional[str]): Status of filestore ("OK" or
            "UNHEALTHY"). Included when get_server_status parameter set.
        status (Optional[str]): Status of server ("OK" or "UNHEALTHY"). Included
            when get_server_status parameter set.
    """

    android_latest_version: Optional[str] = None
    android_min_version: Optional[str] = None
    desktop_latest_version: Optional[str] = None
    desktop_min_version: Optional[str] = None
    ios_latest_version: Optional[str] = None
    ios_min_version: Optional[str] = None
    database_status: Optional[str] = None
    filestore_status: Optional[str] = None
    status: Optional[str] = None


class LicenseRenewalLink(BaseConfig):
    """
    Attributes:
        renewal_link (Optional[str]): License renewal link
    """

    renewal_link: Optional[str] = None


class System(BaseConfig):
    """
    Attributes:
        name (Optional[str]): System property name
        value (Optional[str]): System property value
    """

    name: Optional[str] = None
    value: Optional[str] = None


class User(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        create_at (Optional[int]): The time in milliseconds a user was created
        update_at (Optional[int]): The time in milliseconds a user was last
            updated
        delete_at (Optional[int]): The time in milliseconds a user was deleted
        username (Optional[str]):
        first_name (Optional[str]):
        last_name (Optional[str]):
        nickname (Optional[str]):
        email (Optional[str]):
        email_verified (Optional[bool]):
        auth_service (Optional[str]):
        roles (Optional[str]):
        locale (Optional[str]):
        notify_props (Optional[UserNotifyProps]):
        props (Optional[Props]):
        last_password_update (Optional[int]):
        last_picture_update (Optional[int]):
        failed_attempts (Optional[int]):
        mfa_active (Optional[bool]):
        timezone (Optional[Timezone]):
        terms_of_service_id (Optional[str]): ID of accepted terms of service, if
            any. This field is not present if empty.
        terms_of_service_create_at (Optional[int]): The time in milliseconds the
            user accepted the terms of service
    """

    class Props(BaseConfig):
        """"""

    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    auth_service: Optional[str] = None
    roles: Optional[str] = None
    locale: Optional[str] = None
    notify_props: Optional[UserNotifyProps] = None
    props: Optional[Props] = None
    last_password_update: Optional[int] = None
    last_picture_update: Optional[int] = None
    failed_attempts: Optional[int] = None
    mfa_active: Optional[bool] = None
    timezone: Optional[Timezone] = None
    terms_of_service_id: Optional[str] = None
    terms_of_service_create_at: Optional[int] = None


class ChannelMember(BaseConfig):
    """
    Attributes:
        channel_id (Optional[str]):
        user_id (Optional[str]):
        roles (Optional[str]):
        last_viewed_at (Optional[int]): The time in milliseconds the channel was
            last viewed by the user
        msg_count (Optional[int]):
        mention_count (Optional[int]):
        notify_props (Optional[ChannelNotifyProps]):
        last_update_at (Optional[int]): The time in milliseconds the channel
            member was last updated
    """

    channel_id: Optional[str] = None
    user_id: Optional[str] = None
    roles: Optional[str] = None
    last_viewed_at: Optional[int] = None
    msg_count: Optional[int] = None
    mention_count: Optional[int] = None
    notify_props: Optional[ChannelNotifyProps] = None
    last_update_at: Optional[int] = None


class ChannelMemberWithTeamData(BaseConfig):
    """
    Attributes:
        channel_id (Optional[str]):
        user_id (Optional[str]):
        roles (Optional[str]):
        last_viewed_at (Optional[int]): The time in milliseconds the channel was
            last viewed by the user
        msg_count (Optional[int]):
        mention_count (Optional[int]):
        notify_props (Optional[ChannelNotifyProps]):
        last_update_at (Optional[int]): The time in milliseconds the channel
            member was last updated
        team_display_name (Optional[str]): The display name of the team to which
            this channel belongs.
        team_name (Optional[str]): The name of the team to which this channel
            belongs.
        team_update_at (Optional[int]): The time at which the team to which this
            channel belongs was last updated.
    """

    channel_id: Optional[str] = None
    user_id: Optional[str] = None
    roles: Optional[str] = None
    last_viewed_at: Optional[int] = None
    msg_count: Optional[int] = None
    mention_count: Optional[int] = None
    notify_props: Optional[ChannelNotifyProps] = None
    last_update_at: Optional[int] = None
    team_display_name: Optional[str] = None
    team_name: Optional[str] = None
    team_update_at: Optional[int] = None


class ChannelData(BaseConfig):
    """
    Attributes:
        channel (Optional[Channel]):
        member (Optional[ChannelMember]):
    """

    channel: Optional[Channel] = None
    member: Optional[ChannelMember] = None


class FileInfoList(BaseConfig):
    """
    Attributes:
        order (Optional[List[str]]):  Example: ['file_info_id1',
            'file_info_id2'].
        file_infos (Optional[FileInfos]):
        next_file_id (Optional[str]): The ID of next file info. Not omitted when
            empty or not relevant.
        prev_file_id (Optional[str]): The ID of previous file info. Not omitted
            when empty or not relevant.
    """

    class FileInfos(BaseMapping):
        """"""

        __root__: Dict[str, FileInfo]

    order: Optional[List[str]] = None
    file_infos: Optional[FileInfos] = None
    next_file_id: Optional[str] = None
    prev_file_id: Optional[str] = None


class PostMetadataEmbedsItem(BaseConfig):
    """
    Attributes:
        type (Optional[PostMetadataEmbedsItemType]): The type of content that is
            embedded in this point.
        url (Optional[str]): The URL of the embedded content, if one exists.
        data (Optional[Data]): Any additional information about the embedded
            content. Only used at this time to store OpenGraph metadata.
            This field will be null for non-OpenGraph embeds.
    """

    class Data(BaseConfig):
        """Any additional information about the embedded content. Only used at this
        time to store OpenGraph metadata.
        This field will be null for non-OpenGraph embeds.

        """

    type: Optional[PostMetadataEmbedsItemType] = None
    url: Optional[str] = None
    data: Optional[Data] = None


class PostMetadata(BaseConfig):
    """Additional information used to display a post.

    Attributes:
        embeds (Optional[List[PostMetadataEmbedsItem]]): Information about
            content embedded in the post including OpenGraph previews, image link
            previews, and message attachments. This field will be null if the post
            does not contain embedded content.
        emojis (Optional[List[Emoji]]): The custom emojis that appear in this
            point or have been used in reactions to this post. This field will be
            null if the post does not contain custom emojis.
        files (Optional[List[FileInfo]]): The FileInfo objects for any files
            attached to the post. This field will be null if the post does not have
            any file attachments.
        images (Optional[Images]): An object mapping the URL of an external
            image to an object containing the dimensions of that image. This field
            will be null if the post or its embedded content does not reference any
            external images.
        reactions (Optional[List[Reaction]]): Any reactions made to this point.
            This field will be null if no reactions have been made to this post.
    """

    class Images(BaseConfig):
        """An object mapping the URL of an external image to an object containing
        the dimensions of that image. This field will be null if the post or its
        embedded content does not reference any external images.

        """

    embeds: Optional[List[PostMetadataEmbedsItem]] = None
    emojis: Optional[List[Emoji]] = None
    files: Optional[List[FileInfo]] = None
    images: Optional[Images] = None
    reactions: Optional[List[Reaction]] = None


class UserAutocomplete(BaseConfig):
    """
    Attributes:
        users (Optional[List[User]]): A list of users that are the main result
            of the query
        out_of_channel (Optional[List[User]]): A special case list of users
            returned when autocompleting in a specific channel. Omitted when empty
            or not relevant
    """

    users: Optional[List[User]] = None
    out_of_channel: Optional[List[User]] = None


class UserAutocompleteInTeam(BaseConfig):
    """
    Attributes:
        in_team (Optional[List[User]]): A list of user objects in the team
    """

    in_team: Optional[List[User]] = None


class UserAutocompleteInChannel(BaseConfig):
    """
    Attributes:
        in_channel (Optional[List[User]]): A list of user objects in the channel
        out_of_channel (Optional[List[User]]): A list of user objects not in the
            channel
    """

    in_channel: Optional[List[User]] = None
    out_of_channel: Optional[List[User]] = None


class SlackAttachment(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        fallback (Optional[str]):
        color (Optional[str]):
        pretext (Optional[str]):
        author_name (Optional[str]):
        author_link (Optional[str]):
        author_icon (Optional[str]):
        title (Optional[str]):
        title_link (Optional[str]):
        text (Optional[str]):
        fields (Optional[List[SlackAttachmentField]]):
        image_url (Optional[str]):
        thumb_url (Optional[str]):
        footer (Optional[str]):
        footer_icon (Optional[str]):
        timestamp (Optional[str]): The timestamp of the slack attachment, either
            type of string or integer
    """

    id: Optional[str] = None
    fallback: Optional[str] = None
    color: Optional[str] = None
    pretext: Optional[str] = None
    author_name: Optional[str] = None
    author_link: Optional[str] = None
    author_icon: Optional[str] = None
    title: Optional[str] = None
    title_link: Optional[str] = None
    text: Optional[str] = None
    fields: Optional[List[SlackAttachmentField]] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[str] = None
    timestamp: Optional[str] = None


class Product(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        name (Optional[str]):
        description (Optional[str]):
        price_per_seat (Optional[str]):
        add_ons (Optional[List[AddOn]]):
    """

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_seat: Optional[str] = None
    add_ons: Optional[List[AddOn]] = None


class Invoice(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        number (Optional[str]):
        create_at (Optional[int]):
        total (Optional[int]):
        tax (Optional[int]):
        status (Optional[str]):
        period_start (Optional[int]):
        period_end (Optional[int]):
        subscription_id (Optional[str]):
        item (Optional[List[InvoiceLineItem]]):
    """

    id: Optional[str] = None
    number: Optional[str] = None
    create_at: Optional[int] = None
    total: Optional[int] = None
    tax: Optional[int] = None
    status: Optional[str] = None
    period_start: Optional[int] = None
    period_end: Optional[int] = None
    subscription_id: Optional[str] = None
    item: Optional[List[InvoiceLineItem]] = None


class ChannelModeratedRoles(BaseConfig):
    """
    Attributes:
        guests (Optional[ChannelModeratedRole]):
        members (Optional[ChannelModeratedRole]):
    """

    guests: Optional[ChannelModeratedRole] = None
    members: Optional[ChannelModeratedRole] = None


class LDAPGroupsPaged(BaseConfig):
    """A paged list of LDAP groups

    Attributes:
        count (Optional[float]): Total number of groups
        groups (Optional[List[LDAPGroup]]):
    """

    count: Optional[float] = None
    groups: Optional[List[LDAPGroup]] = None


class Post(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        create_at (Optional[int]): The time in milliseconds a post was created
        update_at (Optional[int]): The time in milliseconds a post was last
            updated
        delete_at (Optional[int]): The time in milliseconds a post was deleted
        edit_at (Optional[int]):
        user_id (Optional[str]):
        channel_id (Optional[str]):
        root_id (Optional[str]):
        original_id (Optional[str]):
        message (Optional[str]):
        type (Optional[str]):
        props (Optional[Props]):
        hashtag (Optional[str]):
        file_ids (Optional[List[str]]):
        pending_post_id (Optional[str]):
        metadata (Optional[PostMetadata]): Additional information used to
            display a post.
    """

    class Props(BaseConfig):
        """"""

    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    edit_at: Optional[int] = None
    user_id: Optional[str] = None
    channel_id: Optional[str] = None
    root_id: Optional[str] = None
    original_id: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None
    props: Optional[Props] = None
    hashtag: Optional[str] = None
    file_ids: Optional[List[str]] = None
    pending_post_id: Optional[str] = None
    metadata: Optional[PostMetadata] = None


class PostList(BaseConfig):
    """
    Attributes:
        order (Optional[List[str]]):  Example: ['post_id1', 'post_id12'].
        posts (Optional[Posts]):
        next_post_id (Optional[str]): The ID of next post. Not omitted when
            empty or not relevant.
        prev_post_id (Optional[str]): The ID of previous post. Not omitted when
            empty or not relevant.
    """

    class Posts(BaseMapping):
        """"""

        __root__: Dict[str, Post]

    order: Optional[List[str]] = None
    posts: Optional[Posts] = None
    next_post_id: Optional[str] = None
    prev_post_id: Optional[str] = None


class PostListWithSearchMatches(BaseConfig):
    """
    Attributes:
        order (Optional[List[str]]):  Example: ['post_id1', 'post_id12'].
        posts (Optional[Posts]):
        matches (Optional[Matches]): A mapping of post IDs to a list of matched
            terms within the post. This field will only be populated on servers
            running version 5.1 or greater with Elasticsearch enabled.
             Example: {'post_id1': ['search match 1', 'search match 2']}.
    """

    class Posts(BaseMapping):
        """"""

        __root__: Dict[str, Post]

    class Matches(BaseMapping):
        """A mapping of post IDs to a list of matched terms within the post. This
        field will only be populated on servers running version 5.1 or greater
        with Elasticsearch enabled.

            Example:
                {'post_id1': ['search match 1', 'search match 2']}

        """

        __root__: Dict[str, List[str]]

    order: Optional[List[str]] = None
    posts: Optional[Posts] = None
    matches: Optional[Matches] = None


class CommandResponse(BaseConfig):
    """
    Attributes:
        response_type (Optional[str]): The response type either in_channel or
            ephemeral
        text (Optional[str]):
        username (Optional[str]):
        icon_url (Optional[str]):
        goto_location (Optional[str]):
        attachments (Optional[List[SlackAttachment]]):
    """

    response_type: Optional[str] = None
    text: Optional[str] = None
    username: Optional[str] = None
    icon_url: Optional[str] = None
    goto_location: Optional[str] = None
    attachments: Optional[List[SlackAttachment]] = None


class ChannelModeration(BaseConfig):
    """
    Attributes:
        name (Optional[str]):
        roles (Optional[ChannelModeratedRoles]):
    """

    name: Optional[str] = None
    roles: Optional[ChannelModeratedRoles] = None


class UserThread(BaseConfig):
    """a thread that user is following

    Attributes:
        id (Optional[str]): ID of the post that is this thread's root
        reply_count (Optional[int]): number of replies in this thread
        last_reply_at (Optional[int]): timestamp of the last post to this thread
        last_viewed_at (Optional[int]): timestamp of the last time the user
            viewed this thread
        participants (Optional[List[Post]]): list of users participating in this
            thread. only includes IDs unless 'extended' was set to 'true'
        post (Optional[Post]):
    """

    id: Optional[str] = None
    reply_count: Optional[int] = None
    last_reply_at: Optional[int] = None
    last_viewed_at: Optional[int] = None
    participants: Optional[List[Post]] = None
    post: Optional[Post] = None


class UserThreads(BaseConfig):
    """
    Attributes:
        total (Optional[int]): Total number of threads (used for paging)
        threads (Optional[List[UserThread]]): Array of threads
    """

    total: Optional[int] = None
    threads: Optional[List[UserThread]] = None


class LoginJsonBody(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        login_id (Optional[str]):
        token (Optional[str]):
        device_id (Optional[str]):
        ldap_only (Optional[bool]):
        password (Optional[str]): The password used for email authentication.
    """

    id: Optional[str] = None
    login_id: Optional[str] = None
    token: Optional[str] = None
    device_id: Optional[str] = None
    ldap_only: Optional[bool] = None
    password: Optional[str] = None


class LoginByCwsTokenJsonBody(BaseConfig):
    """
    Attributes:
        login_id (Optional[str]):
        cws_token (Optional[str]):
    """

    login_id: Optional[str] = None
    cws_token: Optional[str] = None


class CreateUserJsonBody(BaseConfig):
    """
    Attributes:
        email (str):
        username (str):
        first_name (Optional[str]):
        last_name (Optional[str]):
        nickname (Optional[str]):
        auth_data (Optional[str]): Service-specific authentication data, such as
            email address.
        auth_service (Optional[str]): The authentication service, one of
            "email", "gitlab", "ldap", "saml", "office365", "google", and "".
        password (Optional[str]): The password used for email authentication.
        locale (Optional[str]):
        props (Optional[Props]):
        notify_props (Optional[UserNotifyProps]):
    """

    class Props(BaseConfig):
        """"""

    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    auth_data: Optional[str] = None
    auth_service: Optional[str] = None
    password: Optional[str] = None
    locale: Optional[str] = None
    props: Optional[Props] = None
    notify_props: Optional[UserNotifyProps] = None


class GetUsersByGroupChannelIdsResponse_200(BaseConfig):
    """
    Attributes:
        channel_id (Optional[List[User]]):
    """

    channel_id: Optional[List[User]] = None


class SearchUsersJsonBody(BaseConfig):
    """
    Attributes:
        term (str): The term to match against username, full name, nickname and
            email
        team_id (Optional[str]): If provided, only search users on this team
        not_in_team_id (Optional[str]): If provided, only search users not on
            this team
        in_channel_id (Optional[str]): If provided, only search users in this
            channel
        not_in_channel_id (Optional[str]): If provided, only search users not in
            this channel. Must specifiy `team_id` when using this option
        in_group_id (Optional[str]): If provided, only search users in this
            group. Must have `manage_system` permission.
        group_constrained (Optional[bool]): When used with `not_in_channel_id`
            or `not_in_team_id`, returns only the users that are allowed to join the
            channel or team based on its group constrains.
        allow_inactive (Optional[bool]): When `true`, include deactivated users
            in the results
        without_team (Optional[bool]): Set this to `true` if you would like to
            search for users that are not on a team. This option takes precendence
            over `team_id`, `in_channel_id`, and `not_in_channel_id`.
        limit (Optional[int]): The maximum number of users to return in the
            results

            __Available as of server version 5.6. Defaults to `100` if not provided
            or on an earlier server version.__
             Default: 100.
    """

    term: str
    team_id: Optional[str] = None
    not_in_team_id: Optional[str] = None
    in_channel_id: Optional[str] = None
    not_in_channel_id: Optional[str] = None
    in_group_id: Optional[str] = None
    group_constrained: Optional[bool] = None
    allow_inactive: Optional[bool] = None
    without_team: Optional[bool] = None
    limit: Optional[int] = 100


class UpdateUserJsonBody(BaseConfig):
    """
    Attributes:
        id (str):
        email (Optional[str]):
        username (Optional[str]):
        first_name (Optional[str]):
        last_name (Optional[str]):
        nickname (Optional[str]):
        locale (Optional[str]):
        position (Optional[str]):
        props (Optional[Props]):
        notify_props (Optional[UserNotifyProps]):
    """

    class Props(BaseConfig):
        """"""

    id: str
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    locale: Optional[str] = None
    position: Optional[str] = None
    props: Optional[Props] = None
    notify_props: Optional[UserNotifyProps] = None


class PatchUserJsonBody(BaseConfig):
    """
    Attributes:
        email (Optional[str]):
        username (Optional[str]):
        first_name (Optional[str]):
        last_name (Optional[str]):
        nickname (Optional[str]):
        locale (Optional[str]):
        position (Optional[str]):
        props (Optional[Props]):
        notify_props (Optional[UserNotifyProps]):
    """

    class Props(BaseConfig):
        """"""

    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    locale: Optional[str] = None
    position: Optional[str] = None
    props: Optional[Props] = None
    notify_props: Optional[UserNotifyProps] = None


class UpdateUserRolesJsonBody(BaseConfig):
    """
    Attributes:
        roles (str):
    """

    roles: str


class UpdateUserActiveJsonBody(BaseConfig):
    """
    Attributes:
        active (bool):
    """

    active: bool


class SetProfileImageMultipartData(BaseConfig):
    """
    Attributes:
        image (File): The image to be uploaded
    """

    image: File

    _file_properties: ClassVar[Set[str]] = set(["image"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class ResetPasswordJsonBody(BaseConfig):
    """
    Attributes:
        code (str): The recovery code
        new_password (str): The new password for the user
    """

    code: str
    new_password: str


class UpdateUserMfaJsonBody(BaseConfig):
    """
    Attributes:
        activate (bool): Use `true` to activate, `false` to deactivate
        code (Optional[str]): The code produced by your MFA client. Required if
            `activate` is true
    """

    activate: bool
    code: Optional[str] = None


class GenerateMfaSecretResponse_200(BaseConfig):
    """
    Attributes:
        secret (Optional[str]): The MFA secret as a string
        qr_code (Optional[str]): A base64 encoded QR code image
    """

    secret: Optional[str] = None
    qr_code: Optional[str] = None


class CheckUserMfaResponse_200(BaseConfig):
    """
    Attributes:
        mfa_required (Optional[bool]): Value will `true` if MFA is active,
            `false` otherwise
    """

    mfa_required: Optional[bool] = None


class CheckUserMfaJsonBody(BaseConfig):
    """
    Attributes:
        login_id (str): The email or username used to login
    """

    login_id: str


class UpdateUserPasswordJsonBody(BaseConfig):
    """
    Attributes:
        new_password (str): The new password for the user
        current_password (Optional[str]): The current password for the user
    """

    new_password: str
    current_password: Optional[str] = None


class SendPasswordResetEmailJsonBody(BaseConfig):
    """
    Attributes:
        email (str): The email of the user
    """

    email: str


class RevokeSessionJsonBody(BaseConfig):
    """
    Attributes:
        session_id (str): The session GUID to revoke.
    """

    session_id: str


class AttachDeviceIdJsonBody(BaseConfig):
    """
    Attributes:
        device_id (str): Mobile device id. For Android prefix the id with
            `android:` and Apple with `apple:`
    """

    device_id: str


class VerifyUserEmailJsonBody(BaseConfig):
    """
    Attributes:
        token (str): The token given to validate the email
    """

    token: str


class SendVerificationEmailJsonBody(BaseConfig):
    """
    Attributes:
        email (str): Email of a user
    """

    email: str


class SwitchAccountTypeResponse_200(BaseConfig):
    """
    Attributes:
        follow_link (Optional[str]): The link for the user to follow to login or
            to complete the account switching when the current service is
            OAuth2/SAML
    """

    follow_link: Optional[str] = None


class SwitchAccountTypeJsonBody(BaseConfig):
    """
    Attributes:
        current_service (str): The service the user currently uses to login
        new_service (str): The service the user will use to login
        email (Optional[str]): The email of the user
        password (Optional[str]): The password used with the current service
        mfa_code (Optional[str]): The MFA code of the current service
        ldap_id (Optional[str]): The LDAP/AD id of the user
    """

    current_service: str
    new_service: str
    email: Optional[str] = None
    password: Optional[str] = None
    mfa_code: Optional[str] = None
    ldap_id: Optional[str] = None


class CreateUserAccessTokenJsonBody(BaseConfig):
    """
    Attributes:
        description (str): A description of the token usage
    """

    description: str


class RevokeUserAccessTokenJsonBody(BaseConfig):
    """
    Attributes:
        token_id (str): The user access token GUID to revoke
    """

    token_id: str


class DisableUserAccessTokenJsonBody(BaseConfig):
    """
    Attributes:
        token_id (str): The personal access token GUID to disable
    """

    token_id: str


class EnableUserAccessTokenJsonBody(BaseConfig):
    """
    Attributes:
        token_id (str): The personal access token GUID to enable
    """

    token_id: str


class SearchUserAccessTokensJsonBody(BaseConfig):
    """
    Attributes:
        term (str): The search term to match against the token id, user id or
            username.
    """

    term: str


class RegisterTermsOfServiceActionJsonBody(BaseConfig):
    """
    Attributes:
        service_terms_id (str): terms of service ID on which the user is acting
            on
        accepted (str): true or false, indicates whether the user accepted or
            rejected the terms of service.
    """

    service_terms_id: str
    accepted: str


class PublishUserTypingJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): The id of the channel to which to direct the typing
            event.
        parent_id (Optional[str]): The optional id of the root post of the
            thread to which the user is replying. If unset, the typing event is
            directed at the entire channel.
    """

    channel_id: str
    parent_id: Optional[str] = None


class MigrateAuthToLdapJsonBody(BaseConfig):
    """
    Attributes:
        from_ (str): The current authentication type for the matched users.
        match_field (str): Foreign user field name to match.
        force (bool):
    """

    from_: str
    match_field: str
    force: bool


class MigrateAuthToSamlJsonBody(BaseConfig):
    """
    Attributes:
        from_ (str): The current authentication type for the matched users.
        matches (Matches): Users map.
        auto (bool):
    """

    class Matches(BaseConfig):
        """Users map."""

    from_: str
    matches: Matches
    auto: bool


class UpdateUserStatusJsonBody(BaseConfig):
    """
    Attributes:
        user_id (str): User ID
        status (str): User status, can be `online`, `away`, `offline` and `dnd`
        dnd_end_time (Optional[int]): Time in epoch seconds at which a dnd
            status would be unset.
    """

    user_id: str
    status: str
    dnd_end_time: Optional[int] = None


class UpdateUserCustomStatusJsonBody(BaseConfig):
    """
    Attributes:
        emoji (str): Any emoji
        text (str): Any custom status text
        duration (Optional[str]): Duration of custom status, can be
            `thirty_minutes`, `one_hour`, `four_hours`, `today`, `this_week` or
            `date_and_time`
        expires_at (Optional[str]): The time at which custom status should be
            expired. It should be in ISO format.
    """

    emoji: str
    text: str
    duration: Optional[str] = None
    expires_at: Optional[str] = None


class RemoveRecentCustomStatusJsonBody(BaseConfig):
    """
    Attributes:
        emoji (str): Any emoji
        text (str): Any custom status text
        duration (str): Duration of custom status, can be `thirty_minutes`,
            `one_hour`, `four_hours`, `today`, `this_week` or `date_and_time`
        expires_at (str): The time at which custom status should be expired. It
            should be in ISO format.
    """

    emoji: str
    text: str
    duration: str
    expires_at: str


class PostUserRecentCustomStatusDeleteJsonBody(BaseConfig):
    """
    Attributes:
        emoji (str): Any emoji
        text (str): Any custom status text
        duration (str): Duration of custom status, can be `thirty_minutes`,
            `one_hour`, `four_hours`, `today`, `this_week` or `date_and_time`
        expires_at (str): The time at which custom status should be expired. It
            should be in ISO format.
    """

    emoji: str
    text: str
    duration: str
    expires_at: str


class CreateTeamJsonBody(BaseConfig):
    """
    Attributes:
        name (str): Unique handler for a team, will be present in the team URL
        display_name (str): Non-unique UI name for the team
        type (str): `'O'` for open, `'I'` for invite only
    """

    name: str
    display_name: str
    type: str


class UpdateTeamJsonBody(BaseConfig):
    """
    Attributes:
        id (str):
        display_name (str):
        description (str):
        company_name (str):
        allowed_domains (str):
        invite_id (str):
        allow_open_invite (str):
    """

    id: str
    display_name: str
    description: str
    company_name: str
    allowed_domains: str
    invite_id: str
    allow_open_invite: str


class PatchTeamJsonBody(BaseConfig):
    """
    Attributes:
        display_name (Optional[str]):
        description (Optional[str]):
        company_name (Optional[str]):
        invite_id (Optional[str]):
        allow_open_invite (Optional[bool]):
    """

    display_name: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    invite_id: Optional[str] = None
    allow_open_invite: Optional[bool] = None


class UpdateTeamPrivacyJsonBody(BaseConfig):
    """
    Attributes:
        privacy (str): Team privacy setting: 'O' for a public (open) team, 'I'
            for a private (invitation only) team
    """

    privacy: str


class SearchTeamsResponse_200(BaseConfig):
    """
    Attributes:
        teams (Optional[List[Team]]): The teams that matched the query.
        total_count (Optional[float]): The total number of results, regardless
            of page and per_page requested.
    """

    teams: Optional[List[Team]] = None
    total_count: Optional[float] = None


class SearchTeamsJsonBody(BaseConfig):
    """
    Attributes:
        term (Optional[str]): The search term to match against the name or
            display name of teams
        page (Optional[str]): The page number to return, if paginated. If this
            parameter is not present with the `per_page` parameter then the results
            will be returned un-paged.
        per_page (Optional[str]): The number of entries to return per page, if
            paginated. If this parameter is not present with the `page` parameter
            then the results will be returned un-paged.
        allow_open_invite (Optional[bool]): Filters results to teams where
            `allow_open_invite` is set to true or false, excludes group constrained
            channels if this filter option is passed.
            If this filter option is not passed then the query will remain
            unchanged.

            Minimum Server Version:
                5.28
        group_constrained (Optional[bool]): Filters results to teams where
            `group_constrained` is set to true or false, returns the union of
            results when used with `allow_open_invite`
            If the filter option is not passed then the query will remain unchanged.

            Minimum Server Version:
                5.28
        exclude_policy_constrained (Optional[bool]): If set to true, only teams
            which do not have a granular retention policy assigned to them will be
            returned. The `sysconsole_read_compliance_data_retention` permission is
            required to use this parameter.

            Minimum Server Version:
                5.35
    """

    term: Optional[str] = None
    page: Optional[str] = None
    per_page: Optional[str] = None
    allow_open_invite: Optional[bool] = None
    group_constrained: Optional[bool] = None
    exclude_policy_constrained: Optional[bool] = False


class AddTeamMemberJsonBody(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]):
        user_id (Optional[str]):
    """

    team_id: Optional[str] = None
    user_id: Optional[str] = None


class SetTeamIconMultipartData(BaseConfig):
    """
    Attributes:
        image (File): The image to be uploaded
    """

    image: File

    _file_properties: ClassVar[Set[str]] = set(["image"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class UpdateTeamMemberRolesJsonBody(BaseConfig):
    """
    Attributes:
        roles (str):
    """

    roles: str


class UpdateTeamMemberSchemeRolesJsonBody(BaseConfig):
    """
    Attributes:
        scheme_admin (bool):
        scheme_user (bool):
    """

    scheme_admin: bool
    scheme_user: bool


class InviteGuestsToTeamJsonBody(BaseConfig):
    """
    Attributes:
        emails (List[str]): List of emails
        channels (List[str]): List of channel ids
        message (Optional[str]): Message to include in the invite
    """

    emails: List[str]
    channels: List[str]
    message: Optional[str] = None


class ImportTeamResponse_200(BaseConfig):
    """
    Attributes:
        results (Optional[str]):
    """

    results: Optional[str] = None


class ImportTeamMultipartData(BaseConfig):
    """
    Attributes:
        file (File): A file to be uploaded in zip format.
        filesize (int): The size of the zip file to be imported.
        import_from (str): String that defines from which application the team
            was exported to be imported into Mattermost.
    """

    file: File
    filesize: int
    import_from: str

    _file_properties: ClassVar[Set[str]] = set(["file"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class GetTeamInviteInfoResponse_200(BaseConfig):
    """
    Attributes:
        id (Optional[str]):
        name (Optional[str]):
        display_name (Optional[str]):
        description (Optional[str]):
    """

    id: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None


class UpdateTeamSchemeJsonBody(BaseConfig):
    """
    Attributes:
        scheme_id (str): The ID of the scheme.
    """

    scheme_id: str


class CreateChannelJsonBody(BaseConfig):
    """
    Attributes:
        team_id (str): The team ID of the team to create the channel on
        name (str): The unique handle for the channel, will be present in the
            channel URL
        display_name (str): The non-unique UI name for the channel
        type (str): 'O' for a public channel, 'P' for a private channel
        purpose (Optional[str]): A short description of the purpose of the
            channel
        header (Optional[str]): Markdown-formatted text to display in the header
            of the channel
    """

    team_id: str
    name: str
    display_name: str
    type: str
    purpose: Optional[str] = None
    header: Optional[str] = None


class SearchAllChannelsResponse_200(BaseConfig):
    """
    Attributes:
        channels (Optional[List[Channel]]): The channels that matched the query.
        total_count (Optional[float]): The total number of results, regardless
            of page and per_page requested.
    """

    channels: Optional[List[Channel]] = None
    total_count: Optional[float] = None


class SearchGroupChannelsJsonBody(BaseConfig):
    """
    Attributes:
        term (str): The search term to match against the members' usernames of
            the group channels
    """

    term: str


class UpdateChannelJsonBody(BaseConfig):
    """
    Attributes:
        id (str): The channel's id, not updatable
        name (Optional[str]): The unique handle for the channel, will be present
            in the channel URL
        display_name (Optional[str]): The non-unique UI name for the channel
        purpose (Optional[str]): A short description of the purpose of the
            channel
        header (Optional[str]): Markdown-formatted text to display in the header
            of the channel
    """

    id: str
    name: Optional[str] = None
    display_name: Optional[str] = None
    purpose: Optional[str] = None
    header: Optional[str] = None


class PatchChannelJsonBody(BaseConfig):
    """
    Attributes:
        name (Optional[str]): The unique handle for the channel, will be present
            in the channel URL
        display_name (Optional[str]): The non-unique UI name for the channel
        purpose (Optional[str]): A short description of the purpose of the
            channel
        header (Optional[str]): Markdown-formatted text to display in the header
            of the channel
    """

    name: Optional[str] = None
    display_name: Optional[str] = None
    purpose: Optional[str] = None
    header: Optional[str] = None


class UpdateChannelPrivacyJsonBody(BaseConfig):
    """
    Attributes:
        privacy (str): Channel privacy setting: 'O' for a public channel, 'P'
            for a private channel
    """

    privacy: str


class MoveChannelJsonBody(BaseConfig):
    """
    Attributes:
        team_id (str):
        force (Optional[bool]): Remove members those are not member of target
            team before moving the channel.
    """

    team_id: str
    force: Optional[bool] = None


class SearchChannelsJsonBody(BaseConfig):
    """
    Attributes:
        term (str): The search term to match against the name or display name of
            channels
    """

    term: str


class SearchArchivedChannelsJsonBody(BaseConfig):
    """
    Attributes:
        term (str): The search term to match against the name or display name of
            archived channels
    """

    term: str


class AddChannelMemberJsonBody(BaseConfig):
    """
    Attributes:
        user_id (str): The ID of user to add into the channel
        post_root_id (Optional[str]): The ID of root post where link to add
            channel member originates
    """

    user_id: str
    post_root_id: Optional[str] = None


class UpdateChannelRolesJsonBody(BaseConfig):
    """
    Attributes:
        roles (str):
    """

    roles: str


class UpdateChannelMemberSchemeRolesJsonBody(BaseConfig):
    """
    Attributes:
        scheme_admin (bool):
        scheme_user (bool):
    """

    scheme_admin: bool
    scheme_user: bool


class ViewChannelResponse_200(BaseConfig):
    """
    Attributes:
        status (Optional[str]): Value should be "OK" if successful
        last_viewed_at_times (Optional[LastViewedAtTimes]): A JSON object
            mapping channel IDs to the channel view times
    """

    class LastViewedAtTimes(BaseConfig):
        """A JSON object mapping channel IDs to the channel view times"""

    status: Optional[str] = None
    last_viewed_at_times: Optional[LastViewedAtTimes] = None


class ViewChannelJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): The channel ID that is being viewed. Use a blank
            string to indicate that all channels have lost focus.
        prev_channel_id (Optional[str]): The channel ID of the previous channel,
            used when switching channels. Providing this ID will cause push
            notifications to clear on the channel being switched to.
    """

    channel_id: str
    prev_channel_id: Optional[str] = None


class UpdateChannelSchemeJsonBody(BaseConfig):
    """
    Attributes:
        scheme_id (str): The ID of the scheme.
    """

    scheme_id: str


class CreatePostJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): The channel ID to post in
        message (str): The message contents, can be formatted with Markdown
        root_id (Optional[str]): The post ID to comment on
        file_ids (Optional[List[str]]): A list of file IDs to associate with the
            post. Note that posts are limited to 5 files maximum. Please use
            additional posts for more files.
        props (Optional[Props]): A general JSON property bag to attach to the
            post
    """

    class Props(BaseConfig):
        """A general JSON property bag to attach to the post"""

    channel_id: str
    message: str
    root_id: Optional[str] = None
    file_ids: Optional[List[str]] = None
    props: Optional[Props] = None


class CreatePostEphemeralJsonBody(BaseConfig):
    """
    Attributes:
        user_id (str): The target user id for the ephemeral post
        post (Post): Post object to create
    """

    class Post(BaseConfig):
        """Post object to create

        Attributes:
            channel_id (str): The channel ID to post in
            message (str): The message contents, can be formatted with Markdown
        """

        channel_id: str
        message: str

    user_id: str
    post: Post


class UpdatePostJsonBody(BaseConfig):
    """
    Attributes:
        id (str): ID of the post to update
        is_pinned (Optional[bool]): Set to `true` to pin the post to the channel
            it is in
        message (Optional[str]): The message text of the post
        has_reactions (Optional[bool]): Set to `true` if the post has reactions
            to it
        props (Optional[str]): A general JSON property bag to attach to the post
    """

    id: str
    is_pinned: Optional[bool] = None
    message: Optional[str] = None
    has_reactions: Optional[bool] = None
    props: Optional[str] = None


class PatchPostJsonBody(BaseConfig):
    """
    Attributes:
        is_pinned (Optional[bool]): Set to `true` to pin the post to the channel
            it is in
        message (Optional[str]): The message text of the post
        file_ids (Optional[List[str]]): The list of files attached to this post
        has_reactions (Optional[bool]): Set to `true` if the post has reactions
            to it
        props (Optional[str]): A general JSON property bag to attach to the post
    """

    is_pinned: Optional[bool] = None
    message: Optional[str] = None
    file_ids: Optional[List[str]] = None
    has_reactions: Optional[bool] = None
    props: Optional[str] = None


class SearchPostsJsonBody(BaseConfig):
    """
    Attributes:
        terms (str): The search terms as inputed by the user. To search for
            posts from a user include `from:someusername`, using a user's username.
            To search in a specific channel include `in:somechannel`, using the
            channel name (not the display name).
        is_or_search (bool): Set to true if an Or search should be performed vs
            an And search.
        time_zone_offset (Optional[int]): Offset from UTC of user timezone for
            date searches.
        include_deleted_channels (Optional[bool]): Set to true if deleted
            channels should be included in the search. (archived channels)
        page (Optional[int]): The page to select. (Only works with
            Elasticsearch)
        per_page (Optional[int]): The number of posts per page. (Only works with
            Elasticsearch)
             Default: 60.
    """

    terms: str
    is_or_search: bool
    time_zone_offset: Optional[int] = 0
    include_deleted_channels: Optional[bool] = None
    page: Optional[int] = 0
    per_page: Optional[int] = 60


class UploadFileResponse_201(BaseConfig):
    """
    Attributes:
        file_infos (Optional[List[FileInfo]]): A list of file metadata that has
            been stored in the database
        client_ids (Optional[List[str]]): A list of the client_ids that were
            provided in the request
    """

    file_infos: Optional[List[FileInfo]] = None
    client_ids: Optional[List[str]] = None


class UploadFileMultipartData(BaseConfig):
    """
    Attributes:
        files (Optional[File]): A file to be uploaded
        channel_id (Optional[str]): The ID of the channel that this file will be
            uploaded to
        client_ids (Optional[str]): A unique identifier for the file that will
            be returned in the response
    """

    files: Optional[File] = None
    channel_id: Optional[str] = None
    client_ids: Optional[str] = None

    _file_properties: ClassVar[Set[str]] = set(["files"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class GetFileLinkResponse_200(BaseConfig):
    """
    Attributes:
        link (Optional[str]):
    """

    link: Optional[str] = None


class SearchFilesMultipartData(BaseConfig):
    """
    Attributes:
        terms (str): The search terms as inputed by the user. To search for
            files from a user include `from:someusername`, using a user's username.
            To search in a specific channel include `in:somechannel`, using the
            channel name (not the display name). To search for specific extensions
            included `ext:extension`.
        is_or_search (bool): Set to true if an Or search should be performed vs
            an And search.
        time_zone_offset (Optional[int]): Offset from UTC of user timezone for
            date searches.
        include_deleted_channels (Optional[bool]): Set to true if deleted
            channels should be included in the search. (archived channels)
        page (Optional[int]): The page to select. (Only works with
            Elasticsearch)
        per_page (Optional[int]): The number of posts per page. (Only works with
            Elasticsearch)
             Default: 60.
    """

    terms: str
    is_or_search: bool
    time_zone_offset: Optional[int] = 0
    include_deleted_channels: Optional[bool] = None
    page: Optional[int] = 0
    per_page: Optional[int] = 60

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude_none=True)


class CreateUploadJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): The ID of the channel to upload to.
        filename (str): The name of the file to upload.
        file_size (int): The size of the file to upload in bytes.
    """

    channel_id: str
    filename: str
    file_size: int


class UploadDataFormData(BaseConfig):
    """"""


class CreateJobJsonBody(BaseConfig):
    """
    Attributes:
        type (str): The type of job to create
        data (Optional[Data]): An object containing any additional data required
            for this job type
    """

    class Data(BaseConfig):
        """An object containing any additional data required for this job type"""

    type: str
    data: Optional[Data] = None


class TestSiteURLJsonBody(BaseConfig):
    """
    Attributes:
        site_url (str): The Site URL to test
    """

    site_url: str


class MigrateConfigJsonBody(BaseConfig):
    """
    Attributes:
        from_ (Optional[str]):
        to (Optional[str]):
    """

    from_: Optional[str] = None
    to: Optional[str] = None


class UploadLicenseFileMultipartData(BaseConfig):
    """
    Attributes:
        license (File): The license to be uploaded
    """

    license: File

    _file_properties: ClassVar[Set[str]] = set(["license"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class RequestTrialLicenseJsonBody(BaseConfig):
    """
    Attributes:
        users (int): Number of users requested (20% extra is going to be added)
    """

    users: int


class PostLogResponse_200(BaseConfig):
    """"""


class PostLogJsonBody(BaseConfig):
    """
    Attributes:
        level (str): The error level, ERROR or DEBUG
        message (str): Message to send to the server logs
    """

    level: str
    message: str


class UpgradeToEnterpriseStatusResponse_200(BaseConfig):
    """
    Attributes:
        percentage (Optional[int]): Current percentage of the upgrade
        error (Optional[str]): Error happened during the upgrade
    """

    percentage: Optional[int] = None
    error: Optional[str] = None


class SendWarnMetricAckJsonBody(BaseConfig):
    """
    Attributes:
        force_ack (Optional[bool]): Flag which determines if the ack for the
            metric warning should be directly stored (without trying to send email
            first) or not
    """

    force_ack: Optional[bool] = None


class CreateEmojiMultipartData(BaseConfig):
    """
    Attributes:
        image (File): A file to be uploaded
        emoji (str): A JSON object containing a `name` field with the name of
            the emoji and a `creator_id` field with the id of the authenticated
            user.
    """

    image: File
    emoji: str

    _file_properties: ClassVar[Set[str]] = set(["image"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class SearchEmojiJsonBody(BaseConfig):
    """
    Attributes:
        term (str): The term to match against the emoji name.
        prefix_only (Optional[str]): Set to only search for names starting with
            the search term.
    """

    term: str
    prefix_only: Optional[str] = None


class CreateIncomingWebhookJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): The ID of a public channel or private group that
            receives the webhook payloads.
        user_id (Optional[str]): The ID of the owner of the webhook if different
            than the requester. Required for [local
            mode](https://docs.mattermost.com/administration/mmctl-cli-
            tool.html#local-mode).
        display_name (Optional[str]): The display name for this incoming webhook
        description (Optional[str]): The description for this incoming webhook
        username (Optional[str]): The username this incoming webhook will post
            as.
        icon_url (Optional[str]): The profile picture this incoming webhook will
            use when posting.
    """

    channel_id: str
    user_id: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    username: Optional[str] = None
    icon_url: Optional[str] = None


class UpdateIncomingWebhookJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): The ID of a public channel or private group that
            receives the webhook payloads.
        display_name (str): The display name for this incoming webhook
        description (str): The description for this incoming webhook
        hook_id (Optional[str]): Incoming webhook GUID
        username (Optional[str]): The username this incoming webhook will post
            as.
        icon_url (Optional[str]): The profile picture this incoming webhook will
            use when posting.
    """

    channel_id: str
    display_name: str
    description: str
    hook_id: Optional[str] = None
    username: Optional[str] = None
    icon_url: Optional[str] = None


class CreateOutgoingWebhookJsonBody(BaseConfig):
    """
    Attributes:
        team_id (str): The ID of the team that the webhook watchs
        display_name (str): The display name for this outgoing webhook
        trigger_words (List[str]): List of words for the webhook to trigger on
        callback_urls (List[str]): The URLs to POST the payloads to when the
            webhook is triggered
        channel_id (Optional[str]): The ID of a public channel that the webhook
            watchs
        creator_id (Optional[str]): The ID of the owner of the webhook if
            different than the requester. Required in [local
            mode](https://docs.mattermost.com/administration/mmctl-cli-
            tool.html#local-mode).
        description (Optional[str]): The description for this outgoing webhook
        trigger_when (Optional[int]): When to trigger the webhook, `0` when a
            trigger word is present at all and `1` if the message starts with a
            trigger word
        content_type (Optional[str]): The format to POST the data in, either
            `application/json` or `application/x-www-form-urlencoded`
             Default: 'application/x-www-form-urlencoded'.
    """

    team_id: str
    display_name: str
    trigger_words: List[str]
    callback_urls: List[str]
    channel_id: Optional[str] = None
    creator_id: Optional[str] = None
    description: Optional[str] = None
    trigger_when: Optional[int] = None
    content_type: Optional[str] = "application/x-www-form-urlencoded"


class UpdateOutgoingWebhookJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): The ID of a public channel or private group that
            receives the webhook payloads.
        display_name (str): The display name for this incoming webhook
        description (str): The description for this incoming webhook
        hook_id (Optional[str]): Outgoing webhook GUID
    """

    channel_id: str
    display_name: str
    description: str
    hook_id: Optional[str] = None


class UploadSamlIdpCertificateMultipartData(BaseConfig):
    """
    Attributes:
        certificate (File): The IDP certificate file
    """

    certificate: File

    _file_properties: ClassVar[Set[str]] = set(["certificate"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class UploadSamlPublicCertificateMultipartData(BaseConfig):
    """
    Attributes:
        certificate (File): The public certificate file
    """

    certificate: File

    _file_properties: ClassVar[Set[str]] = set(["certificate"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class UploadSamlPrivateCertificateMultipartData(BaseConfig):
    """
    Attributes:
        certificate (File): The private key file
    """

    certificate: File

    _file_properties: ClassVar[Set[str]] = set(["certificate"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class ResetSamlAuthDataToEmailResponse_200(BaseConfig):
    """
    Attributes:
        num_affected (Optional[int]): The number of users whose AuthData field
            was reset.
    """

    num_affected: Optional[int] = None


class ResetSamlAuthDataToEmailJsonBody(BaseConfig):
    """
    Attributes:
        include_deleted (Optional[bool]): Whether to include deleted users.
        dry_run (Optional[bool]): If set to true, the number of users who would
            be affected is returned.
        user_ids (Optional[List[str]]): If set to a non-empty array, then users
            whose IDs are not in the array will be excluded.
    """

    include_deleted: Optional[bool] = False
    dry_run: Optional[bool] = False
    user_ids: Optional[List[str]] = None


class MigrateIdLdapJsonBody(BaseConfig):
    """
    Attributes:
        to_attribute (str): New IdAttribute value
    """

    to_attribute: str


class UploadLdapPublicCertificateMultipartData(BaseConfig):
    """
    Attributes:
        certificate (File): The public certificate file
    """

    certificate: File

    _file_properties: ClassVar[Set[str]] = set(["certificate"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class UploadLdapPrivateCertificateMultipartData(BaseConfig):
    """
    Attributes:
        certificate (File): The private key file
    """

    certificate: File

    _file_properties: ClassVar[Set[str]] = set(["certificate"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class PatchGroupJsonBody(BaseConfig):
    """
    Attributes:
        name (Optional[str]):
        display_name (Optional[str]):
        description (Optional[str]):
    """

    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None


class PatchGroupSyncableForTeamJsonBody(BaseConfig):
    """
    Attributes:
        auto_add (Optional[bool]):
    """

    auto_add: Optional[bool] = None


class PatchGroupSyncableForChannelJsonBody(BaseConfig):
    """
    Attributes:
        auto_add (Optional[bool]):
    """

    auto_add: Optional[bool] = None


class GetGroupUsersResponse_200(BaseConfig):
    """
    Attributes:
        members (Optional[List[User]]):
        total_member_count (Optional[int]):
    """

    members: Optional[List[User]] = None
    total_member_count: Optional[int] = None


class GetGroupStatsResponse_200(BaseConfig):
    """
    Attributes:
        group_id (Optional[str]):
        total_member_count (Optional[int]):
    """

    group_id: Optional[str] = None
    total_member_count: Optional[int] = None


class GetGroupsAssociatedToChannelsByTeamResponse_200(BaseConfig):
    """"""


class UploadBrandImageMultipartData(BaseConfig):
    """
    Attributes:
        image (File): The image to be uploaded
    """

    image: File

    _file_properties: ClassVar[Set[str]] = set(["image"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class CreateCommandJsonBody(BaseConfig):
    """
    Attributes:
        team_id (str): Team ID to where the command should be created
        method (str): `'P'` for post request, `'G'` for get request
        trigger (str): Activation word to trigger the command
        url (str): The URL that the command will make the request
    """

    team_id: str
    method: str
    trigger: str
    url: str


class MoveCommandJsonBody(BaseConfig):
    """
    Attributes:
        team_id (Optional[str]): Destination teamId
    """

    team_id: Optional[str] = None


class RegenCommandTokenResponse_200(BaseConfig):
    """
    Attributes:
        token (Optional[str]): The new token
    """

    token: Optional[str] = None


class ExecuteCommandJsonBody(BaseConfig):
    """
    Attributes:
        channel_id (str): Channel Id where the command will execute
        command (str): The slash command to execute
    """

    channel_id: str
    command: str


class CreateOAuthAppJsonBody(BaseConfig):
    """
    Attributes:
        name (str): The name of the client application
        description (str): A short description of the application
        callback_urls (List[str]): A list of callback URLs for the appliation
        homepage (str): A link to the website of the application
        icon_url (Optional[str]): A URL to an icon to display with the
            application
        is_trusted (Optional[bool]): Set this to `true` to skip asking users for
            permission
    """

    name: str
    description: str
    callback_urls: List[str]
    homepage: str
    icon_url: Optional[str] = None
    is_trusted: Optional[bool] = None


class UpdateOAuthAppJsonBody(BaseConfig):
    """
    Attributes:
        id (str): The id of the client application
        name (str): The name of the client application
        description (str): A short description of the application
        callback_urls (List[str]): A list of callback URLs for the appliation
        homepage (str): A link to the website of the application
        icon_url (Optional[str]): A URL to an icon to display with the
            application
        is_trusted (Optional[bool]): Set this to `true` to skip asking users for
            permission. It will be set to false if value is not provided.
    """

    id: str
    name: str
    description: str
    callback_urls: List[str]
    homepage: str
    icon_url: Optional[str] = None
    is_trusted: Optional[bool] = None


class GetDataRetentionPoliciesCountResponse_200(BaseConfig):
    """
    Attributes:
        total_count (Optional[int]): The number of granular retention policies.
    """

    total_count: Optional[int] = None


class SearchTeamsForRetentionPolicyJsonBody(BaseConfig):
    """
    Attributes:
        term (Optional[str]): The search term to match against the name or
            display name of teams
    """

    term: Optional[str] = None


class SearchChannelsForRetentionPolicyJsonBody(BaseConfig):
    """
    Attributes:
        term (Optional[str]): The string to search in the channel name, display
            name, and purpose.
        team_ids (Optional[List[str]]): Filters results to channels belonging to
            the given team ids
        public (Optional[bool]): Filters results to only return Public / Open
            channels, can be used in conjunction with `private` to return both
            `public` and `private` channels
        private (Optional[bool]): Filters results to only return Private
            channels, can be used in conjunction with `public` to return both
            `private` and `public` channels
        deleted (Optional[bool]): Filters results to only return deleted /
            archived channels
    """

    term: Optional[str] = None
    team_ids: Optional[List[str]] = None
    public: Optional[bool] = None
    private: Optional[bool] = None
    deleted: Optional[bool] = None


class GetPluginsResponse_200(BaseConfig):
    """
    Attributes:
        active (Optional[List[PluginManifest]]):
        inactive (Optional[List[PluginManifest]]):
    """

    active: Optional[List[PluginManifest]] = None
    inactive: Optional[List[PluginManifest]] = None


class UploadPluginMultipartData(BaseConfig):
    """
    Attributes:
        plugin (File): The plugin image to be uploaded
        force (Optional[str]): Set to 'true' to overwrite a previously installed
            plugin with the same ID, if any
    """

    plugin: File
    force: Optional[str] = None

    _file_properties: ClassVar[Set[str]] = set(["plugin"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class InstallMarketplacePluginJsonBody(BaseConfig):
    """
    Attributes:
        id (str): The ID of the plugin to install.
        version (str): The version of the plugin to install.
    """

    id: str
    version: str


class PatchRoleJsonBody(BaseConfig):
    """
    Attributes:
        permissions (Optional[List[str]]): The permissions the role should
            grant.
    """

    permissions: Optional[List[str]] = None


class CreateSchemeJsonBody(BaseConfig):
    """
    Attributes:
        name (str): The name of the scheme
        scope (str): The scope of the scheme ("team" or "channel")
        description (Optional[str]): The description of the scheme
    """

    name: str
    scope: str
    description: Optional[str] = None


class PatchSchemeJsonBody(BaseConfig):
    """
    Attributes:
        name (Optional[str]): The human readable name of the scheme
        description (Optional[str]): The description of the scheme
    """

    name: Optional[str] = None
    description: Optional[str] = None


class OpenGraphJsonBody(BaseConfig):
    """
    Attributes:
        url (str): The URL to get Open Graph Metadata.
    """

    url: str


class DialogElementsItem(BaseConfig):
    """"""


class OpenInteractiveDialogJsonBody(BaseConfig):
    """
    Attributes:
        trigger_id (str): Trigger ID provided by other action
        url (str): The URL to send the submitted dialog payload to
        dialog (Dialog): Post object to create
    """

    class Dialog(BaseConfig):
        """Post object to create

        Attributes:
            title (str): Title of the dialog
            elements (List[DialogElementsItem]): Input elements, see
                https://docs.mattermost.com/developer/interactive-dialogs.html#elements
            callback_id (Optional[str]): Set an ID that will be included when the
                dialog is submitted
            introduction_text (Optional[str]): Markdown formatted introductory
                paragraph
            submit_label (Optional[str]): Label on the submit button
            notify_on_cancel (Optional[bool]): Set true to receive payloads when
                user cancels a dialog
            state (Optional[str]): Set some state to be echoed back with the dialog
                submission
        """

        title: str
        elements: List[DialogElementsItem]
        callback_id: Optional[str] = None
        introduction_text: Optional[str] = None
        submit_label: Optional[str] = None
        notify_on_cancel: Optional[bool] = None
        state: Optional[str] = None

    trigger_id: str
    url: str
    dialog: Dialog


class SubmitInteractiveDialogJsonBody(BaseConfig):
    """
    Attributes:
        url (str): The URL to send the submitted dialog payload to
        channel_id (str): Channel ID the user submitted the dialog from
        team_id (str): Team ID the user submitted the dialog from
        submission (Submission): String map where keys are element names and
            values are the element input values
        callback_id (Optional[str]): Callback ID sent when the dialog was opened
        state (Optional[str]): State sent when the dialog was opened
        cancelled (Optional[bool]): Set to true if the dialog was cancelled
    """

    class Submission(BaseConfig):
        """String map where keys are element names and values are the element input
        values

        """

    url: str
    channel_id: str
    team_id: str
    submission: Submission
    callback_id: Optional[str] = None
    state: Optional[str] = None
    cancelled: Optional[bool] = None


class CreateBotJsonBody(BaseConfig):
    """
    Attributes:
        username (str):
        display_name (Optional[str]):
        description (Optional[str]):
    """

    username: str
    display_name: Optional[str] = None
    description: Optional[str] = None


class PatchBotJsonBody(BaseConfig):
    """
    Attributes:
        username (str):
        display_name (Optional[str]):
        description (Optional[str]):
    """

    username: str
    display_name: Optional[str] = None
    description: Optional[str] = None


class SetBotIconImageMultipartData(BaseConfig):
    """
    Attributes:
        image (File): SVG icon image to be uploaded
    """

    image: File

    _file_properties: ClassVar[Set[str]] = set(["image"])
    """Properties to be included into `files` parameter of request"""

    class Config:
        """Pydantic configuration for the model

        :meta private:
        """

        arbitrary_types_allowed = True

    def get_files(self):
        """Get the `files` attributes for the request from the model

        :meta private:
        """
        response = {}
        file_props = self.dict(include=self._file_properties, exclude_none=True)
        for name, value in file_props.items():
            if isinstance(value, dict):
                response.update(value)
            else:
                response.update({name: value})
        return response

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude=self._file_properties, exclude_none=True)


class ConvertBotToUserJsonBody(BaseConfig):
    """
    Attributes:
        email (Optional[str]):
        username (Optional[str]):
        password (Optional[str]):
        first_name (Optional[str]):
        last_name (Optional[str]):
        nickname (Optional[str]):
        locale (Optional[str]):
        position (Optional[str]):
        props (Optional[Props]):
        notify_props (Optional[UserNotifyProps]):
    """

    class Props(BaseConfig):
        """"""

    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    locale: Optional[str] = None
    position: Optional[str] = None
    props: Optional[Props] = None
    notify_props: Optional[UserNotifyProps] = None


class ConfirmCustomerPaymentMultipartData(BaseConfig):
    """
    Attributes:
        stripe_setup_intent_id (Optional[str]):
    """

    stripe_setup_intent_id: Optional[str] = None

    def get_data(self):
        """Get the `data` attributes for the request from the model

        :meta private:
        """
        return self.dict(exclude_none=True)


class UpdateCloudCustomerJsonBody(BaseConfig):
    """
    Attributes:
        name (Optional[str]):
        email (Optional[str]):
        contact_first_name (Optional[str]):
        contact_last_name (Optional[str]):
        num_employees (Optional[str]):
    """

    name: Optional[str] = None
    email: Optional[str] = None
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    num_employees: Optional[str] = None
