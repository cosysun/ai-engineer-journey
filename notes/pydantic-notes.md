# Pydantic 知识点（基于 v2.14.1 实测）

不是 API 手册，是**会踩的坑 + 值得记的行为**。
每条标 `[已验证]` 的我都跑过实验，附实际输出。

面向：已有工程背景、正在转 AI 应用开发。

---

## 0. 一句话定位

Pydantic 做的是**运行时类型校验 + 数据转换**，靠类型注解驱动。

```python
class User(BaseModel):
    name: str
    age: int

User(name="bob", age="25")   # age 从 str "25" 变成 int 25
```

W01 用它校验 CLI 配置；W03 接 LLM 时它更重要——
LLM 返回的 JSON 字段可能缺、类型可能飘，pydantic 是把它变成可信数据的第一道闸门。

---

## 1. 类型强制（coercion）：v2 最有争议的行为

Pydantic 默认**尝试转换**类型，不是严格检查。

`[已验证]`
```python
class M(BaseModel):
    n: int
    f: float
    b: bool

M(n="123", f="1.5", b="true")   # -> n=123 f=1.5 b=True
M(n="12.0", f="2", b="yes")     # -> n=12  f=2.0 b=True
M(n=True,   f=True, b=0)        # -> n=1   f=1.0 b=False
M(n=1.9,    f=1,    b=1)        # -> ERROR: int_from_float
```

### 那个不一致要注意

| 输入 | 结果 |
|---|---|
| `"12.0"` → `int` | 变成 `12` |
| `1.9` → `int` | 报错 `int_from_float` |

字符串"12.0"能转，浮点数 1.9 不能转。v2 认为 float→int 会丢精度所以拒绝，
但字符串走另一条解析路径，碰巧放行了。

**影响**：配置从 JSON / 环境变量来（都是字符串）时，`min_size="1000"` 会正常变 `1000`——好事。
但期待严格类型检查时，这里会静默放行。

### 想要严格就开 strict

`[已验证]`
```python
class Strict(BaseModel):
    model_config = {"strict": True}
    n: int

Strict(n="123")   # ERROR: int_type
```

**建议**：外部输入（LLM 输出、API 请求、配置文件）用默认宽松；
内部接口契约用 strict，能提前抓到调用方类型错误。

---

## 2. `Optional` 不等于"可选"

`[已验证]`
```python
class A(BaseModel):
    x: Optional[int] = None     # 可以不传，默认 None

class B(BaseModel):
    x: Optional[int]            # 必须传！

B()   # ERROR: missing
```

`Optional[int]` 意思是"**可以传 None**"，不是"**可以不传**"。
要可省略必须给默认值 `= None`。

> 记忆法：`Optional` 管值能不能是 None，`= default` 管能不能不传。

---

## 3. `Field`：默认值 vs 约束 vs 元数据

```python
min_size: int = Field(default=0, ge=0, description="小于该字节的文件跳过")
```

三个参数各管一件事：

| 参数 | 作用 | 不给会怎样 |
|---|---|---|
| `default` / `default_factory` | 缺省值 | **字段变必填** |
| `ge`/`le`/`min_length`/`pattern` | 校验约束 | 无约束 |
| `description` | 文档（进 JSON Schema） | 无，且**不影响必填性** |

`[已验证]` 只写 `Field(description="x")` 不给 default → 报错 `missing`。

### 常用约束

```python
Field(ge=0, le=100)
Field(min_length=1, max_length=50)
Field(pattern=r"^\d{3}$")
Field(strict=True)
```

### `default_factory`：可变默认值

`[已验证]` 结果**和常见说法相反**：

```python
class Bad(BaseModel):
    items: list = []

b1, b2 = Bad(), Bad()
b1.items.append("x")
# b1.items = ['x']   b2.items = []   <- 没污染！
```

pydantic v2 会自动深拷贝可变默认值，这个 Python 经典陷阱在 pydantic 里不存在。
（对比：纯 Python 类 `def __init__(self, items=[])` 是真会污染的。）

