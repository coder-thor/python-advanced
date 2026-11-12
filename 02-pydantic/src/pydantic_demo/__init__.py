import json

from pydantic import BaseModel, ConfigDict, Field, ValidationError, validate_call


def show_error(e: ValidationError) -> None:
    for err in e.errors():
        print("    ", err["type"], err["loc"], err["msg"])


# ---------- 能力一：运行时校验 ----------

class Character(BaseModel):
    name: str
    level: int


def demo_model() -> None:
    print("1. BaseModel：创建对象的时候校验")
    print("   传对的:", Character(name="胡桃", level=90))
    try:
        Character(name={"a": 1}, level="满级")
    except ValidationError as e:
        print("   传错的: 抛出 ValidationError")
        show_error(e)


class StrictCharacter(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    name: str


def demo_assignment() -> None:
    print("2. 创建完再赋值，默认不校验")
    c = Character(name="胡桃", level=90)
    c.name = 123
    print("   c.name = 123 之后:", repr(c.name))
    s = StrictCharacter(name="胡桃")
    try:
        s.name = 123
    except ValidationError as e:
        print("   开了 validate_assignment 再赋值:")
        show_error(e)


def plain_get_character(name: str) -> str:
    return f"查到了 {name}"


@validate_call
def get_character(name: str) -> str:
    """按中文名查本地角色表。"""
    return f"查到了 {name}"


def demo_validate_call() -> None:
    print("3. 函数：不加装饰器不管，加了 @validate_call 才管")
    print("   普通函数传 1:", plain_get_character(1))
    print("   @validate_call 传 '胡桃':", get_character("胡桃"))
    try:
        get_character({"a": 1})
    except ValidationError as e:
        print("   @validate_call 传 {'a': 1}: 函数体没执行")
        show_error(e)
    print("   raw_function 是原函数，绕过校验:", get_character.raw_function(1))


# ---------- 宽松模式 / 严格模式 ----------

class Level(BaseModel):
    level: int


class Name(BaseModel):
    name: str


class LooseName(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    name: str


def try_validate(label: str, model: type[BaseModel], data: dict, **kwargs) -> None:
    try:
        print(f"   {label}:", model.model_validate(data, **kwargs))
    except ValidationError as e:
        print(f"   {label}: 报错")
        show_error(e)


def demo_lax_strict() -> None:
    print("4. 宽松模式是默认的，但不是什么都转")
    try_validate("int 字段传 '80'", Level, {"level": "80"})
    try_validate("int 字段传 80.5", Level, {"level": 80.5})
    try_validate("str 字段传 80", Name, {"name": 80})
    try_validate("开 coerce_numbers_to_str 后 str 传 80", LooseName, {"name": 80})
    try_validate("strict=True 时 int 传 '80'", Level, {"level": "80"}, strict=True)


# ---------- 能力二：生成 JSON Schema ----------

class GetCharacterArgsNoDesc(BaseModel):
    name: str


class GetCharacterArgs(BaseModel):
    """按中文名查本地角色表的星级、元素、武器类型。"""

    name: str = Field(description="角色的中文名，比如“胡桃”")
    level: int = 90


def demo_json_schema() -> None:
    print("5. 生成 JSON Schema，就是 tool 定义里的 parameters")
    print("   只写 name: str，没有描述:")
    print("    ", json.dumps(GetCharacterArgsNoDesc.model_json_schema(), ensure_ascii=False))
    print("   加上三引号描述和 Field(description=...):")
    print("    ", json.dumps(GetCharacterArgs.model_json_schema(), ensure_ascii=False))

    schema = GetCharacterArgs.model_json_schema()
    # 类的描述挪到 function.description，parameters 里只留参数
    description = schema.pop("description")
    tool = {
        "type": "function",
        "function": {
            "name": "get_character",
            "description": description,
            "parameters": schema,
        },
    }
    print("   拼成发给 LLM 的 tool:")
    print(json.dumps(tool, ensure_ascii=False, indent=2))


# ---------- Agent 里的用法：先校验，再执行 ----------

# 模拟 LLM 返回的 tool_calls[0].function.arguments，真实场景它就是一段字符串
FAKE_ARGUMENTS = [
    '{"name": "胡桃", "level": "80"}',
    '{"name": 1}',
    '{"level": 90}',
    '{"name": "胡桃"',
]


def run_tool(arguments: str) -> str:
    try:
        args = GetCharacterArgs.model_validate_json(arguments)
    except ValidationError as e:
        # 第 3 节会讲：错误写进 tool 消息，交给模型重试
        return f"参数错误: {e.errors()[0]['type']}"
    return f"执行工具: name={args.name!r}, level={args.level!r}"


def demo_agent() -> None:
    print("6. 模型给的 arguments 先校验，再执行工具")
    for raw in FAKE_ARGUMENTS:
        print("   模型返回:", raw)
        print("     ->", run_tool(raw))


# ---------- 序列化 ----------

def demo_dump() -> None:
    print("7. 把对象转回 dict / JSON 字符串（v2 写法）")
    args = GetCharacterArgs(name="胡桃")
    print("   model_dump():", args.model_dump())
    print("   model_dump_json():", args.model_dump_json())


# ---------- 原理 ----------

def demo_internals() -> None:
    print("8. 原理：包装后的新函数会提前调用 Rust 校验器进行验证")
    print("   类上的 core schema，type 是:", Character.__pydantic_core_schema__["type"])
    print("   类上的校验器:", type(Character.__pydantic_validator__))
    print("   get_character 是包装后的新函数，原函数在 __wrapped__:", get_character.__wrapped__ is get_character.raw_function)


def main() -> None:
    for demo in (
        demo_model,
        demo_assignment,
        demo_validate_call,
        demo_lax_strict,
        demo_json_schema,
        demo_agent,
        demo_dump,
        demo_internals,
    ):
        demo()
        print()
