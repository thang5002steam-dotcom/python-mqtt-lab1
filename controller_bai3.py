"""Bai 3: nhap ON/OFF, gui lenh va nhan trang thai tu den."""
import json
from threading import Event
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
CMD_TOPIC = "iot/lab/light01/cmd"
STATUS_TOPIC = "iot/lab/light01/status"
ready = Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Ket noi bi tu choi: {reason_code}", flush=True)
    else:
        client.subscribe(STATUS_TOPIC, qos=1)


def on_subscribe(client, userdata, mid, reason_codes, properties):
    if any(code.is_failure for code in reason_codes):
        print("Broker tu choi subscribe.", flush=True)
    else:
        ready.set()
        print(f"SAN SANG nhan trang thai: {STATUS_TOPIC}", flush=True)


def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode("utf-8"))
        if data["device_id"] != "light01" or data["status"] not in ("ON", "OFF"):
            raise ValueError("Sai device_id hoac status")
    except (ValueError, UnicodeDecodeError, KeyError, TypeError) as exc:
        print(f"Phan hoi khong hop le: {exc}", flush=True)
        return
    print(f"\nTrang thai nhan duoc:\n{json.dumps(data)}", flush=True)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()  # Vua cho ban phim, vua nhan phan hoi MQTT.
        if not ready.wait(10):
            raise TimeoutError("Chua subscribe duoc sau 10 giay.")
        while True:
            command = input("Nhap lenh ON/OFF/EXIT: ").strip().upper()
            if command == "EXIT":
                break
            if command not in ("ON", "OFF"):
                print("Lenh sai. Chi nhap ON, OFF hoac EXIT.")
                continue
            info = client.publish(CMD_TOPIC, command, qos=1, retain=False)
            info.wait_for_publish(timeout=10)
            if not info.is_published():
                raise TimeoutError("Broker chua xac nhan lenh.")
            print(f"Da gui lenh {command} toi light01", flush=True)
    except (KeyboardInterrupt, EOFError):
        print("\nDung controller.")
    except (OSError, RuntimeError) as exc:
        print(f"Loi: {exc}. Kiem tra broker va PORT.")
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
