# wordmaster
My implementation of a wordle-like game that lets you guess a word in six tries, with a twist. Instead of only using five letter words, it lets the user choose a length of word (from 3 to 8).

The words are loaded from the "words_dict.txt" file, which I have created by grouping words from [this](https://github.com/dwyl/english-words) repository according to length.

Python version used: 3.8.

## Requirements

The only external libraries used are enchant and requests. Requirements can be installed using the requirements file as shown below,

```bash
pip install -r requirements.txt
```

or by installing enchant(pyenchant) and requests manually.

## Usage

Clone this repository to your local drive or just download the 'wordmaster.py' file, and run the file.

```bash
python wordmaster.py
```
