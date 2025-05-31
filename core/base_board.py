def base() -> dict:
    return {f"{col}{row}": "empty" for row in range(1, 9) for col in "abcdefgh"}
