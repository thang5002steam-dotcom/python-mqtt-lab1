"""Bai 2: mo phong cam bien moi 3 giay. Them --demo de thu canh bao."""
import argparse
import json
import random
import time
from threading import Event
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "iot/lab/sensor01/data"
connected = Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Ket noi bi tu choi: {reason_code}", flush=True)
    else:
        connected.set()
        print("Da ket noi broker.", flush=True)


def make_data(index, demo=False):
    # Demo lap lai: binh thuong, chi nong, chi kho, ca hai, dung nguong.
    samples = [(28.5, 65.2), (36.1, 65.2), (28.5, 38.7),
               (36.1, 38.7), (35.0, 40.0)]
    if demo:
        temperature, humidity = samples[index % len(samples)]
    else:
        temperature = round(random.uniform(20, 40), 1)
        humidity = round(random.uniform(30, 80), 1)
    return {"device_id": "sensor01", "temperature": temperature,
            "humidity": humidity}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Thu cac nguong")
    args = parser.parse_args()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        if not connected.wait(10):
            raise TimeoutError("Chua ket noi MQTT sau 10 giay.")
        index = 0
        while True:
            payload = json.dumps(make_data(index, args.demo))
            info = client.publish(TOPIC, payload, qos=1, retain=False)
            info.wait_for_publish(timeout=10)
            if not info.is_published():
                raise TimeoutError("Broker chua xac nhan du lieu.")
            print(f"Da gui: {payload}", flush=True)
            index += 1
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nDung cam bien.")
    except (OSError, RuntimeError) as exc:
        print(f"Loi: {exc}. Kiem tra broker va PORT.")
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
