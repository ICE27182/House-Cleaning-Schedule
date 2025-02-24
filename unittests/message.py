def yellow(*value:object, end="\n") -> None:
    print("\033[93m", end="")
    print(*value, end = end)
    print("\033[0m", end="")

def dark_yellow(*value:object, end="\n") -> None:
    print("\033[33m", end="")
    print(*value, end = end)
    print("\033[0m", end="")

def red(*value:object, end="\n") -> None:
    print("\033[91m", end="")
    print(*value, end = end)
    print("\033[0m", end="")

def dark_red(*value:object, end="\n") -> None:
    print("\033[31m", end="")
    print(*value, end = end)
    print("\033[0m", end="")

def green(*value:object, end="\n") -> None:
    print("\033[92m", end="")
    print(*value, end = end)
    print("\033[0m", end="")

def dark_green(*value:object, end="\n") -> None:
    print("\033[32m", end="")
    print(*value, end = end)
    print("\033[0m", end="")

def blue(*value:object, end="\n") -> None:
    print("\033[94m", end="")
    print(*value, end = end)
    print("\033[0m", end="")

def dark_blue(*value:object, end="\n") -> None:
    print("\033[34m", end="")
    print(*value, end = end)
    print("\033[0m", end="")