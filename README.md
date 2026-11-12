# Python 进阶

一门课一个仓库。每一集是一个独立目录，在该目录里安装并运行。

```bash
git clone https://github.com/coder-thor/python-advanced
cd python-advanced/03-event-loop
uv sync
uv run event-loop-demo
```

| 目录 | 命令 |
| --- | --- |
| `01-type-annotations` | `uv run python-annotations` |
| `02-pydantic` | `uv run pydantic-demo` |
| `03-event-loop` | `uv run event-loop-demo` |

需要 Python 3.12 或以上。没有的话，`uv sync` 会安装。
