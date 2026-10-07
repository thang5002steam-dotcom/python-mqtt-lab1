"""Bai 1: gui thong diep co ho ten, ma sinh vien va loi chao."""
from threading import Event
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "iot/lab/message"
connected = Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Ket noi bi tu choi: {reason_code}", flush=True)
    else:
        connected.set()
        print("Da ket noi broker.", flush=True)


def main():
    ho_ten = input("Ho ten sinh vien: ").strip()
    ma_sv = input("Ma sinh vien: ").strip()
    if not ho_ten or not ma_sv:
        print("Can nhap du ho ten va ma sinh vien.")
        return
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()  # Xu ly MQTT o luong nen de van nhap ban phim duoc.
        if not connected.wait(10):
            raise TimeoutError("Chua ket noi MQTT sau 10 giay.")
        while True:
            noi_dung = input("Loi chao (Enter = mac dinh, EXIT = dung): ").strip()
            if noi_dung.upper() == "EXIT":
                break
            noi_dung = noi_dung or "Xin chao tu client Python MQTT"
            payload = f"{noi_dung} - {ma_sv} - {ho_ten}"
            info = client.publish(TOPIC, payload, qos=1, retain=False)
            info.wait_for_publish(timeout=10)
            if not info.is_published():
                raise TimeoutError("Broker chua xac nhan thong diep.")
            print(f"Da gui: {payload}", flush=True)
    except KeyboardInterrupt:
        print("\nDung publisher.")
    except (OSError, RuntimeError) as exc:
        print(f"Loi: {exc}. Kiem tra broker va PORT.")
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
