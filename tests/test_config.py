from pathlib import Path

from src import config


def test_project_root_is_repo_root_not_src():
    """PROJECT_ROOT must point above src/, not at src/ itself.

    Regression test: PROJECT_ROOT was computed as
    Path(__file__).resolve().parent, which resolves to the src/ directory
    (config.py's own parent), not the actual project root one level above.
    """
    assert config.PROJECT_ROOT == Path(__file__).resolve().parent.parent
    assert (config.PROJECT_ROOT / "src" / "config.py").exists()
