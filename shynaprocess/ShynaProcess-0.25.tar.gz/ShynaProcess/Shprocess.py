import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet
from google_speech import Speech
from nltk.tokenize import sent_tokenize
import requests
import json
import nltk
import random
import time
from Shynatime import ShTime
import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re
import math
from math import radians
from ShynaDatabase import Shdatabase
from googlesearch import search
import wikipedia


# noinspection PyUnusedLocal
class ShynaJokes:
    """
    Use Rapid API- jokes API
    URL: https://rapidapi.com/Sv443/api/jokeapi-v2/
    There is no limitation but there are chances of repetition. stay alert.
    There are below method to use:
    shyna_random_jokes : any random jokes with no filter whatsoever.
    shyna_joke_contains: takes one parameter 'contains_string'. It will return any random jokes with that string
    contained in it.
    shyna_programming_joke : Random jokes based on programming.
    shyna_pun_joke : Random jokes pun intended.
    shyna_spooky_joke: Random jokes on ghosts.
    shyna_christmas_joke: Random Christmas jokes.
     """
    joke = ""
    status = False
    headers = {
        'x-rapidapi-host': "jokeapi-v2.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }

    def shyna_random_jokes(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                for key, value in response.items():
                    if response['type'] == 'twopart':
                        self.joke = response['setup'] + "\n" + response['delivery']
                    else:
                        self.joke = response['joke']
                    self.status = True
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_joke_contains(self, contains_string):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

        querystring = {"format": "json", "contains": str(contains_string)}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_programming_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/programming"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_pun_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/pun"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_spooky_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/spooky"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke

    def shyna_christmas_joke(self):
        url = "https://jokeapi-v2.p.rapidapi.com/joke/christmas"

        querystring = {"format": "json"}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if not response['error']:
                    for key, value in response.items():
                        if response['type'] == 'twopart':
                            self.joke = response['setup'] + "\n" + response['delivery']
                        else:
                            self.joke = response['joke']
                    self.status = True
                else:
                    self.status = False
        except Exception as e:
            print(e)
            return False
        finally:
            return self.joke


# noinspection PyUnusedLocal
class ShynaGreetings:
    """
    I am using a Message API. The messages are filter as per the categories.
    ['Love','quotes','friendship','Good night','Good morning','funny','Birthday','Sad','Sweet','Random']

    API URL: https://rapidapi.com/ajith/api/messages/
    There are no limitation in use, but sometimes it doesn't return a response, in such case False will be returned.

    Below methods available:
    greet_good_morning
    greet_good_night
    greet_friend_ship_day
    greet_birthday
    greet_love
    greet_quotes
    greet_funny
    greet_sweet
    greet_custom: provide from any above category.
    """
    msg = ""
    status = False
    headers = {
        'x-rapidapi-host': "ajith-messages.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }

    def greet_good_morning(self):
        """Send Good morning message suggestion"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Good morning'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_good_night(self):
        """Send Good night messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Good night'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_friend_ship_day(self):
        """Send Friend-Ship day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'friendship'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_birthday(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Birthday'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_love(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Love'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_quotes(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'quotes'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_funny(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'funny'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_sweet(self):
        """Send Birthday day messages suggestions"""
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": 'Sweet'}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg

    def greet_custom(self, query):
        url = "https://ajith-messages.p.rapidapi.com/getMsgs"
        querystring = {"category": query}
        try:
            while self.status is False:
                response = requests.request("GET", url, headers=self.headers, params=querystring)
                response = response.__dict__
                response = response["_content"].decode('utf-8')
                response = json.loads(response)
                if response['Message']:
                    self.status = True
                    for key, values in response.items():
                        self.msg = response['Message']
                else:
                    self.status = False
        except Exception as e:
            print(e)
            self.msg = False
        finally:
            return self.msg


# noinspection PyUnusedLocal
class ShynaSentenceAnalyzer:
    """Using nltk.sentiment.vader
    sentence_analysis : provide sentence to check the polarity. There is nothing like neutral either it is positive or
    negative sentence.
    This will help in case running a command and there is a follow-up question.  Response the way you like as per the
    sentence polarity it will be decided to perform the command or not.

    We have below method:
    sentence_analysis: Provide sentence to this method
    """
    sia = SentimentIntensityAnalyzer()
    pos_score = 0
    neg_score = 0
    neu_score = 0
    comp_score = 0
    antonyms = []
    status = True

    def analyse_sentence_polarity(self, item):
        self.pos_score = self.sia.polarity_scores(text=item)['pos']
        self.neg_score = self.sia.polarity_scores(text=item)['neg']
        self.neu_score = self.sia.polarity_scores(text=item)['neu']
        self.comp_score = self.sia.polarity_scores(text=item)['compound']
        return self.pos_score, self.neg_score, self.neu_score, self.comp_score

    def get_antonyms(self, word_item):
        for syn in wordnet.synsets(word_item):
            for lm in syn.lemmas():
                if lm.antonyms():
                    self.antonyms.append(lm.antonyms()[0].name())
        return self.antonyms

    def is_neutral_sentence_really(self, check_sentence):
        check = []
        words = str(check_sentence).split(" ")
        for word in words:
            any_antonyms = self.get_antonyms(word_item=word)
            if len(any_antonyms) > 0:
                for antonym in any_antonyms:
                    new_sent = str(check_sentence).replace(word, antonym)
                    new_analysis = self.analyse_sentence_polarity(item=new_sent)[3]
                    if new_analysis < 0:
                        check.append(False)
                    else:
                        self.status = True
            else:
                self.status = True
        if False in check:
            self.status = False
        else:
            self.status = True
        return self.status

    def sentence_analysis(self, check_sentence):
        if self.analyse_sentence_polarity(item=check_sentence)[2] == 1.0:
            if self.is_neutral_sentence_really(check_sentence=check_sentence):
                self.status = 'negative'
            else:
                self.status = 'positive'
        else:
            if self.analyse_sentence_polarity(item=check_sentence)[3] < 0:
                self.status = 'negative'
            else:
                self.status = 'positive'
        return self.status


class GetQuotes:
    """
    We will get quotes form the API I got form Rapid API website link is
    https://rapidapi.com/martin.svoboda/api/quotes15/pricing
    It allows us to request 1 per second, unlimited. we need to get the quotes and analyse them right away
    """
    get_id = {
        'x-rapidapi-host': "quotes15.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }
    key = []
    is_noun = lambda pos: pos[:2] == 'NN'
    content = ''
    tags = []
    originator = []
    status = True

    def extract_noun(self, tag_list):
        nouns = [word for (word, pos) in nltk.pos_tag(tag_list) if self.is_noun]
        return nouns

    def get_quotes(self):
        """This function will get the quotes at wait of 5 seconds and return to quote analyse function"""
        try:
            while self.status is True:
                time.sleep(1)
                url = "https://quotes15.p.rapidapi.com/quotes/random/"
                querystring = {"language_code": "en"}
                headers = self.get_id
                response = requests.request("GET", url, headers=headers, params=querystring)
                response = eval(response.__dict__['_content'].decode('utf-8'))
                for _ in response.items():
                    self.content = response['content']
                    self.tags = response['tags']
                    self.originator = response['originator']
                if "muslim" in self.tags or "religious" in self.tags:
                    self.status = True
                else:
                    self.status = False
            final = self.analysing_quotes(content=self.content, tags=self.tags, originator=self.originator)
            return final
        except Exception as e:
            print(e)

    def analysing_quotes(self, content, tags, originator):
        self.content = content
        self.tags = tags
        self.originator = originator
        try:
            noun = self.extract_noun(tag_list=self.tags)
            noun = random.choice(noun)
            response_is = "I was reading over the Internet about '" + noun + "', " + str(
                originator['name']) + " said once '" + str(content) + "'"
            return response_is
        except Exception as e:
            print(e)


class ShynaSpeak:
    """
    Using google_speech library https://pypi.org/project/google-speech/ and nltk to tokenize every sentence and speak.
    make sure the dependencies for google_speech is installed before using this class.
    sox effect are in place, keep Shyna voice same across the devices.

    There are two methods:
     shyna_speaks: provide sentence(s) to speak out loud
     test_shyna_speaks: run to test everything working fine

    """
    lang = "en"
    sox_effects = ("speed", "1.0999",)
    text = "Hey! Shiv? I hope you can listen to me otherwise doesn't matter what I say or do, you will be only " \
           "complaining"
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()

    def shyna_speaks(self, msg):
        try:
            for i in sent_tokenize(msg):
                speech = Speech(i, self.lang)
                speech.play(self.sox_effects)
        except Exception as e:
            print(e)

    def test_shyna_speaks(self):
        self.shyna_speaks(self.text)

    def shyna_speaks_termux(self, msg):
        """
        Speak function with toast notification.
        In those cases when Shyna is set to sleep the function take care of this itself to speaker to just show a toast
        notification.
        Dependency :
        1) speak_or_not()
        2) Updated for Android device Only.
        """
        try:
            msgs = random.choice(str(msg).split("|"))
            if str(self.speak_or_not()).lower().__eq__('awake'):
                for i in sent_tokenize(msgs):
                    speech = Speech(i, self.lang)
                    speech.play(self.sox_effects)
            else:
                command = "termux-toast -g top " + msgs
                os.popen(cmd=command)
        except Exception as e:
            command = "termux-toast I prefer to stay silent"
            os.popen(cmd=command)
            print(e)

    def speak_or_not(self):
        #  Flow 5. it check what is the last status I send her. it is morning, silent, or sleep and return accordingly
        result = "awake"
        try:
            self.s_data.query = "SELECT greet_string FROM greeting order by count DESC limit 1;"
            cursor = self.s_data.select_from_table()
            if str(cursor).__contains__('Exception') or str(cursor).__contains__('Empty'):
                pass
            else:
                for row in cursor:
                    greet_string = str(row[0])
                    if len(greet_string) > 0:
                        if str(greet_string).lower() == 'morning':
                            result = 'awake'
                        if str(greet_string).lower() == 'silent':
                            result = 'silent'
                        if str(greet_string).lower() == 'sleep':
                            result = 'sleep'
                    else:
                        result = 'awake'
        except Exception as e:
            print(e)
            result = "awake"
        finally:
            return result

    def updated_speak_or_not_status(self, status):
        try:
            if status is False:
                self.s_data.query = "INSERT INTO greeting (new_date, new_time, greet_string) VALUES ('" \
                                    + str(self.s_time.now_date) + "', '" + str(self.s_time.now_time) + "', 'sleep')"
                self.s_data.create_insert_update_or_delete()
                self.shyna_speaks_termux(msg="Okay! I will not disturb anymore")
            else:
                self.s_data.query = "INSERT INTO greeting (new_date, new_time, greet_string) VALUES ('" \
                                    + str(self.s_time.now_date) + "', '" + str(self.s_time.now_time) + "', 'awake')"
                self.s_data.create_insert_update_or_delete()
                self.shyna_speaks_termux(msg="Hey! How are you doing?")
        except Exception as e:
            print(e)
            self.shyna_speaks_termux(msg="Sorry, what was that?")


class ShynaNews:
    """
    This will help in extract the news for the provided url. I have URL(s) stacked in database with their sources
    (TOI, Zee news)

    We have two method as per the sources:
    get_news_toi
    get_news_zee

    Define url at class level and call the function as per the URL source.
    """
    Sh_time = ShTime.ClassTime()
    url = ''
    news_item = {}

    def get_news_toi(self):
        news_feed = feedparser.parse(url_file_stream_or_string=self.url)
        entry = news_feed.entries
        for row in entry:
            for _ in row.items():
                news_date = str(row['published_parsed'].tm_year) + "-" + str(
                    row['published_parsed'].tm_mon) + "-" + str(row['published_parsed'].tm_mday)
                new_time = str(row['published_parsed'].tm_hour) + ":" + str(row['published_parsed'].tm_min) + ":" + str(
                    row['published_parsed'].tm_sec)
                if row['description'] == '':
                    row['description'] = 'Sorry, I have no description. Feel free to checkout the URL'
                    self.news_item[row['title']] = row['description'], row['id'], news_date, new_time
                else:
                    self.news_item[row['title']] = row['description'], row['id'], news_date, new_time
        return self.news_item

    def get_news_zee(self):
        news_feed = feedparser.parse(url_file_stream_or_string=self.url)
        entry = news_feed.entries
        for row in entry:
            for _ in row.items():
                news_date, news_time = self.Sh_time.get_date_and_time(text_string=row['published'])
                self.news_item[row['title']] = row['summary'], news_date, news_time
        return self.news_item


class ShynaWeather:
    """
    Define either lon/lat or city_name. for shyna the lat and lon will be fetched from the database.
    get_weather_lon_lat: return weather details in dict as per lat/lon
    get_astronomy_lon_lat: return astro details in dict as per lat/lon
    get_weather_city: return weather details in dict as per city name
    get_astronomy_city : return astro details in dict as per city name
    get_weather: this will return the complete details. astro and weather.
    """

    weather_headers = {
        'x-rapidapi-host': "weatherapi-com.p.rapidapi.com",
        'x-rapidapi-key': "pG7DIQheytmshvuLgNTRSRs3yTogp1f0rDBjsnjIaJXtHxwvdG"
    }
    weather_dict = {}
    astro_dict = {}
    lat = None
    lon = None
    city_name = None
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()

    def get_weather_lon_lat(self):
        url = "https://weatherapi-com.p.rapidapi.com/current.json"
        w_query = str(self.lat) + "," + str(self.lon)
        # querystring = {"q": "28.698255,77.461441"}
        querystring = {"q": w_query}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == "condition":
                        self.weather_dict[key] = value['text']
                    else:
                        self.weather_dict[key] = value
        except Exception as e:
            self.weather_dict['error'] = e
            print(e)
        finally:
            return self.weather_dict

    def get_astronomy_lon_lat(self):
        url = "https://weatherapi-com.p.rapidapi.com/astronomy.json"
        w_query = str(self.lat) + "," + str(self.lon)
        querystring = {"q": w_query}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == 'astro':
                        for keys, values in value.items():
                            self.astro_dict[keys] = values
                    else:
                        pass
        except Exception as e:
            self.astro_dict['error'] = e
            print(e)
        finally:
            return self.astro_dict

    def get_weather_city(self):
        url = "https://weatherapi-com.p.rapidapi.com/current.json"
        querystring = {"q": self.city_name}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == "condition":
                        self.weather_dict[key] = value['text']
                    else:
                        self.weather_dict[key] = value
        except Exception as e:
            self.weather_dict['error'] = e
            print(e)
        finally:
            return self.weather_dict

    def get_astronomy_city(self):
        url = "https://weatherapi-com.p.rapidapi.com/astronomy.json"
        querystring = {"q": self.city_name}
        try:
            response = requests.request("GET", url=url, headers=self.weather_headers, params=querystring)
            response = eval(response.text)
            for _, val in response.items():
                for key, value in val.items():
                    if key == 'astro':
                        for keys, values in value.items():
                            self.astro_dict[keys] = values
                    else:
                        pass
        except Exception as e:
            self.astro_dict['error'] = e
            print(e)
        finally:
            return self.astro_dict

    def get_weather(self):
        try:
            if self.lat is None and self.lon is None and self.city_name is None:
                self.weather_dict['Error'] = "Please define either latitude or Longitude OR city name"
            elif self.lat is None and self.lon is None:
                self.weather_dict = self.get_weather_city()
                self.astro_dict = self.get_astronomy_city()
                self.weather_dict.update(self.astro_dict)
            else:
                self.weather_dict = self.get_weather_lon_lat()
                self.astro_dict = self.get_astronomy_lon_lat()
                self.weather_dict.update(self.astro_dict)
        except Exception as e:
            self.weather_dict['error'] = e
            print(e)
        finally:
            return self.weather_dict

    def get_weather_sentence(self):
        weather_sentence = False
        try:
            self.s_data.query = "SELECT speak_sentence FROM weather_table where task_date = '" \
                                + str(self.s_time.now_date) + "'"
            result = self.s_data.select_from_table()
            for item in result:
                weather_sentence = item[0]
        except Exception as e:
            weather_sentence = False
            print(e)
        finally:
            return weather_sentence


class BroadcastMessageDecision:
    """
    broadcast_morning_decision: return greetings message ready to forward or just greet.
    """
    s_time = ShTime.ClassTime()
    s_greet = ShynaGreetings()
    msg_send = "Today is not the day"
    choose_day = []

    def broadcast_morning_decision(self):
        try:
            today_day = int(self.s_time.get_day_of_week())
            divide_unit = random.choice([0, 1, 2, 3, 4, 5, 6])
            for i in range(0, int(divide_unit)):
                self.choose_day.append(i)
            if today_day in self.choose_day:
                self.msg_send = self.s_greet.greet_good_morning()
            else:
                self.msg_send = "Good Morning, Shiv!"
        except Exception as e:
            self.msg_send = "Today is not the day"
            print(e)
        finally:
            return self.msg_send


class ShynaMailClient:
    """
    Make sure define a default path of image file. it will use that image or any other file instead of that image.
    Below value need to be defined:
    path = ""
    sender_gmail_account_id = ""
    sender_gmail_account_pass = ""
    master_email_address_is = ""
    email_subject = ""
    email_body = ""

    method
    send_email_with_attachment_subject_and_body: Need email_subject and email_body
    """
    msg = MIMEMultipart()
    path = ""
    sender_gmail_account_id = ""
    sender_gmail_account_pass = ""
    master_email_address_is = ""
    email_subject = ""
    email_body = ""

    def send_email_with_attachment_subject_and_body(self):
        try:
            from_password = self.sender_gmail_account_pass
            self.msg = MIMEMultipart()
            self.msg['From'] = self.sender_gmail_account_id
            self.msg['To'] = self.master_email_address_is
            self.msg['Subject'] = self.email_subject
            body = self.email_body
            self.msg.attach(MIMEText(body, 'plain'))
            filename = self.path
            attachment = open(filename, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            self.msg.attach(p)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(self.sender_gmail_account_id, from_password)
            text = self.msg.as_string()
            s.sendmail(self.sender_gmail_account_id, self.master_email_address_is, text)
            s.quit()
            print("I have sent you the details check your email now")
        except Exception as ex:
            print("Exception from functionality sys \n", str(ex))


class ShynaRegexExtraction:
    """"
    Define string first and then run the needed method(s):
    re_for_cr_db_from_email_body
    get_link_and_data_from_summary
    clean_apostrophe
    """
    input_str = ""

    def re_for_cr_db_from_email_body(self):
        """Extract the Credit and Debit amount from the email's body"""
        regex = r"(.(r).(n))"
        subst = ''
        result = re.sub(regex, subst, self.input_str, 0, re.MULTILINE)
        if result:
            final = str(str(result).split('Dear Customer,')[-1]).split('\n \n Warm')
            if str(final[0]).__contains__('credited to A/c'):
                final_stmt = str(final[0]).split('credited to A/c')[0]
                return "+" + final_stmt.strip('\n \n')
            elif str(final[0]).__contains__('debited from account'):
                final_stmt = str(final[0]).split('debited from account')[0]
                return "-" + final_stmt.strip('\n \n')

    def get_link_and_data_from_summary(self):
        """return news summary and link"""
        try:
            row = []
            regex = r"(')"
            if re.findall(r'(https?://\S+)', self.input_str):
                ans = re.findall(r'(https?://\S+)', self.input_str)
                for rows in ans:
                    rows = rows.strip('"><img')
                    row.append(rows)
            else:
                row.append('empty link')
            link = row[0]
            if self.input_str.split('</a>')[-1]:
                split_data = self.input_str.split('</a>')[-1]
                data = re.sub(regex, "", split_data, 0, re.MULTILINE)
            else:
                data = 'No summary found'
            return link, data
        except Exception as e:
            print(e)
            pass

    def clean_apostrophe(self):
        """Remove apostrophe from the string"""
        try:
            regex = r"(')"
            self.input_str = re.sub(regex, "", self.input_str, 0, re.MULTILINE)
            return self.input_str
        except Exception as e:
            print(e)

# 0.2 Package work


class ShynaDistanceDifference:
    """"
    Return the distance difference in km based on latitude and longitude

    Method is:
    def get_distance_difference(default_latitude, default_longitude, new_latitude, new_longitude): returns float value
    """
    R = 6371.0

    def get_distance_difference(self, default_latitude, default_longitude, new_latitude, new_longitude):
        lat1 = radians(default_latitude)
        lon1 = radians(default_longitude)
        lat2 = radians(new_latitude)
        lon2 = radians(new_longitude)
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = self.R * c
        return float(distance)


class ShynaGoogleSearch:
    """
    perform google search and return the result in form of link.
    define search string as class property.

    Two functions:
    search_google_with_top_result -  Return only one link result
    search_google_with_limit_result - ask for number of result needed and return result in form of link.
    """
    search_string = ''

    def search_google_with_top_result(self):
        return search(term=self.search_string, num_results=0)

    def search_google_with_limit_result(self, result_number):
        return search(term=self.search_string, num_results=result_number)


class ShynaWikiSearch:
    """
    perform wikipedia search.
    define search string as class property.
    Below functions available for use
    search_wiki_page: return the complete page with set search string.
    one_line_introduction: return one line summary of set search string
    set_line_introduction: provide the number of summary sentences needed.
    """
    search_string = ''

    def search_wiki_page(self):
        page_details = wikipedia.page(title=self.search_string, preload=False, auto_suggest=False)
        return page_details.content

    def one_line_introduction(self):
        sentence_summary = wikipedia.summary(title=self.search_string, sentences=1, auto_suggest=False)
        return sentence_summary

    def set_line_introduction(self, num_sent):
        sentence_summary = wikipedia.summary(title=self.search_string, sentences=num_sent, auto_suggest=False)
        return sentence_summary
