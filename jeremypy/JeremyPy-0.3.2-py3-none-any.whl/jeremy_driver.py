import datetime
import os
import re
import requests
from time import sleep

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException, NoSuchElementException)
import pyperclip

from jeremypy.jeremy_config import JeremyConfig
from jeremypy.jeremy_exceptions import InvalidConfigError


class JeremyDriver:
    def __init__(self, profile_path=None, headless=False, version=None):
        options = uc.ChromeOptions()
        if profile_path:
            options.add_argument(f'--user-data-dir={profile_path}')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/87.0.4280.88 Safari/537.36')
        options.add_argument('--no-first-run')
        options.add_argument('--no-service-autorun')
        options.add_argument('--password-store=basic')
        self.driver = uc.Chrome(headless=headless, options=options,
                                version_main=version)

    def close(self):
        """Closes the chromedriver."""
        self.driver.close()

    def find_by_id(self, id_):
        """Easy way to find element by ID."""
        return self.driver.find_element(By.ID, id_)

    def find_by_name(self, name):
        """Easy way to find element by name."""
        return self.driver.find_element(By.NAME, name)

    def find_by_xpath(self, xpath):
        """Easy way to find element by XPATH."""
        return self.driver.find_element(By.XPATH, xpath)

    def find_by_aria_label(self, aria_label):
        """Easy way to find element by aria-label."""
        return self.driver.find_element(By.XPATH, f'//*[@aria-label="{aria_label}"]')


