import ast
import random
import requests
from seleniumbase import __version__
from seleniumbase import BaseCase


class WordleTests(BaseCase):

    word_list = []

    def initalize_word_list(self):
        js_file = "https://www.powerlanguage.co.uk/wordle/main.e65ce0a5.js"
        req_text = requests.get(js_file).text
        start = req_text.find("var La=") + len("var La=")
        end = req_text.find("],", start) + 1
        word_string = req_text[start:end]
        self.word_list = ast.literal_eval(word_string)

    def modify_word_list(self, word, letter_status):
        new_word_list = []
        correct_letters = []
        present_letters = []
        for i in range(len(word)):
            if letter_status[i] == "correct":
                correct_letters.append(word[i])
                for w in self.word_list:
                    if w[i] == word[i]:
                        new_word_list.append(w)
                self.word_list = new_word_list
                new_word_list = []
        for i in range(len(word)):
            if letter_status[i] == "present":
                present_letters.append(word[i])
                for w in self.word_list:
                    if word[i] in w and word[i] != w[i]:
                        new_word_list.append(w)
                self.word_list = new_word_list
                new_word_list = []
        for i in range(len(word)):
            if (
                letter_status[i] == "absent"
                and word[i] not in correct_letters
                and word[i] not in present_letters
            ):
                for w in self.word_list:
                    if word[i] not in w:
                        new_word_list.append(w)
                self.word_list = new_word_list
                new_word_list = []

    def skip_if_incorrect_env(self):
        if self.headless:
            message = "This test doesn't run in headless mode!"
            print(message)
            self.skip(message)
        version = [int(i) for i in __version__.split(".") if i.isdigit()]
        if version < [2, 4, 0]:
            message = "This test requires SeleniumBase 2.4.0 or newer!"
            print(message)
            self.skip(message)

    def test_wordle(self):
        self.skip_if_incorrect_env()
        self.open("https://www.powerlanguage.co.uk/wordle/")
        self.click("game-app::shadow game-modal::shadow game-icon")
        self.initalize_word_list()
        keyboard_base = "game-app::shadow game-keyboard::shadow "
        word = random.choice(self.word_list)
        total_attempts = 0
        success = False
        for attempt in range(6):
            total_attempts += 1
            word = random.choice(self.word_list)
            letters = []
            for letter in word:
                letters.append(letter)
                button = 'button[data-key="%s"]' % letter
                self.click(keyboard_base + button)
            button = 'button[data-key="↵"]'
            self.click(keyboard_base + button)
            self.sleep(1)  # Time for the animation
            row = 'game-app::shadow game-row[letters="%s"]::shadow ' % word
            tile = row + "game-tile:nth-of-type(%s)"
            letter_status = []
            for i in range(1, 6):
                letter_eval = self.get_attribute(tile % str(i), "evaluation")
                letter_status.append(letter_eval)
            if letter_status.count("correct") == 5:
                success = True
                break
            self.word_list.remove(word)
            self.modify_word_list(word, letter_status)

        self.save_screenshot_to_logs()
        print('\nWord: "%s"\nAttempts: %s' % (word.upper(), total_attempts))
        if not success:
            self.fail("Unable to solve for the correct word in 6 attempts!")
        self.sleep(3)
