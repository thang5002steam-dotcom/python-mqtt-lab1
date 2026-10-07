"""Bai 1: nhan thong diep va hien thi thoi diem nhan."""
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "iot/lab/message"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Ket noi bi tu choi: {reason_code}", flush=True)
        client.disconnect()
        return
    client.subscribe(TOPIC, qos=1)  # Dang ky lai neu ket noi duoc khoi phuc.


def on_subscribe(client, userdata, mid, reason_codes, properties):
    if any(code.is_failure for code in reason_codes):
        print("Broker tu choi subscribe.", flush=True)
        client.disconnect()
    else:
        print(f"SAN SANG nhan tren topic: {TOPIC}", flush=True)


def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8", errors="replace")
    print(
        f"\nNhan duoc message:\nTopic: {message.topic}\n"
        f"Payload: {payload}\nTime: {datetime.now():%H:%M:%S}",
        flush=True,
    )


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()  # Cho va xu ly thong diep lien tuc.
    except KeyboardInterrupt:
        print("\nDung subscriber.")
    except OSError as exc:
        print(f"Loi ket noi: {exc}. Hay khoi dong broker truoc.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
