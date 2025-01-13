"""pysolarman.py"""

import types
import struct

from umodbus.client.tcp import read_coils, read_discrete_inputs, read_holding_registers, read_input_registers, write_single_coil, write_multiple_coils, write_single_register, write_multiple_registers, parse_response_adu

from .pysolarmanv5 import CONTROL
from .pysolarmanv5_async import PySolarmanV5Async


def is_ethernet_frame(frame):
    if frame[4] == CONTROL.REQUEST and (frame_len := len(frame)) and frame_len > 6 and (f := int.from_bytes(frame[5:6], byteorder = "big") == len(frame[6:])):
        return (f and int.from_bytes(frame[8:9], byteorder = "big") == len(frame[9:])) if frame_len > 9 else f # [0xa5, 0x17, 0x00, 0x10, 0x45, 0x03, 0x00, 0x98, 0x02]
    return False

def mb_compatibility(response, request):
    return response if not 8 <= (l := len(response)) <= 10 else response[:5] + b'\x06' + response[6:] + (request[l:10] if len(request) > 12 else (b'\x00' * (10 - l))) + b'\x00\x01'

class PySolarmanV5AsyncWrapper(PySolarmanV5Async):
    def __init__(self, address, serial, port, mb_slave_id, logger, auto_reconnect, socket_timeout):
        super().__init__(address, serial, port = port, mb_slave_id = mb_slave_id, logger = logger, auto_reconnect = auto_reconnect, socket_timeout = socket_timeout)

    @property
    def auto_reconnect(self):
        return self._needs_reconnect

    async def connect(self) -> bool:
        if not self.reader_task or self.reader_task.done():
            self.log.info(f"[{self.serial}] Connecting to {self.address}:{self.port}")
            await super().connect()
            return True
        return False

    async def disconnect(self) -> None:
        self.log.info(f"[{self.serial}] Disconnecting from {self.address}:{self.port}")
        await super().disconnect()

class PySolarmanAsync(PySolarmanV5AsyncWrapper):
    def __init__(self, address, serial, port, mb_slave_id, logger, auto_reconnect, socket_timeout):
        super().__init__(address, serial, port, mb_slave_id, logger, auto_reconnect, socket_timeout)
        self._passthrough = serial <= 0

    async def _tcp_send_receive_frame(self, mb_request_frame):
        return mb_compatibility(await self._send_receive_v5_frame(mb_request_frame), mb_request_frame)

    async def _tcp_parse_response_adu(self, mb_request_frame):
        return parse_response_adu(await self._tcp_send_receive_frame(mb_request_frame), mb_request_frame)

    def _received_frame_is_valid(self, frame):
        if self._passthrough or (is_valid := super()._received_frame_is_valid(frame)):
            return True
        if not is_valid and is_ethernet_frame(frame):
            self.log.debug("[%s] V5_ETHERNET_DETECTED: %s", self.serial, frame.hex(" "))
            self._passthrough = True
            return True
        return False

    async def read_coils(self, register_addr, quantity):
        if not self._passthrough:
            return await super().read_coils(register_addr, quantity)
        return await self._tcp_parse_response_adu(read_coils(self.mb_slave_id, register_addr, quantity))

    async def read_discrete_inputs(self, register_addr, quantity):
        if not self._passthrough:
            return await super().read_discrete_inputs(register_addr, quantity)
        return await self._tcp_parse_response_adu(read_discrete_inputs(self.mb_slave_id, register_addr, quantity))

    async def read_input_registers(self, register_addr, quantity):
        if not self._passthrough:
            return await super().read_input_registers(register_addr, quantity)
        return await self._tcp_parse_response_adu(read_input_registers(self.mb_slave_id, register_addr, quantity))

    async def read_holding_registers(self, register_addr, quantity):
        if not self._passthrough:
            return await super().read_holding_registers(register_addr, quantity)
        return await self._tcp_parse_response_adu(read_holding_registers(self.mb_slave_id, register_addr, quantity))

    async def write_single_coil(self, register_addr, value):
        if not self._passthrough:
            return await super().write_single_coil(register_addr, value)
        return await self._tcp_parse_response_adu(write_single_coil(self.mb_slave_id, register_addr, value))

    async def write_multiple_coils(self, register_addr, values):
        if not self._passthrough:
            return await super().write_multiple_coils(register_addr, values)
        return await self._tcp_parse_response_adu(write_multiple_coils(self.mb_slave_id, register_addr, values))

    async def write_single_register(self, register_addr, value):
        if not self._passthrough:
            return await super().write_holding_register(register_addr, value)
        return await self._tcp_parse_response_adu(write_single_register(self.mb_slave_id, register_addr, value))

    async def write_multiple_registers(self, register_addr, values):
        if not self._passthrough:
            return await super().write_multiple_holding_registers(register_addr, values)
        return await self._tcp_parse_response_adu(write_multiple_registers(self.mb_slave_id, register_addr, values))
