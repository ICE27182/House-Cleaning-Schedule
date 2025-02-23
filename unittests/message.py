def yellow(*value:object) -> None:
    print("\033[93m", end="")
    print(*value)
    print("\033[0m", end="")

def red(*value:object) -> None:
    print("\033[91m", end="")
    print(*value)
    print("\033[0m", end="")

def green(*value:object) -> None:
    print("\033[92m", end="")
    print(*value)
    print("\033[0m", end="")