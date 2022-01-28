import hek

# request tor session
tor_session = hek.tor.get_session()

# tor get request
result = tor_session.get("http://httpbin.org/ip").text

# print result
print(result)