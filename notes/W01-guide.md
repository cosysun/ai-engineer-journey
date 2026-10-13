# W01 学习引导 · 从 organize CLI 反推现代 Python 工具链

不是教程，是**对着你写的代码**讲每个决定为什么这么写、以及哪里其实可以更简单。
所有结论我都跑过验证，标注 `[已验证]` 的是实验结果，`[待验证]` 是我没实测的推断。

配套代码：[projects/w01-organize](../projects/w01-organize)
周记：[log/W01.md](../log/W01.md)

---

## 0. 这一周真正在学什么

不是"学会 uv / typer / pydantic"。是建立一条可复用的工程链路：

```
声明依赖 → 环境隔离 → CLI 入口 → 类型化配置 → 校验前置 → 副作用 → 测试
```

这条链每周都会用到。W01 的价值是把每个环节都踩一遍，下次 W03 接 LLM API 时
直接复用，不用再想"项目该怎么组织"。

`organize` 这个工具本身不重要。它可能一辈子不会被真用上。

---

## 1. uv：为什么不是 pip

你肯定用过 `pip install` + `venv`。uv 的差异在这三点：

| | pip + venv | uv |
|---|---|---|
| 装依赖 | `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`（3 步） | `uv sync`（1 步，自动建 venv） |
| 锁版本 | 手写 requirements，`pip freeze` 会带上一堆无关包 | `uv.lock` 自动记录**精确版本 + wheel hash** |
| 跑命令 | 先 activate | `uv run organize` 自动识别项目环境 |

```bash
uv init --name organize    # 生成 pyproject.toml + src 布局
uv add typer pydantic      # 写依赖并自动 lock
uv add --dev pytest        # 开发依赖进 [dependency-groups].dev
uv run organize --help     # 不用 activate
```

**`uv run` 是最省事的一点**——它让你永远不需要记得"我是不是已经 activate 了"。

### 一个你第二天就会撞到的坑

我在这上面浪费了十分钟 `[已验证]`：

```toml
[project.scripts]
organize = "organize:main"     # ← uv init 默认生成
```

`uv init` 会在 `src/organize/__init__.py` 里放一个占位的 `main()`。
你把真实实现写进 `main.py`，但这个 entrypoint 还指向 `__init__.py` 里的旧函数——
于是跑出来是 `Hello from organize!`，**代码看起来完全没生效**。

修法二选一：
```toml
organize = "organize:app"      # A：`__init__.py` 里 `from organize.main import app`
organize = "organize.main:app" # B：直接指向模块
```

> **排查口诀：CLI 起不来 / 行为不对，先查 entrypoint 指向哪个函数。**
> 这不是代码 bug，是配置指错了地方。

---

## 2. pydantic：把校验挡在副作用之前

看你的 `Config`（main.py:23-30）：

```python
class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Path = Field(description="待整理的目录")
    dest: Path = Field(description="归档输出目录")
    strategy: Strategy = Strategy.ext
    dry_run: bool = False
    min_size: int = Field(default=0, ge=0, description="小于该字节的文件跳过")
```

### 2.1 `Field(description=...)` 不给 default = 必填

`[已验证]` 只写 `Field(description="x")` 没有 `default`，实例化时报错 `missing`。
`description` 只是文档，**不等于默认值**。

你这里 `source` / `dest` 是必填——正确。但要注意是"碰巧正确"：
如果哪天写成 `Field(description="x", default=None)`，类型就变成 `Path | None`，
后面 `cfg.source.is_dir()` 会在 `None` 上炸（而且是 `AttributeError`，看不懂的错）。

### 2.2 `ge=0` 这类约束是免费的

一行 `ge=0` 就挡住了 `--min-size -5`。手写得写：
```python
if min_size < 0: raise ValueError(...)   # 三行，还容易漏
```

### 2.3 错误信息怎么读

`[已验证]` `ValidationError.errors()` 返回的是 dict 列表：
```python
{"loc": ("min_size",), "msg": "Input should be greater than or equal to 0",
 "type": "greater_than_equal"}
```

你 main.py:56-58 的写法：
```python
where = ".".join(str(x) for x in err["loc"])
```
是把 `("min_size",)` 变成 `"min_size"`。**嵌套字段时才有意义**（`("db","host")` → `"db.host"`），
你这个扁平 Config 其实用不上，但留着无害，以后配置变复杂就省事了。

### 2.4 `raise ... from None` 在压什么

