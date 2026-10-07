"""Bai 2: doc JSON va canh bao theo nguong trong de."""
import json
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "iot/lab/sensor01/data"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Ket noi bi tu choi: {reason_code}", flush=True)
        client.disconnect()
        return
    client.subscribe(TOPIC, qos=1)


def on_subscribe(client, userdata, mid, reason_codes, properties):
    if any(code.is_failure for code in reason_codes):
        print("Broker tu choi subscribe.", flush=True)
        client.disconnect()
    else:
        print(f"SAN SANG nhan tren topic: {TOPIC}", flush=True)


def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode("utf-8"))
        device_id = data["device_id"]
        temperature = data["temperature"]
        humidity = data["humidity"]
        if (not isinstance(device_id, str)
                or type(temperature) not in (int, float)
                or type(humidity) not in (int, float)):
            raise ValueError("Sai kieu du lieu trong payload")
    except (ValueError, UnicodeDecodeError, KeyError, TypeError) as exc:
        print(f"Payload khong hop le: {exc}", flush=True)
        return
    print(f"\nTime: {datetime.now():%H:%M:%S}\nDevice: {device_id}\n"
          f"Temperature: {temperature} C\nHumidity: {humidity} %", flush=True)
    # Hai if doc lap: mot ban tin co the gay ra ca hai canh bao.
    if temperature > 35:
        print("CANH BAO: Nhiet do cao", flush=True)
    if humidity < 40:
        print("CANH BAO: Do am thap", flush=True)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDung giam sat.")
    except OSError as exc:
        print(f"Loi ket noi: {exc}. Hay khoi dong broker truoc.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