class MessengerDriver(JeremyDriver):
    def __init__(self, config=None, chat=None, account=None, profile_path=None, headless=False, version=None):
        if config:
            self.config = JeremyConfig(config)
            chat = self.config.get("MessengerBot", "CHAT")
            if chat:
                self.chat = chat
                self.account = (self.config.get("MessengerBot", "EMAIL"),
                                self.config.get("MessengerBot", "PASS"))
                self.profile_path = self.config.get("MessengerBot", "PROFILE_PATH")
                self.headless = self.config.get("MessengerBot", "HEADLESS", boolean=True)
            else:
                raise InvalidConfigError
        else:
            if not chat:
                raise Exception("MessengerDriver needs either valid config filename OR chat parameter")
            self.chat = chat
            self.account = account
            self.profile_path = profile_path
            self.headless = headless
        self.message_cache = []
        self.last_error = None
        super().__init__(profile_path=self.profile_path, headless=self.headless, version=version)

    def login(self):
        """Runs login routine."""
        try:
            sleep(1)
            email = self.driver.find_element(By.ID, 'email')
            pw = self.driver.find_element(By.ID, 'pass')
            cb = self.driver.find_element(By.XPATH, '//input[@name="persistent"]/following-sibling::span')
            email.clear()
            email.send_keys(self.account[0])
            sleep(1)
            pw.clear()
            pw.send_keys(self.account[1])
            sleep(1)
            cb.click()
            sleep(1)
            pw.submit()
            assert self.driver.current_url == self.chat
        except Exception as e:
            print(e)
            input("Press enter after logging in")
            self.go_to_chat()

    def go_to_chat(self):
        """Goes to conversation that the bot is going to run on."""
        self.driver.get(self.chat)
        if self.driver.current_url.startswith('https://www.messenger.com/login.php'):
            self.login()

    def get_message_with_emojis(self, element):
        """Gets message with emojis using innerHTML of element."""
        inner_html = element.get_attribute('innerHTML')
        return _extract_message_from_inner_html(inner_html)

    def get_messages(self, initial=False):
        """Finds all available messages sent by other users in chat that have not already been processed, and returns
        them in a list."""
        try:
            messages = []
            message_groups = self.driver.find_elements(By.XPATH, '//div[@role="gridcell" and (div//span/div/div['
                                                                 '1]/div/div or div//span/div/div/div/span)]')
            for group in message_groups:
                try:
                    person_elements = group.find_elements(By.XPATH, 'h4//div[@data-testid="mw_message_sender_name"]')
                    if len(person_elements) == 0:  # Message does not have sender's name above it
                        person_elements = group.find_elements(By.XPATH, 'span')
                    if len(person_elements) == 0:  # Message is outgoing
                        person_elements = group.find_elements(By.XPATH, 'h4/span')
                    if len(person_elements) == 0:  # Message is a reply to another message
                        person_elements = group.find_elements(By.XPATH, 'h4/div/div/div/div')
                    person = person_elements[0].text
                    message_elements = group.find_elements(By.XPATH, 'div//span/div/div/div/div')
                    if len(message_elements) > 0:  # Has text or is a thumbs up
                        if len(message_elements[0].find_elements(By.TAG_NAME, 'span')) > 0:  # Has text and emojis
                            message = self.get_message_with_emojis(message_elements[0])
                        else:  # Only has text or a thumbs up
                            message = message_elements[0].text
                    else:  # Only emojis
                        message_element = group.find_element(By.XPATH, 'div//span/div/div/div')
                        message = self.get_message_with_emojis(message_element)
                    messages.append((person, message))
                except NoSuchElementException as e:  # Someone removed a message
                    pass
            if initial:
                self.message_cache = messages
                return self.message_cache
            if not messages == self.message_cache:
                new_messages = _get_list_b_past_end_of_list_a(self.message_cache,
                                                              messages)
                self.message_cache = messages
                if new_messages:
                    return new_messages
        except (StaleElementReferenceException, IndexError) as e:  # Stale element
            pass
        return []

    def wait_and_click_element_by_xpath(self, xpath, delay=10):
        """Waits up to (delay) seconds until button xpath is available, and then executes a javascript click method."""
        element = WebDriverWait(self.driver, delay).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script('arguments[0].click();', element)

    def send_message(self, message):
        """Enters and sends message with standard send_keys method. This only works with normal unicode characters."""
        input_field = self.find_by_aria_label('Message')
        message = message.replace("\n", Keys.SHIFT + Keys.ENTER + Keys.SHIFT)
        input_field.send_keys(message)
        send_button_xpath = '//*[@aria-label="Press Enter to send"]'
        self.wait_and_click_element_by_xpath(send_button_xpath)

    def send_pretty_message(self, message):
        """Enters and sends message with copy/paste method. This worrks with any unicode characters."""
        input_field = self.find_by_aria_label('Message')
        temp = self.get_clipboard()
        self.copy_to_clipboard(message)
        input_field.send_keys(Keys.SHIFT, Keys.INSERT)
        self.copy_to_clipboard(temp)
        send_button_xpath = '//*[@aria-label="Press Enter to send"]'
        self.wait_and_click_element_by_xpath(send_button_xpath)

    def send_attachment(self, filepath):
        """Sends filepath to attachment field and submits it."""
        attach = self.find_by_xpath('//input[@type="file"]')
        attach.send_keys(filepath)
        send_button_xpath = '//*[@aria-label="Press Enter to send"]'
        self.wait_and_click_element_by_xpath(send_button_xpath)

    def download_url(self, url, download_path=None):
        """Downloads url to download path and automatically adds the extension. If no path is given,
        it downloads to tempfile_(datetime).(ext) in the current working directory.
        """
        if '.jpg' in url:
            thumbnail_extension = '.jpg'
        else:
            thumbnail_extension = os.path.splitext(url)[1]
        r = requests.get(url)
        if not download_path:
            name = os.path.join(os.getcwd(), 'tempfile_'
                                + datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))
        filename = download_path + thumbnail_extension
        with open(filename, 'wb+') as fp:
            fp.write(r.content)
        return filename

    def copy_to_clipboard(self, text):
        """Copies given text to clipboard."""
        pyperclip.copy(text)

    def get_clipboard(self):
        """Returns contents from the clipboard."""
        return pyperclip.paste()

    def messages_found_event(self):
        """Overload this event handler for when the initial messages are located."""
        print("Messages found")

    def new_message_event(self, sender, message):
        """Overload this event handler for when new messages are received in message loop.
        Return True to exit message loop.
        """
        print(f'{sender}: {message}')
        return False

    def this_runs_every_loop(self):
        """Overload this event handler to do something every time the message loop runs (Ex: schedule).
        Return True to exit message loop.
        """
        return False

    def exception_event(self, exception):
        """Overload this event handler for when an exception is raised in message loop.
        Return True to exit message loop.
        """
        return False

    def duplicate_exception_event(self, exception):
        """Overload this event handler for when the same exception is raised in message loop twice in a row.
        Return True to exit message loop.
        """
        return True

    def message_loop(self):
        """Runs message loop. See *_event methods to overload functionality."""
        sleep(1)
        while len(self.get_messages(initial=True)) == 0:
            sleep(1)
        self.messages_found_event()
        while True:
            try:
                if self.this_runs_every_loop():
                    return
                sleep(.1)
                new_messages = self.get_messages()
                if len(new_messages) == 0:
                    continue
                if len(new_messages) > 3:  # In the case that all messages are wrongly considered new
                    continue
                for sender, message in new_messages:
                    if self.new_message_event(sender, message):
                        return
                self.last_error = None
            except Exception as e:
                if self.last_error == str(e):
                    if self.duplicate_exception_event(e):
                        return
                else:
                    if self.exception_event(e):
                        return
                self.last_error = str(e)


def _get_list_b_past_end_of_list_a(list_a, list_b):
    """Returns the sublist of list_b that occurs directly after the overlap
    between list_a and list_b. If there is no direct overlap, return none.
    If list_b does not extend list_a, return empty list.
    """
    for index_a, item_a in enumerate(list_a):
        if list_a[index_a:] == list_b[0:len(list_a)-index_a]:
            return list_b[len(list_a)-index_a:]
    return None


def _extract_message_from_inner_html(text):
    """Returns Messenger message from innerHTML that can contain both text and emojis."""
    pattern = '[^<]+(?:<span)|(?:alt=").{1,3}(?:")|(?:</span>)[^<]*'
    matches = re.findall(pattern, text)
    result = ''
    for match in matches:
        if match.endswith('<span'):
            result += match[:-5]
        elif match.startswith('</span>'):
            result += match[7:]
        elif match.startswith('alt'):
            result += match[5:-1]
    return result


if __name__ == "__main__":
    driver = JeremyDriver()
