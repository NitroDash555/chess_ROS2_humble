from pathlib import Path


def find_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / 'ros2_ws').is_dir():
            return candidate
    return cwd


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def repo_root() -> Path:
    return find_repo_root()


def image_dir() -> Path:
    return ensure_dir(find_repo_root() / 'img')


def image_path(filename: str = 'z.jpg') -> Path:
    return image_dir() / filename


def log_dir() -> Path:
    return ensure_dir(find_repo_root() / 'log')


def moves_log_path() -> Path:
    return log_dir() / 'moves.txt'


def board_calibration_path() -> Path:
    return find_repo_root() / 'config' / 'board_calibration.yaml'

def arduino_cfg_path() -> Path:
    return find_repo_root() / 'config' / 'arduino.yaml'
