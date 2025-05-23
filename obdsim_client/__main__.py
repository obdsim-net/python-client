#!/usr/bin/env python3

import os
import time
import socket
import argparse
import threading
import logging
import json
import can
import sys

logger = logging.getLogger("obd2_client")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class OBD2ProxyClient:
    def __init__(self, config: str, host: str, port: int, channel: str) -> None:
        self._config_name = config
        self._sock = socket.create_connection((host, port))
        self._bus = can.interface.Bus(channel=channel, interface="socketcan")

    def start(self) -> None:
        if not self._send_handshake():
            logger.error("❌ Server rejected config. Exiting.")
            self._sock.close()
            sys.exit(1)

        threading.Thread(target=self._can_to_tcp, daemon=True).start()
        threading.Thread(target=self._tcp_to_can, daemon=True).start()
        logger.info(f"✅ Started proxy for '{self._config_name}'")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down proxy")
            self._sock.close()

    def _send_handshake(self) -> bool:
        payload = json.dumps({"config": self._config_name}) + "\n"
        self._sock.sendall(payload.encode())
        # Wait briefly to catch potential server-side rejection
        try:
            self._sock.settimeout(2)
            response = self._sock.recv(128).decode()
            if "config_not_found" in response:
                return False
        except socket.timeout:
            pass
        finally:
            self._sock.settimeout(None)
        return True

    def _can_to_tcp(self) -> None:
        while True:
            msg = self._bus.recv()
            if msg is None:
                continue
            data_hex = "".join(f"{b:02X}" for b in msg.data)
            frame = f"{msg.arbitration_id:X}#{data_hex}\n"
            try:
                self._sock.sendall(frame.encode())
            except Exception as e:
                logger.error(f"CAN→TCP send failed: {e}")
                break

    def _tcp_to_can(self) -> None:
        buffer = ""
        while True:
            try:
                data = self._sock.recv(1024).decode()
                if not data:
                    logger.info("Server disconnected")
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if "#" not in line:
                        continue
                    can_id_str, data_str = line.split("#", 1)
                    arbitration_id = int(can_id_str, 16)
                    payload = bytes(
                        int(data_str[i:i+2], 16)
                        for i in range(0, len(data_str), 2)
                    )
                    msg = can.Message(
                        arbitration_id=arbitration_id,
                        data=payload,
                        is_extended_id=arbitration_id > 0x7FF,
                    )
                    self._bus.send(msg)
            except Exception as e:
                logger.error(f"TCP→CAN receive failed: {e}")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OBD2 TCP↔CAN Proxy Client")
    parser.add_argument("--config", required=True, help="Config id")
    parser.add_argument("--host", default="port.obdsim.net", help="Server host")
    parser.add_argument("--port", type=int, default=1337, help="Server port")
    parser.add_argument("--channel", default="vcan0", help="CAN interface")
    args = parser.parse_args()

    client = OBD2ProxyClient(
        config=args.config,
        host=args.host,
        port=args.port,
        channel=args.channel,
    )

    client.start()
