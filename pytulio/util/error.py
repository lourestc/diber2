import sys

#Print an error message
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
