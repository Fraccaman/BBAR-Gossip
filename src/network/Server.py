import asyncio
import logging
import os
from abc import ABC, abstractmethod
from asyncio import StreamReader, StreamWriter
from typing import Callable, NoReturn

import uvloop

from src.cryptography.Crypto import Crypto
from src.messages.Message import Message
from src.utils.Logger import Logger, LogLevels

uvloop.install()

logging.getLogger("asyncio").setLevel(logging.DEBUG)


class Server(ABC):
    BUFFER_SIZE = 2 ** 16

    def __init__(self, port: int, host: str, private_key: int, id: int = None, log_level: LogLevels = LogLevels.DEBUG):
        self.host = host
        self.port = port
        self.server, self.loop = self.setup_server(self.run)
        self.id = id or os.getpid()
        self.setup(private_key, log_level, port)
        self.public_key = self.get_public_key(private_key)

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
        try:
            msg_bytes = await reader.read(self.BUFFER_SIZE)
            return msg_bytes
        except Exception as _:
            raise KeyboardInterrupt()

    async def _send(self, message, host, port) -> NoReturn:
        reader, writer = await asyncio.open_connection(host, port, loop=asyncio.get_event_loop())
        writer.write(message)
        await self.run(reader, writer)

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
    async def on_start(self):
        raise Exception('Not implemented')

    @abstractmethod
    async def handle(self, message: bytes, connection):
        raise Exception('Not implemented')

    @staticmethod
    def get_public_key(private_key):
        return Crypto.get_instance().get_ec().generate_public_from_private(private_key)

    @staticmethod
    def get_ip_port(address: str):
        bn_port = int(address.split(':')[1])
        bn_ip = address.split(':')[0]
        return bn_ip, bn_port

    @staticmethod
    @abstractmethod
    def setup(private_key: int, log_level: LogLevels, file: int):
        raise Exception('Not implemented')

    async def run(self, reader: StreamReader, writer: StreamWriter) -> NoReturn:
        Logger.get_instance().debug_item('New connection from {}'.format(writer.get_extra_info('peername')))
        while True:
            try:
                msg_bytes = await self.wait_message(reader)
                if msg_bytes is b'':
                    writer.close()
                    await writer.wait_closed()
                    Logger.get_instance().debug_item(
                        'Connection with {} has been dropped'.format(writer.get_extra_info('peername')))
                    break
                await self.handle(msg_bytes, writer)
            except Exception as e:
                Logger.get_instance().debug_item('An error has occurred: {}'.format(e.args[0]), LogLevels.ERROR)
                writer.close()
                await writer.wait_closed()
            except KeyboardInterrupt:
                return
