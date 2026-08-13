# AGENTS.md

Guidance for agents working in this repository. A ROS 2 (Humble) chess-playing robot: comp_vision reads the board, Stockfish picks a move, a move node drives the arm/Arduino. Early stage: `move` plans commands and publishes them to a topic; `arduino_bridge` is a serial gateway (port not attached yet); `comp_vision` is an action server over the `chess_vision` pipeline subpackage.

## Layout and dependencies

- Eight packages under `ros2_ws/src/`: `arduino_bridge`, `chess_common`, `comp_vision`, `game`, `interfaces`, `move`, `start`, `stockfish_node`. `ros2_ws/{build,install,log}` are colcon artifacts; edit only `src/`.
- `chess_common` (ament_python library, no nodes) provides `repo_paths.py`: `find_repo_root()`, `image_path()`, `log_dir()`, `moves_log_path()`, `board_calibration_path()`. game, comp_vision and the launch file use it — don't re-add per-package path walking.
- `interfaces` (ament_cmake) defines action `GetFEN.action` (goal `string prev_fen` -> result `string fen`, feedback `int32 step` + `string message`) and services `srv/GetMove.srv` (`string fen` -> `string move`), `srv/Move.srv` (`string move`, `string fen` -> empty). Requires `action_msgs` (package.xml + CMakeLists `DEPENDENCIES`).
- Beyond ROS deps: `python-chess` (`import chess`, used by game, move and comp_vision), the `stockfish` Python package, and for comp_vision: `ultralytics`, `opencv`, `shapely`, `dotenv`, `matplotlib` (install_requires pins `numpy<2.0`, `opencv-python-headless<4.11.0`); `arduino_bridge` uses `pyserial` (`import serial`) and `std_msgs`. Pip deps are listed per-package in `install_requires` and installed in bulk by `ros2_ws/scripts/install_vision_deps.sh` (`python3-serial` is also in the Dockerfile).

## Build / test / run

- Build from `ros2_ws`: `source /opt/ros/humble/setup.bash && colcon build --symlink-install && source install/setup.bash`. `chess_common` and `interfaces` build before the consumers (declared deps).
- After editing a `.srv`/`.action` in `interfaces`, rebuild: the other packages import generated modules. Python package sources are symlinked, generated interface code is not.
- Tests are only the default ament scaffolds (copyright/flake8/pep257) — no functional tests exist. Single package: `colcon test --packages-select <pkg>`, then `colcon test_result --all`. Note: package.xml element order matters for xmllint (`test_depend` before `member_of_group`).
- Run everything with `ros2 launch start start.launch.py`, or nodes individually with `ros2 run <pkg> <pkg>`. The launch file renames all four nodes to `main`; action/service names come from node code (`/get_fen`, `/get_move`, `/move`) and are unaffected. `arduino_bridge` is NOT in the launch yet.
- Devcontainer `postCreateCommand` calls `ros2_ws/scripts/install_vision_deps.sh` (in the repo): pip-installs vision deps and apt-installs the stockfish binary if missing. Run it manually on any new device before `colcon build`.
- Arduino port permissions: `sudo bash ros2_ws/scripts/setup_arduino_permissions.sh` (installs a udev rule) or add the user to the `dialout` group. Udev rules apply on the host, not inside a container.

## Game node (`game`) behavior

- Flow: comp_vision `get_fen` (ACTION) -> game -> stockfish `get_move` (service) -> game -> move `move` (service).
- `game` blocks synchronously at startup until the action server and both services are up (`wait_for_server` / `wait_for_service` loop) — don't launch it alone.
- Timer-driven (0.2s): if it is not the robot's turn and 3s have passed since the last engine move, `my_move` becomes True. When `my_move` and not `busy`, a chain of async calls runs: send `GetFEN` goal -> on accepted, `get_result_async` -> stockfish -> move; `busy` prevents overlap. Success on `move` resets `my_move` and updates `last_engine_move_time` (optimistic — no Arduino ack yet).
- `get_fen` retry: on any failure (goal send error, goal rejected, status != SUCCEEDED, empty result) game schedules a one-shot retry timer (`FEN_RETRY_DELAY_SEC = 1.0`), keeping `busy` True. The pipeline itself raises on error and the action server aborts (it no longer returns `prev_fen` on failure). `update_fen()` optimistically applies the Stockfish move to the internal FEN after the move service returns; the FEN is overwritten by the next `get_fen` regardless.
- Log: `game` writes FEN history to `<repo>/log/moves.txt` (via `chess_common.repo_paths.moves_log_path()`), newest line first, capped at 300 lines (`deque(maxlen=300)`). `game_id` = id of the newest line + 1. Line format: `time: DD.MM.YYYY HH:MM:SS | game_id: N | fen: ...`. The launch file also points `ROS_LOG_DIR` at the same dir.

## Node status

- `comp_vision` — action server (`get_fen`) wrapping `chess_vision.pipeline()`. Pipeline lives in `comp_vision/comp_vision/chess_vision/`. Gotchas:
  - `chess_vision` and its `core.*` subpackages MUST keep their `__init__.py` files — the earlier attempt died because the top-level `__init__.py` was missing, so `find_packages()` dropped it at build time.
  - YOLO models load at import time (corner + pieces) from `chess_vision/assets/models/*.pt`, resolved relative to the package — don't move/rename them.
  - `pipeline(image_path, prev_fen, logger, progress_cb)` is stateless: `prev_fen` comes from the game node (`GetFEN.prev_fen`); `progress_cb(step, message)` is called per pipeline step (8 steps) and the action server maps it to feedback. It now RAISES on error (hard failures and `AmbiguousMoveError`/`NoValidMoveError` from `reconstruct_fen`); the action server aborts the goal. Input image is `<repo>/img/z.jpg` (via `chess_common`); debug images are written to `<repo>/pipe/` (also via `chess_common.repo_paths.pipe_dir()`) only when `DEBUG` env var is `true`/`1` (checked via `chess_vision/debug.py:is_debug()`; matplotlib only imported under DEBUG). Note: `start.launch.py` sets `DEBUG=true` (not `NODE_ENV`).
  - `BestMove` (chess-api.com web API) was dropped; `core/functions/clear_console.py` is unused.
  - The ament flake8 scaffold test flags this copied code (long lines) — pre-existing, not a functional issue.
- `move` — service `move` (type `srv/Move`): plans trajectory commands from the UCI move + FEN and publishes each as `std_msgs/String` `MOVE;...` to the topic `/arduino/command` (consumed by `arduino_bridge`). No Arduino/serial code yet; calibration params come from `config/board_calibration.yaml` passed by the launch file.
- `arduino_bridge` — early, works for the connection part: `BridgeNode` (`bridge`) finds the port by `vendor_id`/`product_id` params, a periodic timer auto-reconnects (`reconnect_period`), a `std_msgs/String` subscriber on `command_topic` (default `/arduino/command`) forwards strings to serial via `send_command` (guarded on open port; closes port on `SerialException` so the timer can reconnect). `on_shutdown` closes the port. Params example: `config/arduino.yaml` (default VID/PID `'xxxx'` will never match — set real values). No feedback topic yet.
- `stockfish_node` — real. Node name `stockfish`, service `get_move`. Engine path resolved from `/usr/games/stockfish`, `/usr/bin/stockfish`, else `stockfish` from PATH.
