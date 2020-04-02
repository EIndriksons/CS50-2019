from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""

    # we can use split function to split strings by \n separator
    return compare(a.split(sep="\n"), b.split(sep="\n"))


def sentences(a, b):
    """Return sentences in both a and b"""

    # as per documentation - we run sent_tokenize on each of the lists
    return compare(sent_tokenize(a), sent_tokenize(b))


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    # we run divide() function (see below)
    return compare(divide(a, n), divide(b, n))


def compare(a, b):
    """Because many functions use some sort of comparison logic I decided to implement it separately"""

    # creates output list where we will place our results
    output = []

    # then we compare to get similar lines
    for ai in a:
        for bi in b:
            if ai == bi and ai not in output:
                # if similarity found and it is not already present in the list
                # append it as a new item to the list
                output.append(ai)

    return output


def divide(a, n):
    """As per substrings requirement - splits string in a list"""

    # creates output list where we will place our results
    output = []

    # calculate the required split for the loop
    split = len(a) - n + 1

    # the loop will select starting and ending numbers in the string which whill
    # then be added to the list
    for i in range(split):
        output.append(a[i:n + i])

    return output