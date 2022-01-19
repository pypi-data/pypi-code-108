import numpy as np
import pandas as pd
from .wordle_dictionary import popularity_dict
class Guesser:
    """This class handles guessing strategies. It is sent a strategy name on initialization and sets its guessing function
    to one of the strategy functions.
    """
    
    def __init__(self,strategy):
        strategies={
            "random":self.make_random_guess,
            "entropy":self.make_entropy_guess,
            "scored":self.make_scored_guess
        }
        try:
            self.make_guess=strategies[strategy]
            self.guesses=0
        except:
            print(f"Guessing strategy must be one of:")
            print(", ".join(list(strategies.keys())))
                
    def make_random_guess(self,possible_words):
        """Just pick a random possible word"""
        return  np.random.choice(possible_words) 
                    
    def make_scored_guess(self,possible_words):
        """Pick the first word in the list of possible words
            uses the fact possible_words is sorted by letter frequency"""
        return possible_words[0]        
    
    def make_entropy_guess(self,possible_words):
        """Pick the word that will reduce the size of possible_words the most
        using the expectation value of the reduction of the list size from each letter"""
        
        #entropy calculation is slow so lets use precalculated choice for first guess
        if self.guesses==0:
            self.guesses+=1
            return "soare"
        #for all letter guesses entropy is wordle specific so do full calculation
        else:
            position_count_df,letter_count_df=self.get_position_letter_counts(possible_words)
            n_words=len(possible_words)
            expect_func=lambda x: self.expected_list_reduction(x,n_words,
                                                            position_count_df,letter_count_df)
            expectations=map(expect_func,possible_words)
            A=zip(expectations,possible_words)
            A=sorted(A,reverse=True)
            expectations,possible_words=zip(*A)
            self.guesses+=1
            return possible_words[0]
    
           

    def get_position_letter_counts(self,possible_words):
        """Turn possible_words list into a dataframe of counts of letter/position pairs
            as well as a list of counts of just letter appearances"""
        df=pd.DataFrame(np.asarray([list(word) for word in possible_words]))
        df.columns=[1,2,3,4,5]
        df=df.melt(var_name="Position",value_name="Letter")
        df=df.groupby(["Position","Letter"]).size().reset_index().rename({0:"Count"},axis=1)
        letters=df.groupby("Letter")["Count"].sum()
        df=df.set_index(["Position","Letter"])
        return df,letters
    
    def expected_list_reduction(self,guess,n_words,position_count_df,letter_count_df):
        """
            Calculates the expectation value of the reduction in the word list that will be
            possible from the scoring (green/orange/white) of each letter in a word
            Sums them all together to get an idea of total reduction in list size from a guess
        """
        expect=0.0
        done=[]
        for i,letter in enumerate(guess):
            #count the number of times a letter would be green/orange/white in our word list
            green_count=position_count_df.loc[i+1,letter].values[0]
            orange_count=letter_count_df.loc[letter]-green_count
            white_count=n_words-green_count-orange_count
            
            #expectation value is then probability of result*(reduction in list size from that result)
            expect+=(green_count/n_words)*(n_words-green_count)
            #oranges/whites are only useful once so repeated letters only contribute green reduction
            if letter not in done:
                expect+=(orange_count/n_words)*(n_words-orange_count)
                expect+=(white_count/n_words)*(n_words-white_count)
                done.append(letter)
            expect+=popularity_dict[guess]
        return expect