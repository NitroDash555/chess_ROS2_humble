# chess_ROS2_humble

Учебный проект по созданию роботизированного шахматного манипулятора на базе механики 3D-принтера.

Сценарий работы:
1. Компьютерное зрение (YOLO) распознает доску и фигуры, формирует позицию в формате FEN.
2. Шахматный движок Stockfish получает FEN и выбирает лучший ход.
3. Узел управления перемещением разбивает ход на команды манипулятора.
4. Манипулятор физически перемещает фигуру на доске.

Текущий статус: сквозная сервисная цепочка «зрение → движок → move» работает. `move` умеет строить последовательность команд манипулятора (простой ход, взятие, en passant, рокировка) по калибровке доски из конфига. До железа ещё не дошло: serial-шлюз к Arduino не реализован, команды пока только логируются.

## 1. Назначение проекта

Цель проекта: связать цифрового шахматного партнера (Stockfish) с физическим исполнителем хода (манипулятор), чтобы человек мог играть на реальной доске.

Основная техническая идея:
- Raspberry Pi запускает ROS 2 ноды высокого уровня (зрение, логика партии, интеграция движка).
- Arduino управляет низкоуровневыми действиями (моторы, концевики, сенсоры), получая команды от Pi.
- Обмен между подсистемами организуется через четкий протокол команд и статусов.

## 2. Текущее состояние workspace

В рабочем пространстве 6 ROS 2 пакетов:
- comp_vision
- game
- interfaces
- move
- start
- stockfish_node

Ключевые факты:
- `interfaces` описывает три сервиса: GetFEN (`prev_fen` -> `fen`), GetMove (`fen` -> `move`), Move (`move` + `fen` -> пусто).
- `comp_vision` — работающий CV-пайплайн (YOLO: углы доски + фигуры), упакованный в сервис `get_fen`.
- `move` — работающий разбор хода в команды манипулятора по координатам доски.
- `start` — launch-файл, который поднимает все ноды и передаёт move-узлу файл калибровки.
- Логи партии пишутся в `log/moves.txt`.
- Проект разворачивается в Dev Container на базе ROS 2 Humble.

## 3. Архитектура (логическая)

Поток данных в текущем дизайне:

```
Human board -> comp_vision (GetFEN) -> game -> stockfish_node (GetMove) -> game -> move (Move) -> Arduino/motors (в планах)
```

Детализация по пакетам:

### interfaces
- Тип: ament_cmake
- Назначение: ROS 2 интерфейсы сервисов.
- Сервисы:
  - GetFEN.srv
    - Request: `string prev_fen`
    - Response: `string fen`
  - GetMove.srv
    - Request: `string fen`
    - Response: `string move`
  - Move.srv
    - Request: `string move`, `string fen`
    - Response: пусто

### comp_vision
- Тип: ament_python
- Узел: comp_vision
- Сервис: get_fen (тип GetFEN)
- Назначение: вернуть FEN по текущему кадру.
- Реализация: тонкая обёртка над `comp_vision.chess_vision.pipeline()`:
  - читает кадр `<repo>/img/z.jpg`;
  - принимает `prev_fen` от game, чтобы переживать сбои распознавания (при ошибке возвращает `prev_fen` без изменений);
  - YOLO-модели (углы + фигуры) грузятся при импорте из `chess_vision/assets/models/`;
  - при успехе дописывает FEN в `log/moves.txt`.

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
  - при старте синхронно ждёт появления всех трёх сервисов;
  - таймер 0.2 с: если не ход робота и прошло 3 с после последнего хода движка — инициирует свой ход;
  - цепочка асинхронных вызовов: `get_fen` -> `get_move` -> `move`; флаг `busy` не даёт цепочкам пересекаться;
  - пишет FEN в `log/moves.txt`;
  - FEN обновляется ПОСЛЕ успешного выполнения хода (в `move` уходит старый FEN).

### move
- Тип: ament_python
- Узел: move
- Сервис: move (тип Move)
- Назначение: преобразовать ход в команды для механики/Arduino.
- Реализация:
  - параметры калибровки из `config/board_calibration.yaml`: координаты углов `a1`/`h1`/`a8`, точка `stash`, высоты `z_safe`/`z_grab`;
  - линейная интерполяция клетки -> физические `x;y`, разбор хода на последовательность команд `"x;y;z"` + число схвата (0 — взять, 1 — отпустить);
  - поддержаны варианты: простой ход, взятие (фигура снимается в `stash`), en passant, рокировка;
  - TODO: отправка команд в Arduino (serial/I2C/CAN) — сейчас команды только логируются.

### start
- Тип: ament_python
- Launch: start.launch.py
- Назначение: единая точка запуска всех нод.
- Особенности:
  - move-узлу передаётся `config/board_calibration.yaml` (секция `/move`, соответствует имени узла);
  - `ROS_LOG_DIR` указывается на `log/`.

