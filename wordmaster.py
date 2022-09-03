'''
WORDMASTER

A word guessing game similar to Wordle (https://www.nytimes.com/games/wordle/index.html)
that runs on the command line.
The user has six tries to guess a five-letter word the program has randomly chosen.

During gameplay, the program highlights letters that are correct or incorrect by
marking correct letters in the correct position green (and capitalised), correct
letters in the incorrect position yellow (and capitalised) and prints incorrect
letters in the default font colour of the console.

In addition to displaying the guessed word with letters highlighted appropriately,
the program also displays a virtual qwerty keyboard that marks used letters with
a strikethrough, and displays them with the green-yellow-default colout scheme
that has been described.

This module contains two classes:
Keyboard - which helps in displaying the virtual keyboard appropriately, and
Game - which help initiating and progressing through a game.

The game can be played by running this script directly or by importing the Keyboard
and Game classes from this module on to another script.
'''

import enchant
import requests as req
import random
import os.path
from typing import Tuple, List
import sys

class Keyboard:
    '''
    The Keyboard class

    It contains a nested list "self.keys" containing all letters in the qwerty
    keyboard arranged in three rows.

    The "self.attributes" dictionary contains attribute codes that can be added
    to the keys to visually aid the player.

    '''
    def __init__(self):
        self.keys = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                    ['z', 'x', 'c', 'v', 'b', 'n', 'm']]

        self.attributes = {'green':'\033[92m',
              'yellow':'\033[93m',
              'bold':'\033[1m',
              'underline':'\033[4m',
              'end':'\033[0m',
              'none':'',
              'strikethrough':'\u0336'}   # use strikethrough after string

    def print(self) -> None:
        '''
        Prints the keyboard.
        '''
        for i, line in enumerate(self.keys):
            print(i*" ", end="")             # spacing to match a real keyboard's arrangement
            for key in line:
                print(key, end=' ')
            print("")

    def mark(self, char:str, colour:str) -> None:
        '''
        Marks a letter (char) in the string using the required colour (green/yellow)
        and strikethrough.

        Parameters:
            char (str): character(letter) to mark
            colour (str): colour to mark with (green/yellow)
        Returns:
            None
        '''
        for i in range(len(self.keys)):
            for j in range(len(self.keys[i])):
                if self.keys[i][j][0] == char:
                    if self.keys[i][j][0:2] != "\0":  # not already changed
                        self.keys[i][j] = self.attributes[colour] + self.keys[i][j] + self.attributes['strikethrough'] + self.attributes['end']

