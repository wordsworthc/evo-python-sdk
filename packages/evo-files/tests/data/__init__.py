import json
from pathlib import Path

_THIS_DIR = Path(__file__).parent.resolve()


def _load_json_data(target_file: Path) -> list | dict:
    with target_file.open("r") as json_file:
        return json.load(json_file)


def load_test_data(filename: str) -> list | dict:
    target_file = resolve_file(filename)

    match target_file.suffix.lower():
        case ".json":
            return _load_json_data(target_file)
        case ext:
            raise ValueError(f"Unsupported data file type '{ext}'")


def resolve_file(filename: str) -> Path:
    target_file = (_THIS_DIR / filename).resolve()

    # Test data must live in test data directory.
    if not target_file.is_relative_to(_THIS_DIR):
        raise RuntimeError("Cannot access files outside test data directory.")

    # File must exist.
    if not target_file.exists():
        raise FileNotFoundError(f"Unknown file '{target_file}'")

    return target_file
