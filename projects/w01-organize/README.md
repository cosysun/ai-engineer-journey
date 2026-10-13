# organize

按扩展名或日期批量归档文件的 CLI。W01 的交付物——目标不是这个工具本身有用，
而是跑通「`uv` 项目 + `typer` CLI + `pydantic` 配置校验 + 测试」这条最小工程链路。

## 安装

```bash
uv sync
```

## 用法

```bash
uv run organize <源目录> <目标目录> [选项]
```

| 选项 | 说明 |
|---|---|
| `--by ext` | 按扩展名归档（默认），无扩展名归入 `others/` |
| `--by date` | 按修改时间的 `YYYY-MM` 归档 |
| `--dry-run` | 只打印计划，不实际移动 |
| `--min-size N` | 小于 N 字节的文件跳过 |

```bash
# 预览会怎么动
uv run organize ~/Downloads ~/Sorted --dry-run

# 按月份归档，跳过空文件
uv run organize ~/Photos ~/Archive --by date --min-size 1024
```

## 设计取舍

- **同名冲突不覆盖**，改写成 `name_1.ext`。这是数据操作，丢文件的代价远大于多一个后缀。
- **配置错误在动手之前报 exit 2**，用 pydantic 在 `Config` 层校验，而不是移动一半才炸。
- **`--dry-run` 是默认推荐路径**。批量移动文件不可逆，先看计划再执行。

## 测试

```bash
uv run pytest tests -q
```

## 局限

- 只处理源目录的直接子文件，不递归。
- 按修改时间（mtime）而非拍摄时间，照片的 EXIF 不在考虑范围内。
- 单线程，超大目录会慢；没做断点续传，中断后重跑会跳过已移动的、继续剩下的。
