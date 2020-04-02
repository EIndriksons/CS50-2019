from cs50 import get_int


def main():
    while True:
        # getting input
        height = get_int('Height: ')

        # check for correct usage
        if height >= 1 and height <= 8:
            break

    for n in range(height):
        # print empty spaces height - n - 1
        for ni in range(height - n - 1):
            print(' ', end='')

        # print left hashes n + 1
        for nj in range(n + 1):
            print('#', end='')

        # print two empty spaces
        print('  ', end='')

        # print right hashes n + 1
        for nx in range(n + 1):
            print('#', end='')

        # print new line
        print()


if __name__ == "__main__":
    main()