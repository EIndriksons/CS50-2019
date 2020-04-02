import sys
import crypt


def main():
    # ensuring proper usage
    if len(sys.argv) != 2:
        print('Usage: python crack.py hash')
        exit(1)

    # get hash
    pass_hash = sys.argv[1]

    # get salt from hash
    salt = pass_hash[0:2]

    # initialize alphabet
    # using frequency table from http://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
    alphabet = ' eEtTaAoOiInNsSrRhHdDlLuUcCmMfFyYwWgGpPbBvVkKxXqQjJzZ'

    # building combinations of passwords starting from fifth char
    for char_5 in alphabet:
        for char_4 in alphabet:
            for char_3 in alphabet:
                for char_2 in alphabet:
                    for char_1 in alphabet[1:]:
                        password = f'{char_1}{char_2}{char_3}{char_4}{char_5}'.strip()

                        # hash the password and check if the created hash is equal to the one given
                        if crypt.crypt(password, salt) == pass_hash:
                            print(password)
                            exit(0)

    # we failed
    print("We ain't found shit, sir!")
    exit(2)


if __name__ == '__main__':
    main()