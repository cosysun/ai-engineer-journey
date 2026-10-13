"""Batch-organize files in a directory by extension or date."""

from __future__ import annotations

import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path

import typer
from pydantic import BaseModel, ConfigDict, Field, ValidationError

app = typer.Typer(add_completion=False, help="按扩展名或日期批量归档文件")

UNKNOWN = "others"


class Strategy(str, Enum):
    ext = "ext"
    date = "date"


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Path = Field(description="待整理的目录")
    dest: Path = Field(description="归档输出目录")
    strategy: Strategy = Strategy.ext
    dry_run: bool = False
    min_size: int = Field(default=0, ge=0, description="小于该字节的文件跳过")


def target_dir(cfg: Config, path: Path) -> Path:
    if cfg.strategy is Strategy.date:
        stamp = datetime.fromtimestamp(path.stat().st_mtime)
        bucket = f"{stamp.year}-{stamp.month:02d}"
    else:
        bucket = path.suffix.lower().lstrip(".") or UNKNOWN
    return cfg.dest / bucket


@app.command()
def main(
    source: Path = typer.Argument(..., help="待整理的目录"),
    dest: Path = typer.Argument(..., help="归档输出目录"),
    strategy: Strategy = typer.Option(Strategy.ext, "--by", help="归档依据：ext 或 date"),
    dry_run: bool = typer.Option(False, "--dry-run", help="只打印计划，不实际移动"),
    min_size: int = typer.Option(0, "--min-size", help="小于该字节的文件跳过"),
) -> None:
    try:
        cfg = Config(
            source=source, dest=dest, strategy=strategy, dry_run=dry_run, min_size=min_size
        )
    except ValidationError as exc:
        # 配置错误要在动手之前说清楚，而不是移动一半才炸
        for err in exc.errors():
            where = ".".join(str(x) for x in err["loc"])
            typer.secho(f"配置错误 {where}: {err['msg']}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from None

    if not cfg.source.is_dir():
        typer.secho(f"源目录不存在或不是目录: {cfg.source}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    files = [p for p in cfg.source.iterdir() if p.is_file()]
    moved = skipped = 0

    for path in sorted(files):
        if path.stat().st_size < cfg.min_size:
            skipped += 1
            continue
        target = target_dir(cfg, path) / path.name
        if cfg.dry_run:
            typer.echo(f"[计划] {path.name} -> {target}")
            moved += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        # 同名冲突不覆盖：这是数据操作，丢文件的代价远大于多一个后缀
        if target.exists():
            stem, suffix, n = path.stem, path.suffix, 1
            while target.exists():
                target = target.parent / f"{stem}_{n}{suffix}"
                n += 1
        shutil.move(str(path), str(target))
        typer.echo(f"{path.name} -> {target}")
        moved += 1

    typer.secho(f"\n完成：移动 {moved}，跳过 {skipped}", fg=typer.colors.GREEN)
    if cfg.dry_run:
        typer.secho("（dry-run，未实际移动）", fg=typer.colors.YELLOW)


if __name__ == "__main__":
    app()
