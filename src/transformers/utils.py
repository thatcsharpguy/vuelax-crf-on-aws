import string

PUNCTUATION_SET = set(string.punctuation)


def is_punctuation(token):
    return token in PUNCTUATION_SET


def is_numeric(token):
    try:
        float(token.replace(",", ""))
        return True
    except ValueError:
        return False
