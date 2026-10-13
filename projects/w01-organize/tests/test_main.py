import subprocess
import sys
from pathlib import Path

from organize.main import Config, Strategy, target_dir


def run(args, **kw):
    return subprocess.run(
        [sys.executable, "-m", "organize.main", *map(str, args)],
        capture_output=True, text=True, **kw
    )


def populate(d: Path, names=("a.txt", "b.txt", "c.md", "noext")):
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        (d / n).write_text("x" * 100)
    return d


def test_ext_strategy(tmp_path):
    src, dst = populate(tmp_path / "src"), tmp_path / "dst"
    assert run([src, dst]).returncode == 0
    assert (dst / "txt" / "a.txt").exists()
    assert (dst / "md" / "c.md").exists()
    assert (dst / "others" / "noext").exists()


def test_date_strategy(tmp_path):
    src, dst = populate(tmp_path / "src"), tmp_path / "dst"
    assert run([src, dst, "--by", "date"]).returncode == 0
    assert len(list(dst.glob("*-*/*.txt"))) == 2


def test_dry_run_moves_nothing(tmp_path):
    src, dst = populate(tmp_path / "src"), tmp_path / "dst"
    assert run([src, dst, "--dry-run"]).returncode == 0
    assert not dst.exists()
    assert (src / "a.txt").exists()


def test_min_size_skips(tmp_path):
    src, dst = populate(tmp_path / "src"), tmp_path / "dst"
    assert run([src, dst, "--min-size", "1000"]).returncode == 0
    assert not dst.exists()


def test_collision_keeps_both(tmp_path):
    a, b, dst = tmp_path / "a", tmp_path / "b", tmp_path / "dst"
    populate(a, ("dup.txt",))
    populate(b, ("dup.txt",))
    run([a, dst])
    run([b, dst])
    assert sorted(p.name for p in (dst / "txt").iterdir()) == ["dup.txt", "dup_1.txt"]


def test_bad_input_exits_2(tmp_path):
    assert run([tmp_path / "nope", tmp_path / "out"]).returncode == 2
    assert run([tmp_path, tmp_path / "out", "--min-size", "-1"]).returncode == 2
    assert run([tmp_path, tmp_path / "out", "--by", "bogus"]).returncode == 2


def test_target_dir_unit():
    cfg = Config(source=Path("/s"), dest=Path("/d"))
    assert target_dir(cfg, Path("x.PDF")).name == "pdf"
    assert Config(source=Path("/s"), dest=Path("/d"), strategy=Strategy.date).strategy == Strategy.date
