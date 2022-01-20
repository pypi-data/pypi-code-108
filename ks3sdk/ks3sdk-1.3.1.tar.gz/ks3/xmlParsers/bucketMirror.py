class BucketMirror(object):
    def __init__(self, use_default_robots=None, async_mirror_rule=None, sync_mirror_rules=None):
        self.version = "V3"
        self.use_default_robots = use_default_robots
        self.async_mirror_rule = async_mirror_rule
        self.sync_mirror_rules = sync_mirror_rules

    def keys(self):
        return ('version', 'use_default_robots', 'async_mirror_rule', 'sync_mirror_rules')

    def __getitem__(self, item):
        if item == 'async_mirror_rule':
            return dict(getattr(self, item))
        if item == 'sync_mirror_rules':
            rules_dict = []
            for value in getattr(self, item):
                rules_dict.append(dict(value))
            return rules_dict
        return getattr(self, item)


class SavingSetting(object):
    def __init__(self, acl=None):
        self.acl = acl


class AsyncMirrorRule(object):
    def __init__(self, mirror_urls=[], saving_setting=None):
        self.mirror_urls = mirror_urls
        self.saving_setting = saving_setting

    @classmethod
    def rule_with_acl(cls, mirror_urls=[], saving_setting_acl=None):
        saving_setting = SavingSetting(acl=saving_setting_acl)
        return cls(mirror_urls=mirror_urls, saving_setting=saving_setting)

    def keys(self):
        return ('mirror_urls', 'saving_setting')

    def __getitem__(self, item):
        if item == 'saving_setting':
            return getattr(self, item).__dict__
        return getattr(self, item)


class SyncMirrorRules(object):
    def __init__(self, match_condition=None, mirror_url=None, mirror_request_setting=None, saving_setting=None):
        self.saving_setting = saving_setting
        self.mirror_request_setting = mirror_request_setting
        self.mirror_url = mirror_url
        self.match_condition = match_condition

    @classmethod
    def rules_with_prefix_acl(cls, key_prefixes=None, mirror_url=None, mirror_request_setting=None, saving_setting_acl=None):
        saving_setting = SavingSetting(acl=saving_setting_acl)
        match_condition = MatchCondition(key_prefixes=key_prefixes)
        return cls(match_condition=match_condition, mirror_url=mirror_url, mirror_request_setting=mirror_request_setting, saving_setting=saving_setting)

    def keys(self):
        return ('saving_setting', 'mirror_request_setting', 'mirror_url', 'match_condition')

    def __getitem__(self, item):
        if item == 'mirror_request_setting':
            return dict(getattr(self, item))
        if item == 'saving_setting' or item == 'match_condition':
            return getattr(self, item).__dict__
        return getattr(self, item)

class MirrorRequestSetting(object):
    def __init__(self, pass_query_string=None, follow3xx=None, header_setting=None):
        self.pass_query_string = pass_query_string
        self.follow3xx = follow3xx
        self.header_setting = header_setting

    def keys(self):
        return ('pass_query_string', 'follow3xx', 'header_setting')

    def __getitem__(self, item):
        if item == 'header_setting':
            return dict(getattr(self, item))
        return getattr(self, item)

class HeaderSetting(object):
    def __init__(self, set_headers=[], remove_headers=[], pass_all=None, pass_headers=[]):
        self.set_headers = set_headers
        self.remove_headers = remove_headers
        self.pass_all = pass_all
        self.pass_headers = pass_headers

    def keys(self):
        return ('set_headers', 'remove_headers', 'pass_all', 'pass_headers')

    def __getitem__(self, item):
        return getattr(self, item)

# 回源条件
class MatchCondition(object):
    def __init__(self, http_codes=["404"], key_prefixes=""):
        self.http_codes = http_codes
        self.key_prefixes = key_prefixes