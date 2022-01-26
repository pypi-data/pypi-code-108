from bs4 import BeautifulSoup as BS
import re
import requests
from time import sleep

class StaticSpell:
    def __init__(self, url):
        self.url = url
        self.request = requests.get(url)
        self.status_code = self.request.status_code
        self.slug = self.get_slug()

        # Raise error if status_code is not 200
        if self.status_code != 200:
            assert Exception(f"Your request was rejected. Status Code: {self.status_code}\nSee https://developer.mozilla.org/en-US/docs/Web/HTTP/Status for more details.")
        self.rune = BS(self.request.content, 'html.parser')

    def __repr__(self):
        return f'Static Spell casted on {self.url}'

    def __str__(self):
        return f'Static Spell casted on {self.url}'


    # For selecting first item based on CSS selector.
    def select(self, css_selector):
        return self.rune.select_one(css_selector)


    # For selecting first item based on CSS selector.
    def selectAll(self, css_selector):
        return self.rune.select(css_selector)
    
    # Wait a certain amount of seconds to continue code.
    def wait(self, time_interval):
        sleep(time_interval)

    # Gets the end name of the URL
    def get_slug(self):
        slug = re.sub(r'/$', r'', self.url)
        # Get portion of URL after last forward slash.
        slug =  re.sub(r'^.+?/([^/]+?)$', r'\1', slug)
        # Remove any hashes
        slug = re.sub(r'#[^#]+?$', r'', slug)
        # Remove any queries
        slug = re.sub(r'\?.+?$', r'', slug)
        return slug
