from cs50 import get_int


def main():
    # get input
    number = get_int('Number: ')

    # check number
    if valid(number) == True:
        if len(str(number)) == 15 and str(number)[:2] in ['34', '37']:
            print('AMEX')
        elif len(str(number)) == 16 and str(number)[:2] in ['51', '52', '53', '54', '55']:
            print('MASTERCARD')
        elif len(str(number)) in [13, 16] and str(number)[:1] in ['4']:
            print('VISA')
        else:
            print('INVALID')
    else:
        print('INVALID')


def valid(number):
    # convert integer to string
    number = str(number)

    # initialize values
    product = 0
    odd = 1

    # determine if lenght is even or odd
    if len(number) % 2 == 0:
        odd = 0

    # get every second character reversed from the back
    for c in reversed(range(odd, len(number), 2)):

        # multiply digit by two
        multiple = int(number[c]) * 2

        if multiple >= 10:
            # check if the digit is larger or equals 10
            product = product + sum_integers(multiple)

        else:
            # else add to product sum
            product = product + multiple

    if odd == 1:
        odd = 0
    else:
        odd = 1

    # add to product every other digit
    for x in reversed(range(odd, len(number), 2)):

        # sum together
        product = product + int(number[x])

    return str(product).endswith('0')


def sum_integers(value):
    # convert value to integer
    value = str(value)

    # initialize sum
    sumval = 0

    # sum all digits
    for c in value:
        sumval = sumval + int(c)

    return sumval


if __name__ == '__main__':
    main()