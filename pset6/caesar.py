from cs50 import get_string
from sys import argv


def main():
    # ensuring proper usage
    if len(argv) != 2:
        print('Usage: python caesar.py k')
        exit(1)

    # ensuring proper key
    if int(argv[1]) < 0:
        print('Usage: no negative numbers')
        exit(2)

    # acquire key
    k = int(argv[1])

    # get message & initialize an array
    message = get_string('plaintext: ')
    ciphertext = []

    # if char is alphabetic, then encrypt, else do not change
    for char in message:
        if char.isalpha():
            ciphertext.append(encrypt(char, k))
        else:
            ciphertext.append(char)

    # print output
    print('ciphertext: ', end='')
    print(''.join(ciphertext))


def encrypt(char, k):
    # if char is upper, transform CAPS text, else small
    if char.isupper():
        return chr(((ord(char) - 65 + k) % 26) + 65)
    else:
        return chr(((ord(char) - 97 + k) % 26) + 97)


if __name__ == '__main__':
    main()