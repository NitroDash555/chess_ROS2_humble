# AGENTS.md

Guidance for agents working in this repository. A ROS 2 (Humble) chess-playing robot: comp_vision reads the board, Stockfish picks a move, a move node drives the arm/Arduino. Early stage: `move` is a stub; `comp_vision` is a thin service wrapper over the `chess_vision` pipeline subpackage.

## Layout and dependencies

- Six packages under `ros2_ws/src/`: `comp_vision`, `game`, `interfaces`, `move`, `start`, `stockfish_node`. `ros2_ws/{build,install,log}` are colcon artifacts; edit only `src/`.
- `interfaces` (ament_cmake) defines `srv/GetFEN.srv` (`string prev_fen` -> `string fen`), `srv/GetMove.srv` (`string fen` -> `string move`), `srv/Move.srv` (`string move` -> empty). The `prev_fen` field is new/uncommitted; game.py sets it.
- Beyond ROS deps: `python-chess` (`import chess`, used by game and comp_vision), the `stockfish` Python package, and for comp_vision: `ultralytics`, `opencv`, `shapely`, `dotenv`, `matplotlib` (install_requires pins `numpy<2.0`, `opencv-python-headless<4.11.0`). These pip deps are listed per-package in `install_requires` and installed in bulk by `ros2_ws/scripts/install_vision_deps.sh`.

## Build / test / run

- Build from `ros2_ws`: `source /opt/ros/humble/setup.bash && colcon build --symlink-install && source install/setup.bash`.
- After editing a `.srv` in `interfaces`, rebuild: the other packages import generated modules. Python package sources are symlinked, generated interface code is not.
- Tests are only the default ament scaffolds (copyright/flake8/pep257) — no functional tests exist. Single package: `colcon test --packages-select <pkg>`, then `colcon test_result --all`.
- Run everything with `ros2 launch start start.launch.py`, or nodes individually with `ros2 run <pkg> <pkg>`. The launch file renames all four nodes to `main`; service names come from node code (`/get_fen`, `/get_move`, `/move`) and are unaffected.
- Devcontainer `postCreateCommand` calls `ros2_ws/scripts/install_vision_deps.sh` (in the repo): pip-installs vision deps (`numpy<2.0`, `opencv-python-headless<4.11.0`, `ultralytics`, `shapely`, `python-dotenv`, `python-chess`, `pillow`, `matplotlib`, `stockfish`) and apt-installs the stockfish binary if missing. Run it manually on any new device before `colcon build`.

## Game node (`game`) behavior

- Flow: comp_vision `get_fen` -> game -> stockfish `get_move` -> game -> move `move`.
- `game` blocks synchronously at startup until all three services are up (`wait_for_service` loop) — don't launch it alone.
- Timer-driven (0.2s): if it is not the robot's turn and 3s have passed since the last engine move, `my_move` becomes True. When `my_move` and not `busy`, a chain of three async service calls runs; `busy` prevents overlap. Success on `move` resets `my_move` and updates `last_engine_move_time`.
- `update_fen()` optimistically applies the Stockfish move to the internal FEN (works now, uses `chess.Move.from_uci`), but it runs BEFORE the move service call and the FEN is overwritten by the next `get_fen` regardless.
- Log: `game` writes FEN history to `<repo>/log/moves.txt`, newest line first, capped at 300 lines (`deque(maxlen=300)`). Path found by walking up from cwd to a dir containing both `ros2_ws` and `log`. `game_id` = id of the newest line + 1. Line format: `time: DD.MM.YYYY HH:MM:SS | game_id: N | fen: ...`. The launch file also points `ROS_LOG_DIR` at the same dir.

## Node status

- `comp_vision` — thin wrapper: `comp_vision.py` only exposes the `get_fen` service and calls `chess_vision.pipeline()`. The pipeline lives in `comp_vision/comp_vision/chess_vision/`. Gotchas:
  - `chess_vision` and its `core.*` subpackages MUST keep their `__init__.py` files — the earlier attempt died because the top-level `__init__.py` was missing, so `find_packages()` dropped it at build time.
  - YOLO models load at import time (corner + pieces) from `chess_vision/assets/models/*.pt`, resolved relative to the package — don't move/rename them.
  - `pipeline(image_path, prev_fen, logger)` is stateless: `prev_fen` comes from the game node (`GetFEN.prev_fen`); on detection failure it returns `prev_fen` unchanged. Input image is `<repo>/img/z.jpg`; debug images are written to `./pipe` in cwd only when `DEBUG` env var is `true`/`1` (checked via `chess_vision/debug.py:is_debug()`; matplotlib only imported under DEBUG). On success it appends the detected FEN to `<repo>/log/moves.txt`.
  - `BestMove` (chess-api.com web API) was dropped; `core/functions/clear_console.py` is unused.
  - The ament flake8 scaffold test flags this copied code (long lines) — pre-existing, not a functional issue.
- `move` — stub: only logs the request; no Arduino/serial code yet.
- `stockfish_node` — real. Node name `stockfish`, service `get_move`. Engine path resolved from `/usr/games/stockfish`, `/usr/bin/stockfish`, else `stockfish` from PATH.
