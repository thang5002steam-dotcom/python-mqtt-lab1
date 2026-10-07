"""Bai 3: den mo phong nhan lenh va phan hoi trang thai."""
import json
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
CMD_TOPIC = "iot/lab/light01/cmd"
STATUS_TOPIC = "iot/lab/light01/status"
status = "OFF"  # Den tat khi chuong trinh vua khoi dong.


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Ket noi bi tu choi: {reason_code}", flush=True)
        client.disconnect()
        return
    client.subscribe(CMD_TOPIC, qos=1)


def on_subscribe(client, userdata, mid, reason_codes, properties):
    if any(code.is_failure for code in reason_codes):
        print("Broker tu choi subscribe.", flush=True)
        client.disconnect()
    else:
        print(f"SAN SANG nhan lenh: {CMD_TOPIC}; den dang {status}", flush=True)


def on_message(client, userdata, message):
    global status
    try:
        command = message.payload.decode("utf-8").strip().upper()
    except UnicodeDecodeError:
        print("Lenh khong phai chuoi UTF-8.", flush=True)
        return
    if command not in ("ON", "OFF"):
        print(f"Bo qua lenh sai: {command}", flush=True)
        return
    status = command
    payload = json.dumps({"device_id": "light01", "status": status})
    info = client.publish(STATUS_TOPIC, payload, qos=1, retain=False)
    # Khong wait_for_publish trong callback: luong MQTT can tiep tuc xu ly.
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        print("Khong the gui phan hoi trang thai.", flush=True)
    else:
        print(f"Nhan lenh {command} -> den {status}\nGui trang thai: {payload}",
              flush=True)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDung thiet bi den.")
    except OSError as exc:
        print(f"Loi ket noi: {exc}. Hay khoi dong broker truoc.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
