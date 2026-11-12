def get_character(name: str) -> dict: 
    return {"name": name}


class GetCharacterArgs:
    name: str
    star: int = 5


def main() -> None:
    print("1. 函数上的注解 get_character.__annotations__")
    print("  ", get_character.__annotations__)

    print("2. 类上的注解 GetCharacterArgs.__annotations__")
    print("  ", GetCharacterArgs.__annotations__)

    print("3. 注解写的是 str，传入数字 1")
    print("  ", get_character(1))
