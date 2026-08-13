# chess_ROS2_humble

Учебный проект по созданию роботизированного шахматного манипулятора на базе механики 3D-принтера.

Сценарий работы:
1. Компьютерное зрение (YOLO) распознает доску и фигуры, формирует позицию в формате FEN.
2. Шахматный движок Stockfish получает FEN и выбирает лучший ход.
3. Узел управления перемещением разбивает ход на команды манипулятора.
4. Манипулятор физически перемещает фигуру на доске.

Текущий статус: сквозная цепочка «зрение → движок → move» работает. `get_fen` — ROS 2 action с пошаговым feedback и ретраем при ошибке. `move` умеет строить последовательность команд манипулятора (простой ход, взятие, en passant, рокировка) и публикует их в топик для Arduino-моста. До железа ещё не дошло: `arduino_bridge` умеет подключаться к плате и слушать команды, но обратная связь от Arduino и протокол serial не реализованы.

## 1. Назначение проекта

Цель проекта: связать цифрового шахматного партнера (Stockfish) с физическим исполнителем хода (манипулятор), чтобы человек мог играть на реальной доске.

Основная техническая идея:
- Raspberry Pi запускает ROS 2 ноды высокого уровня (зрение, логика партии, интеграция движка).
- Arduino управляет низкоуровневыми действиями (моторы, концевики, сенсоры), получая команды от Pi.
- Обмен между подсистемами организуется через топик команд и топик статусов.

## 2. Текущее состояние workspace

В рабочем пространстве 8 ROS 2 пакетов:
- arduino_bridge
- chess_common
- comp_vision
- game
- interfaces
- move
- start
- stockfish_node

Ключевые факты:
- `interfaces` описывает action `GetFEN` и сервисы `GetMove`, `Move`.
- `comp_vision` — работающий CV-пайплайн (YOLO: углы доски + фигуры), упакованный в action-сервер `get_fen`.
- `move` — разбор хода в команды манипулятора по координатам доски; команды публикуются в топик `/arduino/command`.
- `arduino_bridge` — serial-мост к Arduino: поиск порта по VID/PID, автопереподключение, слушатель топика команд.
- `chess_common` — общие утилиты (резолв путей репозитория).
- `start` — launch-файл, который поднимает все ноды и передаёт move-узлу файл калибровки.
- Логи партии пишутся в `log/moves.txt`.
- Проект разворачивается в Dev Container на базе ROS 2 Humble.

## 3. Архитектура (логическая)

Поток данных в текущем дизайне:

```
Human board -> comp_vision (action /get_fen) -> game -> stockfish_node (srv /get_move) -> game -> move (srv /move)
move --(topic /arduino/command)--> arduino_bridge --serial--> Arduino (в планах)
Arduino --serial--> arduino_bridge --(topic /arduino/feedback, в планах)--> game
```

Детализация по пакетам:

### interfaces
- Тип: ament_cmake
- Назначение: ROS 2 интерфейсы.
- Action: GetFEN.action
  - Goal: `string prev_fen`
  - Result: `string fen`
  - Feedback: `int32 step`, `string message`
- Сервисы:
  - GetMove.srv
    - Request: `string fen`
    - Response: `string move`
  - Move.srv
    - Request: `string move`, `string fen`
    - Response: пусто

### chess_common
- Тип: ament_python (библиотека, без нод)
- Назначение: общие утилиты. Сейчас — `repo_paths.py`: `find_repo_root()`, `image_path()`, `log_dir()`, `moves_log_path()`, `board_calibration_path()`. Используется game, comp_vision и launch-файлом (убраны три дублирующих резолва путей).

### comp_vision
- Тип: ament_python
- Узел: comp_vision
- Action-сервер: get_fen (тип GetFEN), `MultiThreadedExecutor`
- Назначение: вернуть FEN по текущему кадру.
- Реализация: тонкая обёртка над `comp_vision.chess_vision.pipeline()`:
  - читает кадр `<repo>/img/z.jpg` (путь через `chess_common`);
  - шлёт feedback на каждый из 8 шагов пайплайна (`step` + `message`);
  - при ошибке пайплайна — `goal_handle.abort()` (раньше молча возвращал `prev_fen`);
  - принимает `prev_fen` от game для реконструкции хода;
  - YOLO-модели (углы + фигуры) грузятся при импорте из `chess_vision/assets/models/`;
  - отладочные картинки пишутся в `<repo>/pipe/` при `DEBUG=true` (путь через `chess_common`).

