import sys
from cs50 import get_string


def main():
    # ensure proper usage
    if len(sys.argv) != 2:
        print('Usage: python vigenere.py k')
        exit(1)

    if not sys.argv[1].isalpha():
        print('Usage: python vigenere.py k')
        exit(1)

    # get key
    key = sys.argv[1]
    key_lenght = len(key)
    key_index = 0

    # get plaintext
    plaintext = get_string('plaintext: ')
    ciphertext = ['ciphertext: ']

    # start encryption
    for c in plaintext:
        # check if key index is larger than key lenght to start again
        if key_index >= key_lenght:
            key_index = 0

        if c.isalpha():
            # translate key
            k = ord(key[key_index % key_lenght].lower()) - 97
            key_index += 1

            # append encrypted char to the list
            ciphertext.append(encrypt(c, k))
        else:
            # if not in alphabet, just add to list
            ciphertext.append(c)

    # print outcome
    print(''.join(ciphertext))


def encrypt(c, k):
    if c.isupper():
        return chr(((ord(c) - 65 + k) % 26) + 65)
    else:
        return chr(((ord(c) - 97 + k) % 26) + 97)


if __name__ == '__main__':
    main()