`[已验证]` 不用 `from None` 时，Python 会打印 "During handling of the above exception, another exception occurred"，
把 pydantic 的整条 traceback 也带上。用户只想看"配置错了"，不想看 pydantic 内部怎么发现的。

`from None` 设置 `__suppress_context__ = True`，隐藏上下文链。

---

## 3. typer：类型注解就是 CLI 定义

```python
@app.command()
def main(
    source: Path = typer.Argument(..., help="待整理的目录"),
    strategy: Strategy = typer.Option(Strategy.ext, "--by", help="..."),
    dry_run: bool = typer.Option(False, "--dry-run", help="..."),
) -> None:
```

typer 从**类型注解 + 默认值**推导 CLI：
- `Path` → 接受路径字符串并转成 `Path` 对象
- `bool` + `typer.Option(False)` → 自动变成 `--dry-run` 开关（不用传值）
- `Enum` → 自动限制取值，非法值报错并列出候选

`[已验证]` 传 `--by bogus` 时输出：
```
Invalid value for '--by': 'bogus' is not one of 'ext', 'date'.
```
**这个报错你一行都没写**，是 typer 免费给的。手写 argparse 得写 `choices=[...]` 还得自己调错误文案。

### 3.1 为什么 `class Strategy(str, Enum)` 而不是 `Enum`

`[已验证]`
```python
class S(str, Enum): a = "a"     # S.a == "a"  → True
class P(Enum):      a = "a"     # isinstance(P.a, str) → False
```
继承 `str` 后枚举成员可以直接当字符串比较、f-string 拼接。
纯 `Enum` 成员在 Python 3.11+ 的 `StrEnum` 之前不是 str，写 f-string 会得到 `Strategy.ext` 这种难看输出。

顺带一提：3.11+ 有 `enum.StrEnum`，比 `str, Enum` 干净。你锁的是 `>=3.12`，**可以用**。

### 3.2 `typer.Exit` 是什么

我一开始说它是 `SystemExit` 子类，**错了**。

`[已验证]`
```
typer.Exit.__mro__ = [Exit, RuntimeError, Exception, BaseException]
issubclass(typer.Exit, SystemExit) → False
```

它是 `RuntimeError` 子类。typer 在顶层捕获它并转成退出码。

**实际影响**：如果你在 `main()` 外面套 `try/except Exception`，会把 `typer.Exit` 一起吞掉，
CLI 就永远退出码 0 了。这个坑在你 W03 加重试逻辑时会真的踩到。

---

## 4. pathlib：三个值得记住的点

### 4.1 `/` 运算符

`[已验证]` `Path("/d") / "txt" / "a.txt"` → `/d/txt/a.txt`。
比 `os.path.join` 好读，而且链式下去不会漏括号。

### 4.2 后缀提取的边界情况

`[已验证]`

| 文件名 | `.suffix` | 你的 `lower().lstrip(".")` |
|---|---|---|
| `a.txt` | `.txt` | `txt` ✅ |
| `archive.TAR.GZ` | `.GZ` | `gz` ⚠️ 双后缀只取最后一个 |
| `.bashrc` | `''` | `''` → 落进 `others` |
| `trailing.` | `''` | `''` ⚠️ 有小数点但被当无后缀 |

前两个对你这个工具都**可接受**（把 `.tar.gz` 归到 `gz` 不算错），但要知道边界在哪。

### 4.3 `lstrip` 不是 `removeprefix`

`[已验证]` 这是个真陷阱：
```python
".txt".lstrip(".")   → "txt"     # 想要的效果
"...txt".lstrip(".") → "txt"     # 碰巧对
".t.t".lstrip(".")   → "t.t"     # 只删开头的点，看起来对
"txt".lstrip(".")    → "txt"
```

`lstrip` 删的是**字符集**里任意字符的连续前缀，不是删字符串前缀。
这里因为 suffix 必然以 `.` 开头所以安全，但习惯上应该用：
```python
path.suffix.lower().removeprefix(".")   # 语义精确
```

`removeprefix` 是 3.9+ 的。这个不算 bug，算**可以改得更精确的一处**。

---

## 5. 设计决定：为什么这么写

### 5.1 同名冲突改成 `dup_1.txt`，不覆盖

这是**数据操作**——`shutil.move` 不可逆。覆盖的代价是丢文件，
多一个后缀的代价只是文件名丑。两者不对等，所以宁可丑。

你写了 7 行（main.py:78-83）来处理。`[已验证]` 测试确认两个文件都在。