### stockfish_node
- Тип: ament_python
- Узел: stockfish
- Сервис: get_move (тип GetMove)
- Назначение: принять FEN и вернуть лучший ход от Stockfish.
- Путь к бинарнику ищется в `/usr/games/stockfish`, `/usr/bin/stockfish`, затем `stockfish` из PATH.

### game
- Тип: ament_python
- Узел: game
- Роль: оркестратор партии.
- Поведение:
  - при старте синхронно ждёт появления action `get_fen` и сервисов `get_move`/`move`;
  - таймер 0.2 с: если не ход робота и прошло 3 с после последнего хода движка — инициирует свой ход;
  - цепочка: action `get_fen` -> srv `get_move` -> srv `move`; флаг `busy` не даёт цепочкам пересекаться;
  - при ошибке/abort/cancel `get_fen` — автоматический повтор goal через 1 с (`FEN_RETRY_DELAY_SEC`), `busy` не сбрасывается;
  - пишет FEN в `log/moves.txt`;
  - FEN обновляется ПОСЛЕ успешного выполнения хода.

### move
- Тип: ament_python
- Узел: move
- Сервис: move (тип Move)
- Назначение: преобразовать ход в команды для механики/Arduino.
- Реализация:
  - параметры калибровки из `config/board_calibration.yaml`: координаты углов `a1`/`h1`/`a8`, точка `stash`, высоты `z_safe`/`z_grab`;
  - линейная интерполяция клетки -> физические `x;y`, разбор хода на последовательность команд `"x;y;z"` + число схвата (0 — взять, 1 — отпустить);
  - поддержаны варианты: простой ход, взятие (фигура снимается в `stash`), en passant, рокировка;
  - каждая команда публикуется в топик `/arduino/command` с префиксом `MOVE;` (например `MOVE;12.3;45.6;5.0`), который слушает `arduino_bridge`;
  - TODO: отправка команд в Arduino (serial/I2C/CAN) — сейчас команды только публикуются.

### arduino_bridge
- Тип: ament_python
- Узел: bridge
- Назначение: serial-мост между ROS 2 и Arduino.
- Реализация:
  - параметры: `baudrate`, `vendor_id`, `product_id`, `reconnect_period`, `command_topic` (по умолчанию `/arduino/command`) — пример в `config/arduino.yaml`;
  - поиск порта по VID/PID (`find_arduino_port`), периодический таймер `check_and_connect` с автопереподключением;
  - подписчик на `std_msgs/String` топик команд: любая строка уходит в serial (формат разбирает Arduino, например `MOVE;...` для движения, `SCREEN;...` для экрана);
  - `send_command` пропускает запись, пока порт не подключён; при `SerialException` сам закрывает порт (таймер переподключит);
  - `on_shutdown` закрывает порт.
  - Права на порт без sudo: `scripts/setup_arduino_permissions.sh` (udev-правило) или группа `dialout`.

### start
- Тип: ament_python
- Launch: start.launch.py
- Назначение: единая точка запуска всех нод.
- Особенности:
  - move-узлу передаётся `config/board_calibration.yaml` (секция `/move`, соответствует имени узла);
  - `ROS_LOG_DIR` указывается на `log/`;
  - `DEBUG=true` включает отладочный рендер comp_vision (в `<repo>/pipe/`);
  - пути к log/ и калибровке берутся из `chess_common`.
  - `arduino_bridge` в launch пока не добавлен (добавить, когда появится плата).

## 4. Структура репозитория

Ключевые пути:

- .devcontainer/
  - devcontainer.json
  - Dockerfile
