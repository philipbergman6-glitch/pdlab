"""The report can only quote numbers that the code produced: rendering must succeed."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from pdlab.experiments import Scale, run_all

ROOT = Path(__file__).resolve().parents[1]


def _load_render():
    spec = importlib.util.spec_from_file_location(
        "render_report", ROOT / "scripts" / "render_report.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def quick_canonical(tmp_path_factory: pytest.TempPathFactory) -> Path:
    p = tmp_path_factory.mktemp("canon") / "canonical.json"
    p.write_text(json.dumps(run_all(Scale.quick())))
    return p


def test_every_chapter_renders_without_missing_keys(quick_canonical: Path, tmp_path: Path) -> None:
    mod = _load_render()
    n = mod.render_all(canon=quick_canonical, report=ROOT / "report", build=tmp_path)
    assert n >= 8
    for f in tmp_path.glob("*.md"):
        assert "{{" not in f.read_text(), f"unrendered token in {f.name}"
    assert "TODO" not in (tmp_path / "00_meta.yaml").read_text()


def test_lookup_and_format(quick_canonical: Path) -> None:
    mod = _load_render()
    d = json.loads(quick_canonical.read_text())
    assert mod.lookup(d, "thresholds.thresholds.grim_spe") == 0.5
    assert mod.lookup(d, 'tournament.leaderboards["0.0"][0].rank') == 1
    assert mod.fmt(0.123456, ".2f") == "0.12"
    assert mod.fmt([1, 2, 3], "len") == "3"
    with pytest.raises(KeyError):
        mod.lookup(d, "thresholds.nope")
