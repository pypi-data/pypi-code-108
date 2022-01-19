import re #regex for filtering dictionary
import random #picking random words and wordles
import datetime #for today's wordle

from argparse import ArgumentParser # for invoking from command line

from .wordle_dictionary import scored_dictionary,wordles
from .Guesser import Guesser


class WordleBot:
    """This bot solves wordles."""
    
    def __init__(self,wordle=None,strategy="entropy",dark_mode=True,emoji=True,show_all_lines=False):
        self.dictionary = scored_dictionary
        self.wordles = wordles
        
        self.wordle = None
        self.wordle_number = None
        self.possible_words = self.dictionary
        
        self.solved = False
        self.num_of_guesses = 0
        self.list_of_guesses = []
        self.list_of_colours = []
        self.exclude_letters = []
        self.include_letters = []
        self.correct_letters = list('.....')
        self.misplaced_letters = list('.....')
        self.misplaced_letters_regex = list('.....')
        self.guesser=Guesser(strategy)
        
        self.emoji = emoji
        self.dark_mode = dark_mode
        self.show_all_lines = show_all_lines
            
        if not wordle or wordle == 'todays': # pretty frustrating that 'today' is a valid wordle
            self.pick_todays_wordle()
        elif wordle == 'random':
            self.pick_random_wordle()
        elif type(wordle) == int:
            if wordle >= len(self.wordles) or wordle < 0:
                raise ValueError('Wordle number out of range, choose a number between 0 and {max_wordle_number}'.format(max_wordle_number = len(self.wordles)))
            self.pick_wordle(wordle)
        elif type(wordle) == str:
            self.check_valid(wordle)
            self.set_wordle(wordle)
        else:
            raise ValueError("Invalid wordle argument. Leave empty for today's wordle, set 'random' for a random wordle, choose a number between 0 and {max_wordle_number} for that wordle number, or enter a valid 5-letter word to set that as the wordle.".format(max_wordle_number = len(self.wordles)))
    
    def set_wordle(self,wordle):
        self.wordle = wordle
    
    def pick_wordle(self,wordle_number):
        self.wordle_number = wordle_number
        self.set_wordle(self.wordles[wordle_number])
        
    def pick_random_wordle(self):
        self.wordle = random.choice(self.wordles)
        
    def pick_todays_wordle(self):
        self.wordle_number = (datetime.datetime.now()-datetime.datetime(2021,6,19)).days
        self.wordle = self.wordles[self.wordle_number]
        
    def check_valid(self,guess):
        """Check the word is a dictionary-valid 5-letter word."""
        if len(guess) != 5:
            raise ValueError('Word "{guess}" does not have 5 letters.'.format(guess=guess))
        if guess not in self.dictionary:
            raise ValueError('Word "{guess}" not in dictionary.'.format(guess=guess))
    
    def add_colours(self,any_letters_in_wordle,exact_letters_in_wordle):
        """Add the result of a guess to the array of colours; this uses ascii for now"""
        # b for black, y for yellow, g for green
        
        new_colours = list('bbbbb')
        
        for i in range(5):
            if any_letters_in_wordle[i]:
                new_colours[i] = 'y'
        for i in range(5):
            if exact_letters_in_wordle[i]:
                new_colours[i] = 'g'
                
        new_colours = ''.join(new_colours)
        self.list_of_colours.append(new_colours)
        return new_colours
    
    def prepare_emoji_colours(self):
        """Convert the ascii array of colours to print emoji instead"""
        list_of_colours = self.list_of_colours
        
        if not self.show_all_lines and len(list_of_colours)>6:
            list_of_colours = list_of_colours[:6]
        
        if self.dark_mode:
            wrong_square='⬛'
        else:
            wrong_square='⬜'
            
        prepared_list = [string.replace('b',wrong_square).replace('y','🟨').replace('g','🟩') for string in list_of_colours]
        
        return '\n'.join(prepared_list)
        
    def prepare_ascii_colours(self):
        """Just print the ascii array of colours, no conversion to emoji"""
        list_of_colours = self.list_of_colours
        
        if not self.show_all_lines and len(list_of_colours)>6:
            list_of_colours = list_of_colours[:6]
            
        prepared_list = [string.replace('b',' ').replace('y','▓').replace('g','█') for string in list_of_colours]
        
        return '\n'.join(prepared_list)
        
    def show_result(self):
        if self.emoji:
            prefix_txt = 'WordleBot 🤖 '
        else:
            prefix_txt = 'WordleBot '
        if self.wordle_number:
            num_txt = '{} '.format(self.wordle_number)
        else:
            num_txt = ''
        if self.num_of_guesses < 7:
            score_txt = '{}/6'.format(self.num_of_guesses)
        else:
            score_txt = 'X/6'
            
        first_line = prefix_txt+num_txt+score_txt
        
        
        if self.emoji:
            colours_txt = self.prepare_emoji_colours()
        else:
            colours_txt = self.prepare_ascii_colours()
            
        result_txt = first_line+'\n\n'+colours_txt
        
        print(result_txt)
        
        return result_txt
        
    
    def check_letters(self,guess):
        """Check how the guess matches up to the wordle, and update the lists of letters"""
        # Are the letters in the wordle, regardless of position?
        any_letters_in_wordle = [letter in self.wordle for letter in guess]
        
        for i in range(5):
            if any_letters_in_wordle[i]:
                self.include_letters += guess[i]
            else:
                self.exclude_letters += guess[i]
        
        # Are any letters in the correct position?
        exact_letters_in_wordle = [guess[i] == self.wordle[i] for i in range(5)]
        
        for i in range(5):
            if exact_letters_in_wordle[i]:
                self.correct_letters[i] = guess[i]
                
        # Any letters in the wordle, but in the wrong position?
        misplaced_letters_in_wordle = [x^y for x,y in zip(any_letters_in_wordle,exact_letters_in_wordle)] # elementwise xor
        self.misplaced_letters = list('.....')
        for i in range(5):
            if misplaced_letters_in_wordle[i]:
                self.misplaced_letters[i] = guess[i]
                self.misplaced_letters_regex[i] = '[^'+guess[i]+']'
                
        self.add_colours(any_letters_in_wordle,exact_letters_in_wordle)

    
    def check_guess(self,guess):
        """Check whether the guess is right, and update the lists of letters"""
        self.check_valid(guess)
        
        self.num_of_guesses += 1
        self.list_of_guesses.append(guess)
        
        self.check_letters(guess)
        
        if self.wordle == guess:
            self.solved = True
            return True # congrats!
        
        return False
        
    def filter_possible_words(self):
        """Filter the list of remaining possible words by: 
        1. already guessed words
        2. correctly placed letters; 
        3. misplaced letters; 
        4. letters the word must contain; 
        5. letters the word must not contain"""
        # filter by previously guessed words
        # these should have already been removed in make_guess()
        # but let's make sure in case something happened out of order
        if self.list_of_guesses:
            filter_by_guessed_words = re.compile('(?!('+'|'.join(self.list_of_guesses)+'))')
            self.possible_words = list(filter(filter_by_guessed_words.match,self.possible_words))
            
        # filter by the correctly placed letters
        filter_by_correct_letters = re.compile(''.join(self.correct_letters))
        self.possible_words = list(filter(filter_by_correct_letters.match,self.possible_words))
        
        # filter by misplaced letters
        filter_by_misplaced_letters = re.compile(''.join(self.misplaced_letters_regex))
        self.possible_words = list(filter(filter_by_misplaced_letters.match,self.possible_words))
        
        # filter by letters the word must contain
        if self.include_letters:
            include_letters_regex = ''.join(['(?=\\w*{i})'.format(i=i) for i in self.include_letters])
            filter_by_include_letters = re.compile(include_letters_regex)
            self.possible_words = list(filter(filter_by_include_letters.match,self.possible_words))
        
        # filter by letters the word must not contain
        if self.exclude_letters:
            exclude_letters_regex = ''.join(['(?!\\w*{i})'.format(i=i) for i in self.exclude_letters])
            filter_by_exclude_letters = re.compile(exclude_letters_regex)
            self.possible_words = list(filter(filter_by_exclude_letters.match,self.possible_words))
        
    def make_guess(self):
        """Guess the next word based on the chosen strategy"""
        guess=self.guesser.make_guess(self.possible_words)
        self.possible_words.remove(guess) # Ensure that guessed word is removed from possible future words
        return guess
        

        
    def solve(self):
        """Loop round, filtering posible words and guessing according to the chosen strategy"""
        while not self.solved and self.num_of_guesses < 30: # If not guessed in 30, something's gone wrong
            self.filter_possible_words()
            guess = self.make_guess()
            self.check_guess(guess)

        self.show_result()
        
