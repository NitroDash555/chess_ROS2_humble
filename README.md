# chess_ROS2_humble

Учебный проект по созданию роботизированного шахматного манипулятора на базе механики 3D-принтера.

Сценарий работы:
1. Компьютерное зрение (YOLO) распознает доску и фигуры, формирует позицию в формате FEN.
2. Шахматный движок Stockfish получает FEN и выбирает лучший ход.
3. Узел управления перемещением отправляет ход в подсистему механики (Arduino + драйверы моторов).
4. Манипулятор физически перемещает фигуру на доске.

Сейчас проект находится на ранней стадии: ROS 2 архитектура и базовые пакеты созданы, но часть интеграции и бизнес-логики остается заглушками.

## 1. Назначение проекта

Цель проекта: связать цифрового шахматного партнера (Stockfish) с физическим исполнителем хода (манипулятор), чтобы человек мог играть на реальной доске.

Основная техническая идея:
- Raspberry Pi запускает ROS 2 ноды высокого уровня (зрение, логика партии, интеграция движка).
- Arduino управляет низкоуровневыми действиями (моторы, концевики, сенсоры), получая команды от Pi.
- Обмен между подсистемами организуется через четкий протокол команд и статусов.

## 2. Текущее состояние workspace

В рабочем пространстве обнаружено 6 ROS 2 пакетов:
- comp_vision
- game
- interfaces
- move
- start
- stockfish_node

Ключевые факты:
- Пакет interfaces описывает сервисы для FEN и хода.
- Пакет start содержит launch-файл для одновременного запуска всех нод.
- Файл логов ходов находится в log/moves.txt.
- Проект разворачивается в Dev Container на базе ROS 2 Humble.

## 3. Архитектура (логическая)

Поток данных в текущем дизайне:

Human board -> comp_vision (GetFEN) -> game -> stockfish_node (GetMove) -> game -> move (Move) -> Arduino/motors

Детализация по пакетам:

### interfaces
- Тип: ament_cmake
- Назначение: ROS 2 интерфейсы сервисов.
- Сервисы:
	- GetFEN.srv
		- Request: пусто
		- Response: string fen
	- GetMove.srv
		- Request: string fen
		- Response: string move
	- Move.srv
		- Request: string move
		- Response: пусто

### comp_vision
- Тип: ament_python
- Узел: comp_vision
- Сервис: get_fen (тип GetFEN)
- Назначение: возвращать FEN, полученный из CV-пайплайна.
- Текущее состояние: пока возвращается временная FEN-строка (заглушка).

### stockfish_node
- Тип: ament_python
- Узел: stockfish_node
- Сервис: get_move (тип GetMove)
- Назначение: получить FEN и вернуть лучший ход от Stockfish.

### game
- Тип: ament_python
- Узел: game
- Роль: оркестратор партии.
- Что делает:
	- вызывает get_fen
	- пишет FEN в log/moves.txt
	- вызывает get_move
	- отправляет ход в сервис move

### move
- Тип: ament_python
- Узел: move
- Сервис: move (тип Move)
- Назначение: преобразовать ход в команды для механики/Arduino.
- Текущее состояние: каркас без низкоуровневой реализации.

### start
- Тип: ament_python
- Launch: start.launch.py
- Назначение: единая точка запуска всех нод.

## 4. Структура репозитория

Ключевые пути:

- .devcontainer/
	- devcontainer.json
	- Dockerfile
- ros2_ws/
	- src/
		- comp_vision/
		- game/
		- interfaces/
		- move/
		- start/
		- stockfish_node/
	- launch/
	- build/, install/, log/ (артефакты colcon)
- log/
	- moves.txt (история распознанных позиций)

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
3. Дождаться postCreateCommand (сборка colcon).

## 6. Сборка и запуск

Все команды выполнять внутри контейнера.

### 6.1 Сборка workspace

```bash
cd /workspaces/chess_ROS2_humble/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

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
ros2 service call /get_fen interfaces/srv/GetFEN "{}"
ros2 service call /get_move interfaces/srv/GetMove "{fen: 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 2'}"
ros2 service call /move interfaces/srv/Move "{move: 'e2e4'}"
```

### 7.4 Проверка логов

```bash
tail -n 20 /workspaces/chess_ROS2_humble/log/moves.txt
```

Формат строки:
- time: DD.MM.YYYY HH:MM:SS | game_id: N | fen: ...

## 8. Известные проблемы текущей реализации

По результатам пробного запуска исправлены критичные ошибки старта и сервисной цепочки:

- Исправлен callback и API использования движка в stockfish_node.
- Исправлена обработка future/result в game.
- Исправлен callback сервиса move (возвращает response).
- Исправлена зависимость ultralytics в package.xml comp_vision.
- Убрана блокировка input() в game.
- Исправлено определение пути до log/moves.txt (без жесткой цепочки parent-parent).

Актуальные ограничения на текущий момент:

1. comp_vision и move пока содержат заглушки.
	 - Нет реального YOLO-пайплайна построения FEN.
	 - Нет низкоуровневого драйвера перемещения (serial-протокол к Arduino).
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

### Шаг 1. Стабилизировать сервисную логику
- Добавить валидацию FEN и UCI-ходов.
- Добавить обработку ошибочных/пустых ответов сервисов с retry.

### Шаг 2. Подключить реальный Stockfish pipeline
- Инициализация движка через путь к бинарнику.
- Настройка depth/skill/threads.

### Шаг 3. Реализовать CV-пайплайн
- Захват кадра.
- Детекция доски и фигур YOLO.
- Построение FEN.

### Шаг 4. Реализовать serial-шлюз к Arduino
- Добавить модуль транспорта в пакете move.
- Реализовать очередь команд, state machine и retries.

### Шаг 5. Добавить тесты
- Unit-тесты на парсинг FEN/UCI и протокол serial.
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

- В проекте есть пустой файл ros2_ws/launch/start.launch.py; актуальный launch расположен в пакете start: src/start/launch/start.launch.py.
- Папки ros2_ws/build, ros2_ws/install, ros2_ws/log являются артефактами сборки и обычно не редактируются вручную.
- Логи ходов хранятся вне ros2_ws: в корневом log/moves.txt.

---

Документ актуален для текущего состояния репозитория на момент ревизии.