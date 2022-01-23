class Events:
    class NewDevlog:
        def name(self): return "NEW_DEVLOG"
    class NewPost:
        def name(self): return "NEW_POST"
    class NewReply:
        def name(self): return "NEW_REPLY"
    class NewLike:
        def name(self): return "NEW_LIKE"
    class NewFollower:
        def name(self): return "NEW_FOLLOWER"
    class UnFollowed:
        def name(self): return "UNFOLLOWED"
    class NewEdit:
        def name(self): return "NEW_EDIT"
    class Unlike:
        def name(self): return "UNLIKE"