- config/
  - board_calibration.yaml (калибровка доски для move)
  - arduino.yaml (пример параметров arduino_bridge)
- img/
  - z.jpg (входной кадр для распознавания)
- log/
  - moves.txt (история распознанных позиций)
- ros2_ws/
  - src/
    - arduino_bridge/
    - chess_common/
    - comp_vision/
    - game/
    - interfaces/
    - move/
    - start/
    - stockfish_node/
  - scripts/ (установка зависимостей, udev-правило для Arduino)
  - build/, install/, log/ (артефакты colcon) и pipe/ (отладочные картинки comp_vision)

## 5. Подготовка окружения (Dev Container)

Контейнер уже включает:
- ROS 2 Humble Desktop
- stockfish (apt + python package)
- Gazebo и turtlesim
- python3-serial, python3-opencv
- инструменты сборки и отладки

Запуск в VS Code:
1. Открыть папку проекта.
2. Выполнить Reopen in Container.
3. Дождаться postCreateCommand (установка зависимостей + сборка colcon).

### 5.1 Установка на новом устройстве (вне Dev Container)

Зависимости ставятся автоматически одним скриптом:

```bash
cd ros2_ws
bash scripts/install_vision_deps.sh
```

Скрипт pip-устанавливает `numpy<2.0`, `opencv-python-headless<4.11.0`, `ultralytics`, `shapely`, `python-dotenv`, `python-chess`, `pillow`, `matplotlib`, `stockfish`, а также apt-бинарник Stockfish, если он не установлен. Эти же зависимости прописаны в `install_requires` в `setup.py` каждого пакета.

Доступ к Arduino без sudo:

```bash
sudo bash ros2_ws/scripts/setup_arduino_permissions.sh   # udev-правило
# или: sudo usermod -aG dialout $USER   # после этого перелогиниться
```

После установки зависимостей — сборка:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 6. Сборка и запуск

Все команды выполнять внутри контейнера.

### 6.1 Сборка workspace

