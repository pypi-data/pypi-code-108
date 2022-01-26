# can't use nested enums, so even though it hurts my soul...nested classes it is
class ENDPOINTS():
    class GET_BEATMAPS():
        EXTENSION = "get_beatmaps"
        REQUIRED = [["since"], ["s"], ["b"], ["u"], ["h"]]
        POSSIBLE = ["since", "s", "b", "u", "h", "type", "m", "a", "limit", "mods"]

    class GET_MATCH():
        EXTENSION = "get_match"
        REQUIRED = [["mp"]]
        POSSIBLE = ["mp"]

    class GET_SCORES():
        EXTENSION = "get_scores"
        REQUIRED = [["b"]]
        POSSIBLE = ["b", "u", "m", "mods", "type", "limit"]

    class GET_REPLAY():
        EXTENSION = "get_replay"
        REQUIRED = [["b", "u"], ["s"]]
        POSSIBLE = ["b", "u", "m", "s", "type", "mods"]

    class GET_USER():
        EXTENSION = "get_user"
        REQUIRED = [["u"]]
        POSSIBLE = ["u", "m", "type", "event_days"]

    class GET_USER_BEST():
        EXTENSION = "get_user_best"
        REQUIRED = [["u"]]
        POSSIBLE = ["m", "u", "limit", "type"]

    class GET_USER_RECENT():
        EXTENSION = "get_user_recent"
        REQUIRED = [["u"]]
        POSSIBLE = ["m", "u", "limit", "type"]
