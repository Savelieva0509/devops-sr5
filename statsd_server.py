import socket
from datetime import datetime

HOST = "127.0.0.1"
PORT = 8125  # стандартний порт StatsD

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"Імітаційний StatsD слухає UDP {HOST}:{PORT} ... (Ctrl+C - зупинити)", flush=True)

try:
    while True:
        data, addr = sock.recvfrom(1024)
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] отримано від {addr[0]}:{addr[1]} -> {data.decode('utf-8')}", flush=True)
except KeyboardInterrupt:
    print("\nStatsD зупинено")
