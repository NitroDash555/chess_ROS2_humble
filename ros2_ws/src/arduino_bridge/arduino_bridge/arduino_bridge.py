import rclpy
from rclpy.node import Node
import serial
import serial.tools.list_ports

from std_msgs.msg import String

class BridgeNode(Node):
    def __init__(self):
        super().__init__('bridge')

        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('vendor_id', 'xxxx')
        self.declare_parameter('product_id', 'xxxx')
        self.declare_parameter('reconnect_period', 2.0)
        self.declare_parameter('command_topic', '/arduino/command')

        self.baudrate = self.get_parameter('baudrate').value
        self.vid = self.get_parameter('vendor_id').value.lower()
        self.pid = self.get_parameter('product_id').value.lower()

        self.serial_port = None

        loop_period = self.get_parameter('reconnect_period').value
        self.connect_timer = self.create_timer(loop_period, self.check_and_connect)

        command_topic = self.get_parameter('command_topic').value
        self.command_sub = self.create_subscription(
            String, command_topic, self.on_command, 10)

    def find_arduino_port(self):
        """Сканирует систему и возвращает имя порта по VID/PID"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Преобразуем hex-значения в строки для сравнения
            vid_str = f"{port.vid:04x}" if port.vid else ""
            pid_str = f"{port.pid:04x}" if port.pid else ""
            
            if vid_str == self.vid and pid_str == self.pid:
                return port.device
        return None

    def check_and_connect(self):
        if self.serial_port is None or not self.serial_port.is_open:
            port_name = self.find_arduino_port()
            
            if not port_name:
                self.get_logger().error(f"Arduino (VID:{self.vid} PID:{self.pid}) не найдена в системе.")
                return

            try:
                self.get_logger().info(f"Найдено устройство на {port_name}. Подключение...")
                self.serial_port = serial.Serial(port_name, self.baudrate, timeout=1)
                self.get_logger().info("Успешно подключено!")
            except serial.SerialException as e:
                # Если под обычным пользователем нет прав (MODE="0666" не был задан через udev),
                # этот блок поймает PermissionError и выведет подсказку.
                self.get_logger().error(f"Ошибка открытия порта {port_name}: {e}")
                self.serial_port = None

    def on_command(self, msg):
        """Слушатель топика: любой String уходит в Arduino без ожидания ответа.

        Формат строки разбирает сам Arduino, например:
            MOVE;x;y;z    - движение
            SCREEN;Hello  - вывод на экран
        """
        if self.send_command(msg.data.encode()):
            self.get_logger().info(f'Отправлено в Arduino: {msg.data}')

    def send_command(self, data: bytes) -> bool:
        """Отправляет команду в Arduino. Без подключённого порта ничего не делает."""
        if self.serial_port is None or not self.serial_port.is_open:
            self.get_logger().warn('Serial port не подключена, команда пропущена')
            return False

        try:
            self.serial_port.write(data)
            return True
        except serial.SerialException as e:
            # Если кабель отсоединили, объект serial может ещё считать порт открытым.
            # Закрываем сами, чтобы check_and_connect смог переподключиться.
            self.get_logger().warn(f'Ошибка записи, связь потеряна: {e}')
            self._close_port()
            return False

    def _close_port(self):
        if self.serial_port is not None:
            try:
                self.serial_port.close()
            except serial.SerialException:
                pass
            self.serial_port = None
            self.get_logger().info('Serial port закрыта')

    def on_shutdown(self):
        self._close_port()


def main(args=None):
    rclpy.init(args=args)
    node = BridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()