## 4. Структура репозитория

Ключевые пути:

- .devcontainer/
  - devcontainer.json
  - Dockerfile
- config/
  - board_calibration.yaml (калибровка доски для move)
- img/
  - z.jpg (входной кадр для распознавания)
- log/
  - moves.txt (история распознанных позиций)
- ros2_ws/
  - src/
    - comp_vision/
    - game/
    - interfaces/
    - move/
    - start/
    - stockfish_node/
  - scripts/ (установка зависимостей)
  - build/, install/, log/, pipe/ (артефакты colcon и отладочные картинки)

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

После правки `.srv` в `interfaces` пересборка обязательна (остальные пакеты импортируют сгенерированные модули; исходники Python при этом симлинкуются).

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
ros2 run game game
```

Замечание: `game` блокируется в ожидании сервисов, поэтому его нельзя запускать в одиночку.

## 7. Отладка ROS 2 взаимодействий

### 7.1 Проверить доступные сервисы

```bash
ros2 service list
```

Ожидаются:
- /get_fen
- /get_move
- /move

### 7.2 Проверить интерфейсы

```bash
ros2 interface show interfaces/srv/GetFEN
ros2 interface show interfaces/srv/GetMove
ros2 interface show interfaces/srv/Move
```

### 7.3 Ручной вызов сервисов

```bash
ros2 service call /get_fen interfaces/srv/GetFEN "{prev_fen: ''}"
ros2 service call /get_move interfaces/srv/GetMove "{fen: 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 2'}"
ros2 service call /move interfaces/srv/Move "{move: 'e2e4', fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'}"
```

### 7.4 Проверка логов

```bash
tail -n 20 /workspaces/chess_ROS2_humble/log/moves.txt
```

Формат строки:
- time: DD.MM.YYYY HH:MM:SS | game_id: N | fen: ...

## 8. Известные проблемы текущей реализации

Исправлено по результатам пробных запусков:
- Исправлен callback и API использования движка в stockfish_node.
- Исправлена обработка future/result в game.
- Исправлен callback сервиса move (возвращает response).
- Исправлена зависимость ultralytics в package.xml comp_vision.
- Убрана блокировка input() в game.
- Исправлено определение пути до log/moves.txt (без жесткой цепочки parent-parent).
- `update_fen` в game перенесён после выполнения хода — move-узлу уходит актуальный (старый) FEN.

Актуальные ограничения на текущий момент:

1. `move` не отправляет команды в Arduino — нет serial-транспорта (команды только логируются).
2. Нет валидации входного FEN и UCI-ходов.
3. Нет retry/state machine для ошибок обмена с исполнительной частью.

## 9. Рекомендованный протокол Pi <-> Arduino

Для следующего этапа разработки рекомендуемый минимальный протокол по Serial:

### 9.1 Формат команд (ASCII, одна строка)

```text
MOVE <uci_move>\n
HOME\n
STATUS\n
STOP\n
```

Примеры:
- MOVE e2e4
- MOVE a7a8q

### 9.2 Формат ответов Arduino

```text
OK <command>\n
ERR <code> <message>\n
STATE <idle|busy|homing|error>\n
POS <x> <y> <z>\n
```

### 9.3 Таймауты и надежность
- Таймаут ответа на команду: 3-5 секунд (или больше для длинного перемещения).
- При таймауте: повтор запроса статуса + аварийная остановка.
- Обязательное подтверждение каждой команды (ACK/NACK).

## 10. План дальнейшей разработки

### Сделано
- Реальный CV-пайплайн (YOLO) в comp_vision.
- Разбор ходов в move: простой ход, взятие, en passant, рокировка.
- Калибровка доски через config/board_calibration.yaml.

### Осталось
- Шаг 1. Serial-шлюз к Arduino
  - Модуль транспорта в пакете move.
  - Очередь команд, state machine и retries.
- Шаг 2. Валидация и надёжность
  - Валидация FEN и UCI-ходов.
  - Обработка ошибочных/пустых ответов сервисов с retry.
- Шаг 3. Тесты
  - Unit-тесты на разбор ходов, парсинг FEN/UCI и протокол serial.
  - Интеграционные тесты сервисных цепочек ROS 2.

## 11. Команды для ежедневной разработки

```bash
# 1) Пересобрать после изменений
cd /workspaces/chess_ROS2_humble/ros2_ws
colcon build --symlink-install
source install/setup.bash

# 2) Запустить систему
ros2 launch start start.launch.py

# 3) Проверить сервисы
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
- Входной кадр для распознавания: `img/z.jpg`.

---

Документ актуален для текущего состояния репозитория на момент ревизии.