### 5.2 校验在循环之前，不在里面

```python
try:
    cfg = Config(...)          # ← 先校验
except ValidationError:
    raise typer.Exit(2)

if not cfg.source.is_dir():    # ← 再检查目录
    raise typer.Exit(2)

for path in sorted(files):     # ← 最后才动文件
```

顺序不能反。如果先移动 50 个文件才发现 `--min-size -5`,
用户得到一个**半完成的状态**——这比直接失败糟得多。

> 通用原则：**所有可能失败的事，在产生副作用之前做完。**
> 这条在你 W09 写重试/fallback 时会再次出现。

---

## 5.3 `--dry-run` 应不应该是默认？

现在是可选。但考虑到这个工具做的事不可逆，
**我倾向于改成默认开启、要真正执行得显式传 `--apply`**。

这是产品判断不是技术判断，你自己定。改的话：
```python
apply: bool = typer.Option(False, "--apply", help="真正执行，默认只预览")
```

---

## 6. 测试：7 个用例覆盖了什么

[tests/test_main.py](../projects/w01-organize/tests/test_main.py)

| 测试 | 防的是什么 |
|---|---|
| `test_ext_strategy` | 归档分桶对了没 |
| `test_date_strategy` | 日期模式没退化 |
| `test_dry_run_moves_nothing` | **最重要**——dry-run 真的不落盘 |
| `test_min_size_skips` | 过滤生效 |
| `test_collision_keeps_both` | **第二重要**——不丢数据 |
| `test_bad_input_exits_2` | 退出码给调用方用（shell 脚本会依赖） |
| `test_target_dir_unit` | 纯函数单测，最快 |

### 值得注意的两点

**1. 用 `subprocess` 跑 CLI 而不是直接调函数**
```python
def run(args):
    return subprocess.run([sys.executable, "-m", "organize.main", *map(str, args)], ...)
```
这是在测**真实入口**，包括 typer 的参数解析、退出码。
直接 `main(...)` 测不到 `--by bogus` 这类解析层错误。
代价是慢一点，但 CLI 工具这个取舍值得。

**2. `test_bad_input_exits_2` 里有个冗余**
```python
assert run([...]).returncode == 2
assert run([...]).returncode == 2
assert run([...]).returncode == 2
```
三个断言放一个测试里，**第一个失败就看不到后两个**。
更好的写法是 `@pytest.mark.parametrize`。W02 遇到类似情况可以改。

---

## 7. 我建议你动手改的三处

不用都做，挑一个：

**A. `lstrip` → `removeprefix`**（5 分钟）
main.py:38。语义更精确，顺便理解两者差别。

**B. `Strategy` 改用 `StrEnum`**（5 分钟）
`from enum import StrEnum`（3.11+）。比你现在的 `str, Enum` 干净。

**C. `test_bad_input_exits_2` 改 parametrize**（15 分钟）
```python
@pytest.mark.parametrize("args", [
    [Path("/nope"), Path("/out")],
    ["--min-size", "-1"],
    ["--by", "bogus"],
])
def test_bad_input_exits_2(tmp_path, args):
    assert run([tmp_path, tmp_path/"out", *args]).returncode == 2
```
学 pytest 的核心特性，后面每周都要用。

**再加一个可选的挑战**：把 `--dry-run` 改成默认、`--apply` 才真做。
这是"不可逆操作怎么设计接口"的思考，比技术本身值钱。

---

## 8. 这周没碰（不用现在补）

- `asyncio` —— W03 接 LLM API 流式输出时会用，到时候自然学到
- 列表推导 / 生成器 —— 你肯定已会，W02 用 pandas 时会自然强化
- 类型注解深入（`Generic`、`Protocol`）—— 做库才需要，做应用暂时用不上
- 打包发布到 PyPI —— 独立开发大概率不需要，`uv` 本地跑就够

---

## 自查：这些你能答出来吗

不用背，答不上来就回头看对应章节。

1. `Field(description="x")` 不给 default，字段是必填还是可选？
2. entrypoint 指向错的时候，现象是什么？怎么排查？
3. 为什么 `Strategy` 要继承 `str`？
4. `typer.Exit` 继承自谁？如果你在 main 外包 `except Exception` 会怎样？
5. 为什么校验要放在移动文件之前？
6. `lstrip(".")` 和 `removeprefix(".")` 的区别？
7. 为什么测试要用 subprocess 跑 CLI 而不是直接调函数？

（答案都在上面，或在你自己的代码里。）
