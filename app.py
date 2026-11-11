import logging
import socket
import time

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

# 1. Логування: у файл app.log і в консоль, у потрібному форматі
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("app")
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # прибрати службовий шум Flask

# 2. Імітаційний StatsD: сюди відправляємо UDP-повідомлення про помилки
STATSD_HOST = "127.0.0.1"
STATSD_PORT = 8125
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_to_statsd(message):
    udp.sendto(message.encode("utf-8"), (STATSD_HOST, STATSD_PORT))


# 3. Сам застосунок
app = Flask(__name__)
START_TIME = time.time()
request_count = 0


@app.before_request
def count_request():
    global request_count
    request_count += 1


@app.route("/")
def index():
    log.info("Запит на / - сервіс працює")
    return "Сервіс працює"


@app.route("/error")
def error():
    log.warning("Запит на /error - зараз буде помилка")
    return 1 / 0  # ZeroDivisionError


@app.route("/status")
def status():
    uptime = round(time.time() - START_TIME, 1)
    log.info("Запит на /status: uptime=%s с, запитів=%s", uptime, request_count)
    return jsonify(status="ok", uptime_seconds=uptime, requests_total=request_count)


# 4. Обробник БУДЬ-ЯКОГО винятку
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):  # наприклад, 404 - це не збій коду
        log.warning("HTTP %s на %s", e.code, request.path)
        return e
    log.exception("Помилка на %s: %s", request.path, e)
    send_to_statsd(f"app.errors:1|c|#route:{request.path},error:{type(e).__name__}")
    return jsonify(error=type(e).__name__, message=str(e)), 500


if __name__ == "__main__":
    log.info("Застосунок запущено на http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)