仍推荐 `default_factory=list` 的理由：
- 语义更明确
- 默认值需要动态计算时必须用它（如 `default_factory=datetime.now`）
- 迁移到 dataclass / 其他框架时行为一致

---

## 4. 校验器：三种写法

### 4.1 `field_validator`（单字段）

`[已验证]`
```python
class V(BaseModel):
    n: int

    @field_validator("n")
    @classmethod
    def double(cls, v):
        return v * 2

V(n="5").n   # -> 10（收到的是已转成 int 的 5，不是 "5"）
```

默认 `mode="after"`：先类型转换，再进校验器，所以收到的已是正确类型。
要拿原始值用 `@field_validator("n", mode="before")`。

> `@classmethod` 在 v2 是推荐的（不加能跑，会有警告）。

### 4.2 `model_validator`（跨字段）

```python
@model_validator(mode="after")
def check_range(self):
    if self.start > self.end:
        raise ValueError("start 必须早于 end")
    return self
```

### 4.3 `computed_field`（派生字段）

`[已验证]`
```python
class Rect(BaseModel):
    w: int
    h: int

    @computed_field
    @property
    def area(self) -> int:
        return self.w * self.h

Rect(w=3, h=4).model_dump()   # {'w': 3, 'h': 4, 'area': 12}
```

不占初始化参数，但会进序列化输出。

---

## 5. 错误处理：一次拿全

`[已验证]` pydantic 会**收集所有错误**再抛：

```python
class Cfg(BaseModel):
    min_size: int = Field(default=0, ge=0)
    name: str = Field(min_length=3)

Cfg(min_size=-1, name="ab")
```

`ValidationError.errors()` 返回：
```python
[
  {'type': 'greater_than_equal', 'loc': ('min_size',), 'msg': 'Input should be greater than or equal to 0', 'input': -1, 'ctx': {'ge': 0}, 'url': '...'},
  {'type': 'string_too_short',   'loc': ('name',),     'msg': 'String should have at least 3 characters',  'input': 'ab', 'ctx': {'min_length': 3}, 'url': '...'}
]
```

关键字段：
- `loc` — 出错字段路径，嵌套时是多元素元组 `('db', 'host')`
- `msg` — 人话描述，可直接给用户看
- `input` — 原始错误值（**打日志时别直接打，可能含敏感数据**）
- `ctx` — 约束上下文，如 `{'ge': 0}`
- `type` — 机器可读错误码，适合程序分支

你在 W01 写的遍历全部是对的——用户一次看到所有问题，不用改一个跑一次。

`e.error_count()` 拿总数，`str(e)` 拿格式化全文。

---

## 6. 配置：`model_config`

`[已验证]`

| 配置 | 效果 |
|---|---|
| `extra="forbid"` | 多余字段报错 `extra_forbidden` |
| `extra="ignore"` | 多余字段静默丢弃（**v2 默认**） |
| `extra="allow"` | 多余字段保留进 `__pydantic_extra__` |
| `frozen=True` | 不可变 + 可哈希 |
| `strict=True` | 全局严格模式 |
| `populate_by_name=True` | 允许用字段名或 alias 初始化 |

```python
class C(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    a: int

C(a=1, b=2)    # ERROR: extra_forbidden
C(a=1).a = 2   # ERROR: frozen_instance
hash(C(a=1))   # frozen 才能哈希，可进 set / 当 dict key
```

**做 LLM 输出解析时建议 `extra="forbid"`**——模型多返回字段往往意味着 prompt 或 schema 对不上，
静默忽略会让你 debug 一整天。

---

## 7. 嵌套与构造

`[已验证]`
```python
class Addr(BaseModel):
    city: str

class User(BaseModel):
    name: str
    addr: Addr

u = User(name="a", addr={"city": "BJ"})
u.addr            # Addr(city='BJ')
u.model_dump()    # {'name': 'a', 'addr': {'city': 'BJ'}}
```

三种构造入口：

```python
User.model_validate(dict_data)
User.model_validate_json(json_str)
User(name="a", addr=...)
```

**`model_validate_json` 是解析 LLM 输出的首选**——比 `json.loads()` 再传 dict 快，错误信息一致。

