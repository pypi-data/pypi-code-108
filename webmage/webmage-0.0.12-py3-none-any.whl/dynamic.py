from bs4 import BeautifulSoup as BS
import re
from selenium import webdriver
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json

# Runes
from .dynamic_rune import DynamicRune

class DynamicSpell:
    def __init__(self, url, driver_path=None, ghost=False):
        self.url = url
        self.driver_path = driver_path
        self.ghost = ghost

        self.initialize_driver()

    def initialize_driver(self):
        # Get chrome driver if no path is given.
        if self.driver_path == None:
            self.driver_path = ChromeDriverManager().install()

        # Set options to ignore useless errors.
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        if self.ghost:
            options.add_argument('--headless')


        # Open the chrome browser. It will show up unless ghost == True.
        self.driver = webdriver.Chrome(self.driver_path, chrome_options=options, desired_capabilities=capabilities)
        # Go to the initialized webpage.
        self.driver.get(self.url)


    def close(self):
        self.driver.close()


    # For selecting first item based on CSS selector.
    def select(self, css_selector):
        return DynamicRune(self.driver.find_element_by_css_selector(css_selector), self.driver)


    # For selecting first item based on CSS selector.
    def selectAll(self, css_selector):
        return [DynamicRune(i, self.driver)for i in self.driver.find_elements_by_css_selector(css_selector)]

    # Changes the URL of the original soup.
    def change_url(self, url):
        self.url = url
        self.driver.get(url)

    # Click on a element by its css selector
    def click(self, css_selector):
        self.driver.find_element_by_css_selector(css_selector).click()

    # Click on all elements by its css selector. Waits 0.25 between each click by default
    def clickAll(self, css_selector, wait_interval=0.25):
        clickable_elements = self.driver.find_elements_by_css_selector(css_selector).click()
        for el in clickable_elements:
            el.click()
            self.wait(wait_interval)

    def scroll(self, wait_interval, scroll_count, scroll_css_selector="document.scrollingElement", callback=None, verbose=True):
        counter = 1

        # Make the CSS Selector into a querySelector
        if scroll_css_selector != 'document.scrollingElement':
            scroll_css_selector = f'document.querySelector("{scroll_css_selector}")'

        last_height = self.driver.execute_script(f"return {scroll_css_selector}.scrollHeight")

        while counter <= scroll_count:
            self.driver.execute_script(f"{scroll_css_selector}.scrollTop = {scroll_css_selector}.scrollHeight;")
            # Wait to load page
            self.wait(wait_interval)
            if verbose:
                print(f'\rScroll #{counter} completed!', end='')
            counter += 1
            
            # Execute callback function
            if callback:
                callback(self)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(f"return {scroll_css_selector}.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height
        # Go to next line after scroll completion.
        print('')


    def delicate_scroll(self, wait_interval, scroll_count, scroll_pixel_length=500, scroll_css_selector="document.scrollingElement", callback=None, verbose=True):
        counter = 1

        # Make the CSS Selector into a querySelector
        if scroll_css_selector != 'document.scrollingElement':
            scroll_css_selector = f'document.querySelector("{scroll_css_selector}")'

        # last_height = self.driver.execute_script(f"return {scroll_css_selector}.scrollHeight")
        max_height = int(self.cast_js(f'return {scroll_css_selector}.scrollHeight'))
        i = 0

        while counter <= scroll_count:
            self.cast_js(f'{scroll_css_selector}.scrollTop = {i}')
            i += scroll_pixel_length
            # Wait to load page
            self.wait(wait_interval)
            if verbose:
                print(f'\rScroll #{counter} completed!', end='')
            counter += 1
            # Execute callback function
            if callback:
                callback(self)

            # If page is dynamically adding content to page, max_height will increment.
            max_height = int(self.cast_js(f'return {scroll_css_selector}.scrollHeight'))

        # Go to next line after scroll completion.
        print('')


    def infinite_scroll(self, wait_interval, scroll_css_selector="document.scrollingElement", callback=None, verbose=True):
        counter = 1

        # Make the CSS Selector into a querySelector
        if scroll_css_selector != 'document.scrollingElement':
            scroll_css_selector = f'document.querySelector("{scroll_css_selector}")'

        last_height = self.driver.execute_script(f"return {scroll_css_selector}.scrollHeight")

        while True:
            self.driver.execute_script(f"{scroll_css_selector}.scrollTop = {scroll_css_selector}.scrollHeight;")
            # Wait to load page
            self.wait(wait_interval)
            if verbose:
                print(f'\rScroll #{counter} completed!', end='')
            counter += 1
            # Execute callback function
            if callback:
                callback(self)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(f"return {scroll_css_selector}.scrollHeight")
            # Break if at the bottom of the page.
            if new_height == last_height:
                break
            last_height = new_height
        # Go to next line after scroll completion.
        print('')


    def delicate_infinite_scroll(self, wait_interval, scroll_pixel_length=500, scroll_css_selector="document.scrollingElement", callback=None, verbose=True):
        counter = 1

        # Make the CSS Selector into a querySelector
        if scroll_css_selector != 'document.scrollingElement':
            scroll_css_selector = f'document.querySelector("{scroll_css_selector}")'

        # last_height = self.driver.execute_script(f"return {scroll_css_selector}.scrollHeight")
        max_height = int(self.cast_js(f'return {scroll_css_selector}.scrollHeight'))
        i = 0

        while max_height > i:
            self.cast_js(f'{scroll_css_selector}.scrollTop = {i}')
            i += scroll_pixel_length
            # Wait to load page
            self.wait(wait_interval)
            if verbose:
                print(f'\rScroll #{counter} completed!', end='')
            counter += 1
            # Execute callback function
            if callback:
                callback(self)

            # If page is dynamically adding content to page, max_height will increment.
            max_height = int(self.cast_js(f'return {scroll_css_selector}.scrollHeight'))

        # Go to next line after scroll completion.
        print('')

    # Wait a certain amount of seconds to continue code.
    def wait(self, time_interval):
        sleep(time_interval)

    # Gets the end name of the URL
    def get_slug(self):
        # Get portion of URL after last forward slash.
        slug =  re.sub(r'^.+?/([^/]+?)$', r'\1', self.url)
        # Remove any hashes
        slug = re.sub(r'#[^#]+?$', r'', slug)
        # Remove any queries
        slug = re.sub(r'\?.+?$', r'', slug)
        return slug



    def network_log(self):
        filtered_entries = []
        # Get the full performance log
        logs = self.driver.get_log('performance')

        for entry in logs:
            # Parse the entry.
            log = json.loads(entry["message"])["message"]
            # Filter for only these 3 logs.
            if (
                "Network.response" in log["method"]
                or "Network.request" in log["method"]
                or "Network.webSocket" in log["method"]
            ):
                filtered_entries.append(log)
        return filtered_entries


    def cast_js(self, javaScript):
        return self.driver.execute_script(javaScript)


    def cast_in_discrete_tab(self, url, callback=False, payload=None):
        # Open a new tab to the url
        self.cast_js(f"window.open('{url}', '_blank');")
        # Get list of all tabs (handles)
        handles = self.driver.window_handles
        # Make focus on second handle
        self.driver.switch_to.window(handles[1])
        # Pause to allow tab to load
        self.wait(3)
        # Call the callback with the payload arguments
        if callback:
            payload = callback(self, payload)

        # Close the tab
        self.driver.close()
        # Switch focus back to main handle
        self.driver.switch_to.window(handles[0])

        return payload

    def take_screenshot(self, css_selector):
        return self.driver.find_element_by_css_selector(css_selector).screenshot_as_png

    def clear(self, css_selector):
        self.driver.find_element_by_css_selector(css_selector).clear()

    def type(self, css_selector, string):
        self.driver.find_element_by_css_selector(css_selector).send_keys(string)

    def switch_frames(self, css_selector):
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element_by_css_selector(css_selector))

    def get_page_source(self):
        return self.driver.page_source