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

class Keyboard:
    def __init__(self):
        self.keys = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                    ['z', 'x', 'c', 'v', 'b', 'n', 'm']]

        self.attributes = {'green':'\033[92m',     # visual attributes of a string
              'yellow':'\033[93m',
              'bold':'\033[1m',
              'underline':'\033[4m',
              'end':'\033[0m',
              'none':'',
              'striketh':'\u0336'}   # use strikethrough after string

    def print(self):           # print keyboard
        for i, line in enumerate(self.keys):
            print(i*" ", end="")             # spacing to match a real keyboard's arrangement
            for key in line:
                print(key, end=' ')
            print("")

    def mark(self, char:str, colour:str):            # marks letters/keys
        for i in range(len(self.keys)):
            for j in range(len(self.keys[i])):
                if self.keys[i][j][0] == char:
                    if self.keys[i][j][0:2] != "\0":  # not already changed
                        self.keys[i][j] = self.attributes[colour] + self.keys[i][j] + self.attributes['striketh'] + self.attributes['end']

class Game:
    def __init__(self):
        self.tries = 0
        self.found = False
        self.guess = None
        self.results = [["_" for _ in range(5)] for _ in range(6)]
        self.kb = Keyboard()
        self.words_list, self.count = self.load_dictionary2list('five_letter_words.txt')   # load dictionary of 5-letter words
        self.true_word = self.words_list[random.randint(0, self.count)]              # word to guess
        self.true_word_dict = self.word2dict(self.true_word)
        self.dictionary = enchant.Dict(LANG)                              # spellchecker
        self.attributes = {'green':'\033[92m',
              'yellow':'\033[93m',
              'bold':'\033[1m',
              'underline':'\033[4m',
              'end':'\033[0m',
              'striketh':'\u0336'}   # use strikethrough after string

    def load_dictionary2list(self, filename:str) -> Tuple[List[str], int]:
        '''reads dict of 5 letter words onto a list'''

        dictionary = enchant.Dict(LANG) # spellchecker

        if not os.path.isfile(filename):      # download file if it's not there
            url = "https://raw.githubusercontent.com/charlesreid1/five-letter-words/master/sgb-words.txt"
            res = req.get(url)
            with open(filename, 'wb') as f:
                f.write(res.content)

        words_file = open(filename)
        words_list = []
        for line in words_file:        # count will have index of last word
            if dictionary.check(line[:-1]):        # to avoid words that the spellchecker doesnt know of
                words_list.append(line[:-1])
        words_file.close()
        return words_list, len(words_list)-1

    def reset_game(self) -> None:
        self.tries = 0
        self.found = False
        self.guess = None
        self.results = [["_" for _ in range(5)] for _ in range(6)]
        self.kb = Keyboard()

        self.true_word = self.words_list[random.randint(0, self.count)]              # word to guess
        self.true_word_dict = self.word2dict(self.true_word)

    def play(self) -> None:

        while not self.found and self.tries < 6 and self.guess != '0':   # '0' is the code for terminating the program

            self.guess = self.get_guess()      # get a valid Guess

            if self.guess != '0':
                self.check_exact_matches()     # exact matches are prioritised
                self.check_other_matches()

                self.print_results()
                self.kb.print()

                self.tries += 1

                if not self.true_word_dict:
                    self.found = True
                    print('Correct guess! Number of tries = ' + str(self.tries))

                self.true_word_dict = self.word2dict(self.true_word)      # reset true_dict

        if self.guess == '0':
            print('QUIT')
        elif not self.found:
            print(':( The word was', self.true_word)

    def check_exact_matches(self) -> None:
        for i in range(5):
            if self.guess[i] == self.true_word[i]:
                self.results[self.tries][i] = self.attributes['green'] + self.attributes['bold'] + self.guess[i].upper() + self.attributes['end']
                self.kb.mark(self.guess[i], 'green')
                self.update_true_word_dict(self.guess[i])         # update letter count for true word
            else:
                self.results[self.tries][i] = "_"

    def check_other_matches(self) -> None:
        for i in range(5):
            if self.results[self.tries][i] == "_":
                if self.guess[i] in self.true_word_dict:
                    self.results[self.tries][i] = self.attributes['yellow'] + self.attributes['bold'] + self.guess[i].upper() + self.attributes['end']
                    self.kb.mark(self.guess[i], 'yellow')
                    self.update_true_word_dict(self.guess[i])         # update letter count for true word

                else:
                    self.results[self.tries][i] = self.guess[i]
                    self.kb.mark(self.guess[i], 'none')

    def get_guess(self) -> str:
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
        '''converts word to dict representing letter counts'''
        output = dict()
        for ch in word:
            if ch in output:
                output[ch] += 1
            else:
                output[ch] = 1
        return output

    def update_true_word_dict(self, letter:str) -> None:
        if self.true_word_dict[letter] == 1:      # update dict
            self.true_word_dict.pop(letter)
        else:
            self.true_word_dict[letter] -= 1

    def print_results(self) -> None:
        '''print results in a 5x6 grid'''
        for line in self.results:
            for ch in line:
                print(ch, end=" ")
            print("")


if __name__ == "__main__":

    LANG = "en_US"          # the 5-letter-word list contains "en_US" words

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
