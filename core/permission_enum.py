from enum import Enum


class PermissionEnum(Enum):
    add_reactions = "add_reactions"
    administrator = "administrator"
    attach_files = "attach_files"
    ban_members = "ban_members"
    change_nickname = "change_nickname"
    connect = "connect"
    create_instant_invite = "create_instant_invite"
    create_private_threads = "create_private_threads"
    create_public_threads = "create_public_threads"
    deafen_members = "deafen_members"
    embed_links = "embed_links"
    external_emojis = "external_emojis"
    external_stickers = "external_stickers"
    kick_members = "kick_members"
    manage_channels = "manage_channels"
    manage_emojis = "manage_emojis"
    manage_emojis_and_stickers = "manage_emojis_and_stickers"
    manage_events = "manage_events"
    manage_guild = "manage_guild"
    manage_messages = "manage_messages"
    manage_nicknames = "manage_nicknames"
    manage_permissions = "manage_permissions"
    manage_roles = "manage_roles"
    manage_threads = "manage_threads"
    manage_webhooks = "manage_webhooks"
    mention_everyone = "mention_everyone"
    moderate_members = "moderate_members"
    move_members = "move_members"
    mute_members = "mute_members"
    priority_speaker = "priority_speaker"
    read_message_history = "read_message_history"
    read_messages = "read_messages"
    request_to_speak = "request_to_speak"
    send_messages = "send_messages"
    send_messages_in_threads = "send_messages_in_threads"
    send_tts_messages = "send_tts_messages"
    speak = "speak"
    start_embedded_activities = "start_embedded_activities"
    stream = "stream"
    use_application_commands = "use_application_commands"
    use_external_emojis = "use_external_emojis"
    use_external_stickers = "use_external_stickers"
    use_slash_commands = "use_slash_commands"
    use_voice_activation = "use_voice_activation"
    view_audit_log = "view_audit_log"
    view_channel = "view_channel"
    view_guild_insights = "view_guild_insights"
