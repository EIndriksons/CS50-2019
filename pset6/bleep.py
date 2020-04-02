from cs50 import get_string
from sys import argv


def main():
    # ensuring proper usage
    if len(argv) != 2:
        print('Usage: python bleep.py dictionary')
        exit(1)

    # initializing a set
    # according to stackoverflow - sets are faster when it comes to checking if an element exists inside of it
    # while lists are faster when iterating over it
    banned_words = set()

    # open banned word file
    with open(argv[1], 'r') as f:
        for row in f:
            # add banned words to the set and remove newline element
            banned_words.add(str.strip(row))

    # ask for input
    plaintext = get_string('What message would you like to censor?\n')

    # split individual words in a list
    plaintext = plaintext.split()

    # iterating over words and checking with banned words
    for i, word in enumerate(plaintext):
        for banned_word in banned_words:
            # checking word against banned word
            if str.lower(word) == banned_word:
                # if the word is banned replace it with stars
                plaintext[i] = censor(len(word))

    # prints censored text
    print(' '.join(plaintext))


# returns a string of stars of the required lenght
def censor(lenght):

    # list for stars
    li = []

    # add stars to the list
    i = 0
    while i < lenght:
        li.append('*')
        i += 1

    return ''.join(li)


if __name__ == "__main__":
    main()
