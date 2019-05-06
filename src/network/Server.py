import asyncio
import logging
import os
import traceback
from abc import ABC, abstractmethod
from asyncio import StreamReader, StreamWriter
from typing import Callable, NoReturn, Tuple

import uvloop
from fastecdsa.point import Point

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message
from src.utils.Constants import END_OF_MESSAGE
from src.utils.Logger import Logger, LogLevels
from src.utils.PubSub import PubSub

uvloop.install()

logging.getLogger("asyncio").setLevel(logging.DEBUG)


class Server(ABC):
    BUFFER_SIZE = 2 ** 16 - 1
    EMPTY_BYTES = b''

    def __init__(self, port: int, host: str, private_key: int, id: int = None, log_level: LogLevels = LogLevels.DEBUG):
        self.host = host
        self.port = port
        self.server, self.loop = self.setup_server(self.run)
        self.id = id or os.getpid()
        self.setup(private_key, log_level, port)
        self.public_key = self.get_public_key(private_key)
        self.connections = {}

    def start(self) -> NoReturn:
        Logger.get_instance().debug_item(
            'Starting {} node {} on port {}'.format(self.__class__.__name__, self.id, self.port), LogLevels.PRODUCTION)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            Logger.get_instance().debug_item('KeyboardInterrupt, exiting...', LogLevels.ERROR)
            for task in asyncio.Task.all_tasks():
                task.cancel()
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.loop.close()

    async def wait_message(self, reader: StreamReader) -> bytes:
        blocks = []
        try:
            block = await reader.read(self.BUFFER_SIZE)
            blocks.append(block)
            while block[-3:] != END_OF_MESSAGE:
                block = await reader.read(self.BUFFER_SIZE)
                blocks.append(block)
            return b''.join(blocks)[:-3]
        except Exception as _:
            raise KeyboardInterrupt()

    async def _send(self, message, host, port) -> NoReturn:
        reader, writer = await asyncio.open_connection(host, port, loop=asyncio.get_event_loop())
        writer.write(message)
        self.loop.create_task(self.run(reader, writer))

    @staticmethod
    async def send_to_peer(connection: StreamWriter, message: Message) -> NoReturn:
        msg_serialized = message.serialize()
        connection.write(msg_serialized)
        await connection.drain()

    async def send_to(self, host: str, port: int, message: Message) -> NoReturn:
        msg_serialized = message.serialize()
        await self._send(msg_serialized, host, port)

    def setup_server(self, run: Callable):
        loop = asyncio.get_event_loop()
        loop.call_soon(asyncio.ensure_future, self.on_start())
        coro = asyncio.start_server(run, self.host, self.port, loop=loop)
        server = loop.run_until_complete(coro)
        return server, loop

    @abstractmethod
    async def on_start(self) -> NoReturn:
        raise Exception('Not implemented')

    @abstractmethod
    async def handle(self, message: bytes, connection) -> NoReturn:
        raise Exception('Not implemented')

    @staticmethod
    def get_public_key(private_key: int) -> Point:
        return Crypto.get_instance().get_ec().generate_public_from_private(private_key)

    @staticmethod
    def get_ip_port(address: str) -> Tuple[str, int]:
        bn_port = int(address.split(':')[1])
        bn_ip = address.split(':')[0]
        return bn_ip, bn_port

    @staticmethod
    @abstractmethod
    def setup(private_key: int, log_level: LogLevels, file: int) -> NoReturn:
        raise Exception('Not implemented')

    @staticmethod
    def to_address(address: Tuple[str, int]) -> str:
        return '{}:{}'.format(address[0] if address[0] != '127.0.0.1' else '0.0.0.0', address[1])

    def add_connection(self, writer: StreamWriter) -> NoReturn:
        address = self.to_address(writer.get_extra_info('peername'))
        self.connections[address] = writer

    async def drop_connection(self, connection: StreamWriter) -> NoReturn:
        address = self.to_address(connection.get_extra_info('peername'))
        if address not in self.connections: return
        conn = self.connections[address]
        if not conn.is_closing():
            connection.close()
            await connection.wait_closed()
            self.connections.pop(address)
        Logger.get_instance().debug_item('Connection with {} closed'.format(address))

    async def run(self, reader: StreamReader, writer: StreamWriter) -> NoReturn:
        Logger.get_instance().debug_item('New connection from {}'.format(writer.get_extra_info('peername')))
        self.add_connection(writer)
        while True:
            try:
                msg_bytes = await self.wait_message(reader)
                reader._eof = False
                if msg_bytes is self.EMPTY_BYTES:
                    reader._eof = True
                    await self.drop_connection(writer)
                    Logger.get_instance().debug_item(
                        'Connection with {} has been dropped'.format(writer.get_extra_info('peername')))
                    break
                await self.handle(msg_bytes, writer)
            except Exception as e:
                traceback.print_exc()
                Logger.get_instance().debug_item('An error has occurred: {}'.format(e.args[0]), LogLevels.ERROR)
                await PubSub().remove_all()
                await self.drop_connection(writer)
            except KeyboardInterrupt:
                return
