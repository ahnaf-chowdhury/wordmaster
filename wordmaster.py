import enchant
import requests as req
import random
import os.path

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
            print(i*" ", end="")
            for key in line:
                print(key, end=' ')
            print("")

    def mark(self, char, colour):            # marks letters/keys
        for i in range(len(self.keys)):
            for j in range(len(self.keys[i])):
                if self.keys[i][j][0] == char:
                    if self.keys[i][j][0:2] != "\0":  # not already changed
                        self.keys[i][j] = self.attributes[colour] + self.keys[i][j] + self.attributes['striketh'] + self.attributes['end']

def load_dictionary2list(filename):
    '''reads dict of 5 letter words onto a list'''

    # spellchecker
    dictionary = enchant.Dict(LANG) # spellchecker

    if not os.path.isfile(filename):      # download file if it's not there
        url = "https://raw.githubusercontent.com/charlesreid1/five-letter-words/master/sgb-words.txt"
        res = req.get(url)
        with open(filename, 'wb') as f:
            f.write(res.content)

    flw_file = open(filename)
    flw_list = []
    for line in flw_file:        # count will have index of last word
        if dictionary.check(line[:-1]):        # to avoid words that the spellchecker doesnt know of
            flw_list.append(line[:-1])
    flw_file.close()
    return flw_list, len(flw_list)-1

def word2dict(word):
    '''converts word to dict representing letter counts'''
    output = dict()
    for ch in word:
        if ch in output:
            output[ch] += 1
        else:
            output[ch] = 1
    return output

def print_results(res):
    '''print results in a 5x6 grid'''
    for line in res:
        for ch in line:
            print(ch, end=" ")
        print("")

class Game:
    def __init__(self):
        self.tries = 0
        self.found = False
        self.guess = None
        self.results = [["_" for _ in range(5)] for _ in range(6)]
        self.kb = Keyboard()

        self.flw, self.count = load_dictionary2list('five_letter_words.txt')   # load dictionary of 5-letter words
        self.true = self.flw[random.randint(0, self.count)]              # word to guess
        self.true_dict = word2dict(self.true)
        self.dictionary = enchant.Dict(LANG) # spellchecker

        self.attributes = {'green':'\033[92m',
              'yellow':'\033[93m',
              'bold':'\033[1m',
              'underline':'\033[4m',
              'end':'\033[0m',
              'striketh':'\u0336'}   # use strikethrough after string

    def reset_game(self):
        self.tries = 0
        self.found = False
        self.guess = None
        self.results = [["_" for _ in range(5)] for _ in range(6)]
        self.kb = Keyboard()

        self.true = self.flw[random.randint(0, self.count)]              # word to guess
        self.true_dict = word2dict(self.true)

    def play(self):

        while not self.found and self.tries < 6 and self.guess != '0':

            self.guess = self.get_guess()      # get a valid Guess

            if self.guess != '0':
                self.check_exact_matches()
                self.check_other_matches()

                print_results(self.results)
                self.kb.print()

                self.tries += 1

                if not self.true_dict:
                    self.found = True
                    print('Correct guess! Number of tries = ' + str(self.tries))

                self.true_dict = word2dict(self.true)      # reset true_dict

        if self.guess == '0':
            print('QUIT')
        elif not self.found:
            print(':( The word was', self.true)

    def check_exact_matches(self):
        for i in range(5):
            if self.guess[i] == self.true[i]:
                self.results[self.tries][i] = self.attributes['green'] + self.attributes['bold'] + self.guess[i].upper() + self.attributes['end']
                self.kb.mark(self.guess[i], 'green')
                self.update_dict(self.guess[i])         # update letter count for true word
            else:
                self.results[self.tries][i] = "_"

    def check_other_matches(self):
        for i in range(5):
            if self.results[self.tries][i] == "_":
                if self.guess[i] in self.true_dict:
                    self.results[self.tries][i] = self.attributes['yellow'] + self.attributes['bold'] + self.guess[i].upper() + self.attributes['end']
                    self.kb.mark(self.guess[i], 'yellow')
                    self.update_dict(self.guess[i])         # update letter count for true word

                else:
                    self.results[self.tries][i] = self.guess[i]
                    self.kb.mark(self.guess[i], 'none')

    def update_dict(self, letter):
        if self.true_dict[letter] == 1:      # update dict
            self.true_dict.pop(letter)
        else:
            self.true_dict[letter] -= 1

    def get_guess(self):
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


if __name__ == "__main__":

    # # load 5-letter-word dictionary
    # flw = load_dictionary2list('five_letter_words.txt')

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
