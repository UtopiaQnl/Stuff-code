from __future__ import annotations

import sys
from socket import error as SocketErrors, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gethostname

__all__ = ('Socket', SocketErrors)


class Socket(object):
    """
    Оболочка для <class socket> из socket.

    Python ver. = 3.9+
    """
    __address: str | None
    __port: int | None
    __socket: socket
    __another_socket: socket
    _hostname: str | None
    sep: str | None
    buffer_size: int

    client_mode: bool

    __slots__ = (
        '__address', '__port', '__socket', '__another_socket', '_hostname', 'sep', 'buffer_size', 'client_mode'
    )

    def __init__(self, another_socket=None, addr=None, port=None, sep="<|>", buffer=1024 * 16_384):
        """ Создает сокет с уже встроенными параметрами.

        :param addr: Адрес сокета. ip.
        :param port: Порт сокета.
        :param another_socket: Другой сокет. Для совместимости подключенных сокетов.
        :param sep: Разделитель для команды. По умолчанию <|>.
        :param buffer: Буфер для пакета отправляемых данных. По умолчанию 16Mb.
        """

        self.client_mode = True if another_socket is not None else False

        if self.client_mode:
            self.__another_socket = another_socket
        else:
            self.__socket = socket(family=AF_INET, type=SOCK_STREAM, proto=0)
            self.__socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

        self.__address = addr  # TODO сделать проверку на валидность адреса и порта + исключения
        self.__port = port

        self._hostname = gethostname()
        self.sep = sep
        self.buffer_size = buffer

    def bind(self, listen: 'int >= 1' = 3) -> bool:
        """ Связывает __address и __port с __socket

        :param listen: Количество подключений, которые система разрешит, прежде чем отклонять новые подключения.
        :return: bool
        """
        if self.client_mode:
            raise Warning('Клиент не может настроить свой сокет как серверный!')

        listen = 1 if listen <= 0 else listen  # TODO сделать проверку на валидность введенных данных
        try:
            self.__socket.bind((self.__address, self.__port))
            self.__socket.listen(listen)
        except SocketErrors as E:
            print('Создание сокета - Провалилось!\n', E)
            sys.exit()

    def accept(self) -> (socket, (str, int)):
        """ Ждет входящих подключений. Возвращает новый сокет и информацию об подключившимся в виде кортежа

        :return: (socket object, address info = (address, port))
        """
        if self.client_mode:
            raise Warning('Клиент не может принимать других соединений! Он клиент...')

        connect, address_info = self.__socket.accept()
        return Socket(another_socket=connect, addr=address_info[0], port=address_info[1]), address_info

    def connect(self, addr: (str, int) = None) -> None:
        """ Подключается к другому сокету по addr

        :param addr: последовательность (address, port).
        :return: None
        """
        if self.client_mode:
            raise Warning('Клиент не может подключится к серверу... Он уже это сделал.')

        self.__init__(addr=self.__address, port=self.__port, sep=self.sep, buffer=self.buffer_size)
        addr = (self.__address, self.__port) if not addr else addr
        self.__socket.connect(addr)

    def recv(self, buffer=None, encoding='utf8', decode=True) -> str | bytes:
        """ Получение данных их сокета, размер которые равен buffer. Возвращает эти-же байты или дешифрованную строку

        :param buffer: размер буфера получаемых байт.
        :param encoding: кодировка для расшифровки принятых байт.
        :param decode: нужно ли дешифровать данные.
        :return: str | bytes
        """
        buffer = buffer if buffer else self.buffer_size

        if self.client_mode:
            if decode:
                data = self.__another_socket.recv(buffer).decode(encoding=encoding)
            else:
                data = self.__another_socket.recv(buffer)
        else:
            if decode:
                data = self.__socket.recv(buffer).decode(encoding=encoding)
            else:
                data = self.__socket.recv(buffer)

        return data

    def sendall(self, data: str | bytes, encoding='utf8') -> None:
        """ Отправляет данные сокету. Если данные не байты, то он их кодирует кодировкой encoding.

        :param data: Данные для отправки.
        :param encoding: Кодировка байтов или данных.
        :return: None
        """
        data = data.encode(encoding) if isinstance(data, str) else data

        if self.client_mode:
            self.__another_socket.sendall(data)
        else:
            self.__socket.sendall(data)

    def close(self) -> None:
        """ Закрывает сокет

        :return: None
        """
        if self.client_mode:
            self.__another_socket.close()
        else:
            self.__socket.close()