```bash
cd /workspaces/chess_ROS2_humble/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

После правки `.srv`/`.action` в `interfaces` пересборка обязательна (остальные пакеты импортируют сгенерированные модули; исходники Python при этом симлинкуются).

### 6.2 Запуск всех нод

```bash
cd /workspaces/chess_ROS2_humble/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch start start.launch.py
```

### 6.3 Запуск узлов по отдельности

```bash
cd /workspaces/chess_ROS2_humble/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run comp_vision comp_vision
ros2 run stockfish_node stockfish_node
ros2 run move move
ros2 run arduino_bridge arduino_bridge --ros-args --params-file ../../config/arduino.yaml
ros2 run game game
```

Замечание: `game` блокируется в ожидании сервисов/action, поэтому его нельзя запускать в одиночку.

## 7. Отладка ROS 2 взаимодействий

### 7.1 Проверить доступные action/сервисы

```bash
ros2 action list
ros2 service list
```

Ожидаются:
- action: /get_fen
- сервисы: /get_move, /move

### 7.2 Проверить интерфейсы

```bash
ros2 interface show interfaces/action/GetFEN
ros2 interface show interfaces/srv/GetMove
ros2 interface show interfaces/srv/Move
```

### 7.3 Ручной вызов

```bash
ros2 action send_goal /get_fen interfaces/action/GetFEN "{prev_fen: ''}"
ros2 service call /get_move interfaces/srv/GetMove "{fen: 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 2'}"
ros2 service call /move interfaces/srv/Move "{move: 'e2e4', fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'}"
```

Команды move при этом появятся в топике:

```bash
ros2 topic echo /arduino/command
```

### 7.4 Проверка логов

```bash
tail -n 20 /workspaces/chess_ROS2_humble/log/moves.txt
```

Формат строки:
- time: DD.MM.YYYY HH:MM:SS | game_id: N | fen: ...

## 8. Известные проблемы текущей реализации

Актуальные ограничения на текущий момент:

1. `move` публикует команды в топик, но не отправляет их в Arduino напрямую; `arduino_bridge` подключён к serial, но реального протокола с Arduino ещё нет.
2. Нет обратной связи от Arduino: game считает ход выполненным оптимистично (`last_engine_move_time` ставится сразу). План — топик `/arduino/feedback`, который читает game.
3. Нет e-stop (отмена посреди хода) — можно добавить отдельной топик-командой (`STOP`).
4. Нет валидации входного FEN и UCI-ходов.
5. `arduino_bridge` не включён в launch-файл.
6. У `arduino_bridge` дефолтные `vendor_id`/`product_id` = `'xxxx'` — пока не заданы реальные VID/PID, плата не найдётся.

## 9. Рекомендованный протокол Pi <-> Arduino

Команды идут в топик `/arduino/command` (`std_msgs/String`), формат строк разбирает Arduino:

### 9.1 Формат команд (ASCII, одна строка)

```text
MOVE;x;y;z      # перемещение (публикует move)
MOVE;<gripper>  # схват: 0 — взять, 1 — отпустить
SCREEN;<text>   # вывод на экран
STOP            # аварийная остановка
HOME            # домой
STATUS          # запрос статуса
```

Пример (echo топика):
```bash
ros2 topic pub /arduino/command std_msgs/msg/String "data: 'SCREEN;Hello'"
```

### 9.2 Обратная связь от Arduino (план)

Arduino шлёт строки по serial, `arduino_bridge` публикует их в топик `/arduino/feedback`, который читает game:

```text
OK <command>
ERR <code> <message>
STATE <idle|busy|homing|error>
DONE <move_id>
```

### 9.3 Таймауты и надежность
- Таймаут ответа на команду: 3-5 секунд (или больше для длинного перемещения).
- При таймауте: повтор запроса статуса + аварийная остановка.
- Обязательное подтверждение каждой команды (ACK/NACK).

## 10. План дальнейшей разработки

### Сделано
- Реальный CV-пайплайн (YOLO) в comp_vision, упакованный в action `/get_fen` с feedback и ретраем.
- Разбор ходов в move: простой ход, взятие, en passant, рокировка.
- Калибровка доски через config/board_calibration.yaml.
- Публикация команд move в топик `/arduino/command`.
- Пакет `arduino_bridge`: подключение по VID/PID, автопереподключение, слушатель команд.
- Пакет `chess_common` (общие пути репозитория).
- udev-скрипт для доступа к Arduino без sudo.

### Осталось
- Шаг 1. Serial-протокол с Arduino + топик обратной связи `/arduino/feedback`, который читает game (убрать оптимистичное `last_engine_move_time`).
- Шаг 2. Валидация и надёжность
  - Валидация FEN и UCI-ходов.
  - E-stop (топик-команда `STOP`).
- Шаг 3. Тесты
  - Unit-тесты на разбор ходов, парсинг FEN/UCI и протокол serial.
  - Интеграционные тесты цепочек ROS 2.

## 11. Команды для ежедневной разработки

```bash
# 1) Пересобрать после изменений
cd /workspaces/chess_ROS2_humble/ros2_ws
colcon build --symlink-install
source install/setup.bash

# 2) Запустить систему
ros2 launch start start.launch.py

# 3) Проверить action/сервисы
ros2 action list
ros2 service list

# 4) Быстрая диагностика
ros2 node list
ros2 doctor
```

## 12. Полезные заметки

- Launch-файл живёт в пакете `start`: `src/start/launch/start.launch.py`; ноды сохраняют свои имена.
- Папки `ros2_ws/build`, `ros2_ws/install`, `ros2_ws/log` являются артефактами сборки и обычно не редактируются вручную.
- Логи ходов хранятся вне ros2_ws: в корневом `log/moves.txt`.
- Калибровка доски для move: `config/board_calibration.yaml` (секция `/move`, по имени узла).
- Параметры arduino_bridge: `config/arduino.yaml`.
- Входной кадр для распознавания: `img/z.jpg`.
- Общие пути (`img/`, `log/`, `config/`) резолвятся через `chess_common.repo_paths` — не дублируй резолв в нодах.

---

Документ актуален для текущего состояния репозитория на момент ревизии.
