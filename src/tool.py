

def str_to_int(int_string):
    value = 0

    try:
        value = int(int_string)
    except ValueError:
        value = 0

    return value