def run_bot(*args, **kwargs):
    bot = WordleBot(*args, **kwargs)
    bot.solve()
    
def run_bot_from_cmd():
    arguments = parse_args()
    
    # If wordle argument is number (and not None), convert from str to int
    arguments.wordle
    if arguments.wordle and all(map(str.isdigit,arguments.wordle)):
        arguments.wordle = int(arguments.wordle)
    
    run_bot(wordle=arguments.wordle,
          strategy=arguments.strategy,
         dark_mode=arguments.dark_mode,
             emoji=arguments.emoji,
    show_all_lines=arguments.show_all_lines)
    
def parse_args():
    parser = ArgumentParser(description= "This bot solves wordles. Invoking with no arguments solves today's wordle, or you can pass it a wordle number or 5-letter word to solve for.")
    parser.add_argument('wordle', type=str, help="Optional. Either a wordle number between 0 and 2315, a 5-letter word to guess, or the string 'random' to choose a random wordle. If not specified, solves today's wordle.", nargs='?', default=None)
    parser.add_argument('--strategy', type=str, help="The strategy to employ. Choose from 'entropy' (best but slowest), 'scored', or 'random'.", choices=['entropy','scored','random'], default='entropy')
    #parser.add_argument('--dark_mode', dest='dark_mode', action='store_true')
    parser.add_argument('--light-mode', dest='dark_mode', action='store_false', default=True, help="Replaces dark squares with light squares.")    
    #parser.add_argument('--emoji', dest='emoji', action='store_true')
    parser.add_argument('--no-emoji', dest='emoji', action='store_false', default=True, help="Removes emoji from output, useful if your terminal does not support emoji.")    
    parser.add_argument('--show-all-lines', dest='show_all_lines', action='store_true', default=False, help="Shows all lines in the bot's solution, even if it fails (takes more than 6 guesses).")
    
    
    arguments=parser.parse_args()
    #print(arguments)
    
    return arguments