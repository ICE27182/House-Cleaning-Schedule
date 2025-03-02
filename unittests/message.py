

DEFAULT_COLOR = "\033[0m"

YELLOW = "\033[93m"
def yellow(*value:object, end="\n") -> None:
    print(YELLOW, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")
DARK_YELLOW = "\033[33m"
def dark_yellow(*value:object, end="\n") -> None:
    print(DARK_YELLOW, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")
RED = "\033[91m"
def red(*value:object, end="\n") -> None:
    print(RED, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")
DARK_RED = "\033[31m"
def dark_red(*value:object, end="\n") -> None:
    print(DARK_RED, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")
GREEN = "\033[92m"
def green(*value:object, end="\n") -> None:
    print(GREEN, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")
DARK_GREEN = "\033[32m"
def dark_green(*value:object, end="\n") -> None:
    print(DARK_GREEN, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")
BLUE = "\033[94m"
def blue(*value:object, end="\n") -> None:
    print(BLUE, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")
DARK_BLUE = "\033[34m"
def dark_blue(*value:object, end="\n") -> None:
    print(DARK_BLUE, end="")
    print(*value, end = end)
    print(DEFAULT_COLOR, end="")

