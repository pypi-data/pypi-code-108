import requests
import bs4

class Forum:
    def __init__(self, url):
        if not "://" in str(url):
            print("No protocol specified for XenGet; defaulting to https://")
            url = "https://" + str(url)
        self.url = url
    
    def get_member(self, id):
        return self.Member(self, id)
    
    class Member():
        def __init__(self, forum, id):
            self.id = int(id)
            self.forum = forum

        def get_avatar(self):
            if self.id > 999:
                member_parent_dir = str(self.id)[:-3] + "/"
            else:
                member_parent_dir = ""
            image = requests.get(f"{self.forum.url}/data/avatars/o/{member_parent_dir}{str(self.id)}.jpg", allow_redirects=True)
            return image.content

        def get_banner(self):
            if self.id > 999:
                member_parent_dir = str(self.id)[:-3] + "/"
            else:
                member_parent_dir = ""
            image = requests.get(f"{self.forum.url}/data/profile_banners/l/{member_parent_dir}{str(self.id)}.jpg", allow_redirects=True)
            return image.content

        def get_username(self):
            page = requests.get(f"{self.forum.url}/members/{str(self.id)}", allow_redirects=True).content
            soup = bs4.BeautifulSoup(page, 'html.parser')
            username = soup.find('span', {"class": "username"})
            if not username == None: username = username.text
            return username

        def get_joindate(self):
            page = requests.get(f"{self.forum.url}/members/{str(self.id)}", allow_redirects=True).content
            soup = bs4.BeautifulSoup(page, 'html.parser')
            joindate = soup.find('time', {"class": "u-dt"})
            if not joindate == None: joindate = joindate.text
            return joindate