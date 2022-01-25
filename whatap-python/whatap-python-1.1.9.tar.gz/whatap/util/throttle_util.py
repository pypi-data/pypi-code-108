from whatap.conf.configure import Configure as conf
from whatap.pack.pack_enum import EventLevel
from whatap.net.udp_session import UdpSession
from whatap.util.hash_util import HashUtil
from whatap.util.int_set import IntSet
import whatap.util.string_util as string_util
from whatap.util.ip_util import IPUtil
from whatap.net.packet_type_enum import PacketTypeEnum

def getThrottleStringToHashSet(value, deli):
    intset = IntSet()
    if value is not None:
        vv = string_util.tokenizer(value, deli)
        if vv is None:
            return intset
        for x in vv:
            intset.put(HashUtil.hash(x))

    return intset

def getThrottleIP(value, deli):
    intset = IntSet()
    if value is not None:
        vv = string_util.tokenizer(value, deli)
        if not vv :
            return intset
        for x in vv:
            ip = IPUtil.toInt(x)
            if ip != 0:
                intset.put(ip)

    return intset

def getThrottleIgnorePrefixl(value, deli):
    strset = set()
    if value:
        vv = StringUtil.tokenizer(value, deli)
        if not vv:
            return []
        for x in vv:
            if x:
                strset.add(x)

    return list(strset)


passingUrlSet = getThrottleStringToHashSet(conf.throttle_passing_url, ",")
passingPrefix = getThrottleIgnorePrefixl(conf.throttle_passing_url_prefix, ",")
blockingUrlSet = getThrottleStringToHashSet(conf.throttle_blocking_url, ",")
blockingIPSet = getThrottleIP(conf.throttle_blocking_ip, ",")

blocking_enabled = blockingUrlSet.size() > 0 or blockingIPSet.size() > 0

def getHash():
    k1 = string_util.trimEmpty(conf.throttle_passing_url)
    k2 = string_util.trimEmpty(conf.throttle_passing_url_prefix)
    k3 = string_util.trimEmpty(conf.throttle_blocking_url)
    k4 = string_util.trimEmpty(conf.throttle_blocking_ip)
    return hash(k1) ^ hash(k2) ^ hash(k3) ^ hash(k4)


def isblocking(str_ip, path):
    remote_ip = IPUtil.toInt(str_ip)
    if not blocking_enabled:
        return False
    if blockingIPSet.contains(remote_ip):
        return True
    urlhash = HashUtil.hashFromString(path)
    if blockingUrlSet.contains(urlhash):
        return True
    return False

def sendrejectevent(ctx, path, ip):
    pathHash = HashUtil.hashFromString(path)
    datas = ("REJECTED_URL", EventLevel.WARNING,
             "Rejected " + path,
             pathHash,
             path,
             ip,
    )
    UdpSession.send_packet(PacketTypeEnum.EVENT, ctx, datas)
    
valueHash = 0
def updateConfig():
    global passingUrlSet, passingPrefix, blockingUrlSet, blockingIPSet, blocking_enabled, ignoreContext, ignoreDomain, valueHash
    newHash = getHash()
    if valueHash != newHash:
        passingUrlSet = getThrottleStringToHashSet(conf.throttle_passing_url, ",")
        passingPrefix = getThrottleIgnorePrefixl(conf.throttle_passing_url_prefix, ",")
        blockingUrlSet = getThrottleStringToHashSet(conf.throttle_blocking_url, ",")
        blockingIPSet = getThrottleIP(conf.throttle_blocking_ip, ",")

        blocking_enabled = len(blockingUrlSet) > 0 or len(blockingIPSet) > 0

        ignoreContext = StringUtil.tokenizer(conf.throttle_blocking_ignore_context, ",")
        ignoreDomain = getThrottleStringToHashSet(conf.throttle_blocking_ignore_domain, ",")

        valueHash = getHash()
conf.addObserver(updateConfig)
