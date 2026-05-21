import unittest
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir

from craftcms_management.common.paths import load_path_config


class LoadPathConfigTests(unittest.TestCase):
    """Tests for script path configuration loading."""

    def test_derives_paths_from_relative_backend_root(self) -> None:
        """Resolve BACKEND_ROOT relative to the dotenv file."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts_root = root / "scripts"
            scripts_root.mkdir()
            env_path = scripts_root / ".env"
            env_path.write_text("BACKEND_ROOT=../backend\n", encoding="utf-8")

            paths = load_path_config(env_path)

            self.assertEqual(paths.repo_root, root.resolve())
            self.assertEqual(paths.backend_root, (root / "backend").resolve())
            self.assertEqual(paths.backend_env, paths.backend_root / ".env")
            self.assertEqual(paths.tmp_dir, Path(gettempdir()).resolve())

    def test_missing_backend_root_raises_value_error(self) -> None:
        """Reject env files without BACKEND_ROOT."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("TMP_DIR=/tmp\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_path_config(env_path)


if __name__ == "__main__":
    unittest.main()