class Game:
    '''
    The Game class

    It can be used to initiate a game, and contains class variables to keep
    track of the game.

    Some class variables:

    self.guess: Holds a string (during gameplay) containing the user's guess
    self.results: Contains results of each of the six guesses the user makes in
        a nested list.
    self.words_list: A list containing a dictionary of five-letter words loaded
        from a text file.
    self.count: Number of words in the aforementioned list.
    self.true_word: A randomly selected word to guess
    self.true_word_dict: A dictionary object containing the counts of each letter
        in self.true_word
    self.dictionary: an object from theh "enchant" library that is used as a
        spellchecker to validate each guess.
    '''
    def __init__(self):
        self.tries = 0
        self.found = False
        self.guess = None

        self.results = [["_" for _ in range(5)] for _ in range(6)]
        self.kb = Keyboard()
        self.attributes = {'green':'\033[92m',
              'yellow':'\033[93m',
              'bold':'\033[1m',
              'underline':'\033[4m',
              'end':'\033[0m',
              'strikethrough':'\u0336'}   # use strikethrough after string

        self.language = 'en_US'
        url = "https://raw.githubusercontent.com/charlesreid1/five-letter-words/master/sgb-words.txt"
        self.words_list, self.count = self.load_dictionary2list('five_letter_words.txt', url)   # load dictionary of 5-letter words
        self.true_word = self.words_list[random.randint(0, self.count-1)]              # word to guess
        self.true_word_dict = self.word2dict(self.true_word)                       # dictionary containing letter counts of the word to guess
        self.dictionary = enchant.Dict(self.language)                              # spellchecker

    def load_dictionary2list(self, filename:str, download_url:str) -> Tuple[List[str], int]:
        '''
        Reads a dictionary of five-letter words from a txt file onto a list.
        If the file doesn't exist, it tries to download it from a URL.

        Parameters:
            filename (str): The method looks for this filename in the current
                directory, which should store the words.
            download_url (str): If the filename mentioned is not found the method
                tries to download the required data from this URL and saves it
                under filename.

        Returns:
            Tuple(value1, value2):
            value1: a list of strings containing all words in the loaded dictionary.
            value2: the length of this list.
        '''

        dictionary = enchant.Dict(self.language)  # spellchecker

        if not os.path.isfile(filename):      # download file if it's not there
            res = req.get(download_url)

            if res.status_code == 404:
                print("ERROR: URL for downloading dictionary \"" + download_url + "\" not found. Please fix this and try again.")    #to check whether the URL is valid
                sys.exit()

            with open(filename, 'wb') as f:
                f.write(res.content)

        # opening the file and reading the words onto a list:
        words_file = open(filename)
        words_list = []
        for line in words_file:
            if dictionary.check(line[:-1]):        # to avoid words that the spellchecker doesnt know of
                words_list.append(line[:-1])
        words_file.close()

        return words_list, len(words_list)

    def reset_game(self) -> None:
        '''
        Resets the game (by resetting class variables in the Game object) if the
        user wants to play again. Picks another word to guess.
        '''

        self.tries = 0
        self.found = False
        self.guess = None
        self.results = [["_" for _ in range(5)] for _ in range(6)]
        self.kb = Keyboard()

        self.true_word = self.words_list[random.randint(0, self.count)]              # word to guess
        self.true_word_dict = self.word2dict(self.true_word)

    def play(self) -> None:
        '''
        Defines the structure of a game.

        Six tries are allowed.

        First, a valid guess is taken in from the user using another method, which
        ensures that the input is a five-character string which is a dictionary
        word.

        If the guess isn't '0' (exit code), exact matches (correct letters in
        correct positions) are checked for first. Then other matches (correct
        letters in incorrect) positions are checked for.

        This updates the self.results object which stores the guessed word in a
        certain round, the keybard object and the self.true_word_dict variable
        which stores the number of letters in the true word that haven't been
        guessed yet.

        The updated results object and keyboard are also printed on the console.

        In the end, the self.true_word_dict dictionary is reset for the next
        guess.

        If the self.true_word_dict dictionary is empty after checking for exact
        matches, then the user has made the correct guess. The game ends.

        If in six tries, no correct guess has been made, the game ends.
        '''

        while not self.found and self.tries < 6 and self.guess != '0':   # '0' is the code for terminating the program

            self.guess = self.get_guess()      # get a valid Guess

            if self.guess != '0':
                self.check_exact_matches()     # exact matches are prioritised

                if not self.true_word_dict:    # an empty dictionary at this point means all letters have been guessed correctly
                    self.found = True
                    print('Correct guess! Number of tries = ' + str(self.tries))

                self.check_other_matches()     # other matches are checked for

                self.print_results()           # printing results and the updated keyboard
                self.kb.print()

                self.tries += 1

                self.true_word_dict = self.word2dict(self.true_word)      # reset true_word_dict

        if self.guess == '0':
            print('QUIT')
        elif not self.found:
            print(':( The word was', self.true_word)

    def check_exact_matches(self) -> None:
        '''
        Checks each of the five letters in the guess for an exact match with the
        true word. If there is a match, it updates the results and keyboard objects
        to display the appropriate attributes (green colour and strikethrough
        for the keyboard). It also updates the self.true_word_dict dicitonary using
        another method which decrements the count of a certain letter in the
        dicitonary object.
        '''
        for i in range(5):
            if self.guess[i] == self.true_word[i]:
                self.results[self.tries][i] = self.attributes['green'] + self.attributes['bold'] + self.guess[i].upper() + self.attributes['end']
                self.kb.mark(self.guess[i], 'green')
                self.update_true_word_dict(self.guess[i])         # update letter count for true word

    def check_other_matches(self) -> None:
        '''
        Checks for matches that are not in the correct positions (exact mathces
        will have already been marked).

        For each letter in the guess that doesn't have an exact match, if
        the letter is still available in self.true_word_dict, it's marked
        yellow in the results object and in the keybard (along with a
        strikethrough). self.true_word_dict is also updated.

        If the letter isn't available, it's still added to the results object
        and marked with a strikethrough in the keyboard.

        '''
        for i in range(5):
            if self.results[self.tries][i] == "_":                    # an empty position means there is no exact match here
                if self.guess[i] in self.true_word_dict:              # the letter is available
                    self.results[self.tries][i] = self.attributes['yellow'] + self.attributes['bold'] + self.guess[i].upper() + self.attributes['end']
                    self.kb.mark(self.guess[i], 'yellow')
                    self.update_true_word_dict(self.guess[i])         # update letter count for true word

                else:                                                 # the letter isn't available
                    self.results[self.tries][i] = self.guess[i]
                    self.kb.mark(self.guess[i], 'none')

    def get_guess(self) -> str:
        '''
        Prompts the user to enter a five-letter guess until it gets a five-letter
        word which is validated by the dictionary.

        Parameters: None.
        Returns:
            str: The user's five-letter guess.
        '''

        guess = None
        while not guess:
            guess = input('Please enter a guess (5 letters):  (or enter 0 to quit)')
            if guess != '0':
                if len(guess) != 5:
                    print('Guess must consist of 5 letters')
                    guess = None
                elif not self.dictionary.check(guess):
                    print('Word not recognised')
                    guess = None
        return guess

    def word2dict(self, word:str) -> dict:
        '''
        Converst a string to a dictionary containing the counts of its characters.

        Parameters: word (str): the input string.
        Returns: dict.
        '''
        output = dict()
        for ch in word:
            if ch in output:
                output[ch] += 1
            else:
                output[ch] = 1
        return output

    def update_true_word_dict(self, letter:str) -> None:
        '''
        Decrements the count of the letter in self.true_word_dict. If the
        original count is 1, the letter is popped from the dictionary.

        Parameters: letter (str).
        Returns: None.
        '''
        if self.true_word_dict[letter] == 1:      # update dict
            self.true_word_dict.pop(letter)
        else:
            self.true_word_dict[letter] -= 1

    def print_results(self) -> None:
        '''
        Prints results in a 5x6 grid
        '''
        for line in self.results:
            for ch in line:
                print(ch, end=" ")
            print("")


if __name__ == "__main__":

    # create game object:
    this_game = Game()

    # play game:
    play = True
    while play:
        this_game.play()
        response = input('Would you like to play again? (y/n)')
        if response.lower() == 'y':
            play = True
            this_game.reset_game()
        else:
            play = False
