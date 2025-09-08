import socket
import re
from typing import Tuple

HOST = "192.0.2.123"
PORT = 50000          # ou a “virtual COM port” configurada
ENC  = "ascii"
EOL  = b"\r\n"
PROMPT_BYTE = b">"    # prompts típicos terminam com '>'

def recv_until(sock: socket.socket, end: bytes = PROMPT_BYTE, timeout: float = 5.0) -> bytes:
    sock.settimeout(timeout)
    buf = bytearray()
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
        if end in buf:
            break
    return bytes(buf)

def send_cmd(sock: socket.socket, cmd: str, wait_prompt: bool = True) -> str:
    sock.sendall(cmd.encode(ENC) + EOL)
    if wait_prompt:
        data = recv_until(sock)
        return data.decode(ENC, errors="ignore")
    return ""

def parse_status_value(text: str) -> Tuple[int, float]:
    m = re.search(r"Status:(\d+)\s+Value:([^\s]+)", text)
    if not m:
        raise ValueError(f"Resposta inesperada: {text!r}")
    return int(m.group(1)), float(m.group(2))

with socket.create_connection((HOST, PORT), timeout=5) as s:
    # ler banner/prompt inicial
    recv_until(s)

    # sequência segura
    send_cmd(s, "close")
    send_cmd(s, "open")

    measurement = "TAMeasQMH101_1"
    signal = "TA"

    out = send_cmd(s, f"LASTVAL {measurement} {signal}")
    status, value = parse_status_value(out)
    print({"status": status, "value": value})