序列化：
```python
u.model_dump()        # -> dict（Path 仍是 PosixPath 对象）
u.model_dump_json()   # -> str（Path 变成 "/a/b"）
u.model_dump(mode="json")  # -> dict，但值已 JSON 化
```

`[已验证]` 要存 JSON 必须用后两者，`model_dump()` 里 Path 还是对象。

---

## 8. Union：v2 的 smart mode

`[已验证]`
```python
class U(BaseModel):
    v: Union[int, str]

U(v="123").v   # '123'  str <- 保持字符串，没强转 int
U(v=123).v     # 123    int
U(v="abc").v   # 'abc'  str
U(v=True).v    # 1      int <- bool 被当 int 匹配了
```

v1 是严格从左到右（`"123"` 会强转成 `123`），**v2 改成 smart mode**：优先保持原类型。

这个改动是好事——LLM 返回 `{"count": "42"}` 时，v2 保留 `"42"`，不悄悄变 `42`。

注意 `True` 被 `int` 吃掉（bool 是 int 子类）。要区分就写 `Union[bool, int, str]`，bool 放前面。

---

## 9. 别名：接外部 API 的脏字段名

`[已验证]`
```python
class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_name: str = Field(alias="userName")

User(userName="bob")    # 可以
User(user_name="bob")   # 也可以（要开 populate_by_name）
```

接第三方 API（驼峰）但内部想用蛇形时常用。

---

## 10. 和 AI 应用直接相关的用法

这是学 pydantic 的真实目的，前面都是铺垫。

### 10.1 把 LLM 输出钉成可信数据

```python
class Todo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1)
    owner: Optional[str] = None
    due: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    priority: int = Field(default=3, ge=1, le=5)

todo = Todo.model_validate_json(llm_response)
```

比手写 `if "title" not in d: raise ...` 干净得多，
错误信息还能喂回给模型让它自我修正（W20 会用到）。

### 10.2 生成 JSON Schema 喂给 structured output

```python
Todo.model_json_schema()
```

OpenAI / Claude 的 function calling 都要 schema——**别手写，从 pydantic 生成**。
模型返回后用同一个类校验回来，schema 和校验永远同步。

### 10.3 每个 CLI / API 的配置层

W01 就是这个模式：

```
typer/argparse 收参数 → pydantic Config 校验 → 业务逻辑
```

校验逻辑集中在类定义里，业务代码没有散落的 `if not x: raise`。

---

## 11. 速查卡

```python
# 定义
class M(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    a: int                                    # 必填
    b: str = "x"                              # 可选有默认
    c: Optional[int] = None                   # 可传 None 且可省略
    d: int = Field(default=0, ge=0, description="...")
    e: list = Field(default_factory=list)

# 构造
M.model_validate(dict_data)
M.model_validate_json(json_str)

# 序列化
m.model_dump()
m.model_dump_json()
m.model_dump(mode="json")

# 错误
try:
    M(...)
except ValidationError as e:
    e.errors()
    e.error_count()
```

---

## 12. 这周不用学

- 自定义类型 / `Annotated` 高级用法 —— 做库才需要
- `@field_serializer` —— 有非常规格式时再看
- `TypeAdapter` —— 校验 `list[Todo]` 这类非 BaseModel 时学，W07 做 eval 会用到
- 性能调优 / `model_construct` —— 别提前优化

---

## 13. 自查题

1. `Optional[int]` 不给默认值，字段是必填还是可选？
2. `"12.0"` 和 `1.9` 传给 `int` 字段，哪个报错？为什么不一致？
3. `Field(description="x")` 不给 default，字段能省略吗？
4. pydantic v2 里 `items: list = []` 会污染其他实例吗？纯 Python 类呢？
5. 怎么让模型同时支持 `userName` 和 `user_name` 两种字段名？
6. `model_dump()` 和 `model_dump_json()` 对 `Path` 字段的结果有什么不同？
7. 为什么解析 LLM 输出建议开 `extra="forbid"`？
8. 做 AI 应用时，pydantic 除了校验还能帮你做什么？（提示：schema）

（答案都在上面。）
