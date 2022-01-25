from hek import system

# new file path
path = "dog.jpg"
# file url
url = "https://example/dog_picure.jpg"
# download content
result = system.download_content(url=url, path=path)
# print result
print(result)