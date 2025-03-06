import inspect
import shutil
import unittest
from pathlib import Path

from ..data import Environment
from ..utils import Cache
from .consts import BASE_URL, ORG, WORKSPACE_ID


class TestWithStorage(unittest.TestCase):
    CACHE_DIR: Path

    @classmethod
    def setUpClass(cls) -> None:
        cache_dir = Path(inspect.getfile(cls)).parent.resolve() / f".{cls.__name__.lower()}_cache"

        def _cleanup_cache() -> None:
            """Fail-safe cleanup of the cache directory."""
            shutil.rmtree(cache_dir, ignore_errors=True)

        cls.addClassCleanup(_cleanup_cache)
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Write gitignore file in case cleanup fails.
        gitignore_file = cache_dir / ".gitignore"
        gitignore_file.write_text("*\n", encoding="utf-8")

        cls.CACHE_DIR = cache_dir

    def setUp(self) -> None:
        self.cache = Cache(self.CACHE_DIR)
        self.environment = Environment(hub_url=BASE_URL, org_id=ORG.id, workspace_id=WORKSPACE_ID)
