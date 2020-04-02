from cs50 import get_float


def main():
    while True:
        # getting input
        change = get_float('Change owed: ')

        # converting to cents
        change = int(change * 100)

        # check for correct usage
        if change > 0:
            break

    # we start with zero coins/change
    coins = 0

    # start performing checks from largest to smallest coin
    while change >= 25:
        change = change - 25
        coins += 1

    while change >= 10:
        change = change - 10
        coins += 1

    while change >= 5:
        change = change - 5
        coins += 1

    while change >= 1:
        change = change - 1
        coins += 1

    # print output
    print(coins)


if __name__ == "__main__":
    main()