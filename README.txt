# Thực hành Python MQTT buổi 1

Họ tên: **Điền họ tên của bạn**  
Mã sinh viên: **Điền mã sinh viên của bạn**

Bộ mã mẫu mô phỏng gửi nhận tin nhắn, cảm biến nhiệt độ độ ẩm và đèn thông minh. Không cần cảm biến hoặc đèn thật. Hãy đọc code, chạy từng bài và ghi lại kết quả thực tế trước khi nộp.

## 1. Yêu cầu theo đề

| Bài | File gửi hoặc thiết bị | File nhận hoặc điều khiển | Điều cần đạt |
|---|---|---|---|
| 1 | publisher_bai1.py | subscriber_bai1.py | Gửi họ tên, mã SV và lời chào; bên nhận in topic, nội dung, thời điểm |
| 2 | sensor_publisher_bai2.py | monitor_subscriber_bai2.py | Gửi JSON mỗi 3 giây; cảnh báo nhiệt độ > 35°C và độ ẩm < 40% |
| 3 | device_bai3.py | controller_bai3.py | Gửi ON/OFF; thiết bị đổi trạng thái và trả JSON trạng thái sau mỗi lệnh hợp lệ |

Hạn nộp trong đề: **23:59 Thứ Bảy 10/10/2026**. Nộp link GitHub vào nhóm Zalo chung của lớp. Đề ghi README.md ở phần đầu và README.txt ở phần cuối; bộ này có cả hai, cùng nội dung. Khi chỉnh README, hãy cập nhật cả hai.

## 2. Hiểu MQTT trước khi chạy

- Broker: chương trình trung gian nhận và chuyển bản tin. Bộ này dùng Eclipse Mosquitto trên máy của bạn.
- Publisher: chương trình gửi bản tin.
- Subscriber: chương trình đăng ký nhận bản tin.
- Topic: tên kênh, ví dụ `iot/lab/message`. Bên gửi và bên nhận phải dùng đúng cùng tên kênh.
- Payload: nội dung bản tin; có thể là văn bản hoặc chuỗi JSON.

Luồng bài 1: Publisher -> Broker -> Subscriber.

Luồng bài 2: Sensor -> Broker -> Monitor.

Luồng bài 3:

```text
Controller -- topic iot/lab/light01/cmd --> Broker --> Device
Controller <-- topic iot/lab/light01/status -- Broker <-- Device
```

Đèn trong bài 3 chỉ là biến `status` trong Python. Đổi ON/OFF sẽ đổi biến và in kết quả ra màn hình.

## 3. Chuẩn bị trên Windows

### Bước 1: Giải nén và mở thư mục

1. Giải nén ZIP, mở thư mục `python_mqtt_lab` bên trong.
2. Trong VS Code, chọn File -> Open Folder -> chọn thư mục đó.
3. Chọn Terminal -> New Terminal. Các lệnh dưới đây dùng PowerShell, chạy trong thư mục có các file .py.
4. Kiểm tra bằng `dir`: phải thấy sáu file Python và `mosquitto.conf`.

### Bước 2: Kiểm tra Python

```powershell
py --version
```

Nếu chưa có Python, tải bản Python 3 tại https://www.python.org/downloads/windows/ và cài theo hướng dẫn của bộ cài. Mở lại terminal sau khi cài. Nếu chỉ có lệnh `python`, dùng `python --version` và thay `py` bằng `python` ở lệnh tạo môi trường tiếp theo.

### Bước 3: Tạo môi trường và cài thư viện

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import paho.mqtt.client as mqtt; print(mqtt.CallbackAPIVersion.VERSION2)"
```

Lệnh cuối cần in `CallbackAPIVersion.VERSION2`. Bộ mẫu dùng paho-mqtt 2.1.0 và API callback VERSION2. Không cần kích hoạt môi trường; luôn gọi đúng `.venv\Scripts\python.exe` như trên. Nhờ vậy tránh lỗi PowerShell chặn Activate.ps1.

### Bước 4: Cài Mosquitto

1. Mở https://mosquitto.org/download/.
2. Chọn bộ cài Windows x64 nếu máy chạy Windows 64-bit.
3. Cài Mosquitto. Ghi lại thư mục cài; lệnh dưới giả sử `C:\Program Files\mosquitto`.
4. Nếu bộ cài có lựa chọn cài/chạy Windows Service, có thể bỏ chọn để tự chạy broker trong terminal và nhìn log dễ hơn.

### Bước 5: Cấu hình và chạy broker

File `mosquitto.conf` đã có:

```text
listener 1883 127.0.0.1
allow_anonymous true
persistence false
```

- `listener 1883 127.0.0.1`: nhận kết nối ở cổng 1883 trên chính máy này.
- `allow_anonymous true`: bài lab không yêu cầu tên đăng nhập/mật khẩu.
- `persistence false`: không lưu dữ liệu broker xuống ổ đĩa qua lần khởi động lại.

Ở terminal thứ nhất, chạy:

```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -c .\mosquitto.conf -v
```

Nếu cài ở chỗ khác, thay đường dẫn chương trình. Dấu `&` là cách PowerShell chạy đường dẫn có dấu cách. Log cần cho thấy broker mở cổng 1883 và đang chạy; nội dung chính xác tùy phiên bản. Giữ terminal này mở suốt buổi thực hành.

Mở terminal thứ hai trong cùng thư mục và kiểm tra:

```powershell
Test-NetConnection 127.0.0.1 -Port 1883
```

Kết quả cần có `TcpTestSucceeded : True`. Kiểm tra này chỉ chứng minh cổng đang mở; bước chạy Python tiếp theo mới kiểm tra MQTT.

Trong cả sáu file Python đã có:

```python
BROKER = "127.0.0.1"
PORT = 1883
```

Giữ nguyên nếu mọi chương trình chạy trên một máy. Địa chỉ 127.0.0.1 luôn trỏ về máy đang chạy chương trình; cấu hình này không dùng để chạy hai máy khác nhau.

## 4. Bài 1: Gửi và nhận thông điệp

### Chạy và kiểm tra

1. Giữ broker chạy ở terminal 1.
2. Terminal 2 chạy bên nhận trước:

```powershell
.\.venv\Scripts\python.exe .\subscriber_bai1.py
```

3. Đợi dòng `SAN SANG nhan tren topic: iot/lab/message`.
4. Mở terminal 3 trong cùng thư mục, chạy:

```powershell
.\.venv\Scripts\python.exe .\publisher_bai1.py
```

5. Nhập họ tên thật và mã sinh viên thật. Ví dụ chỉ để minh họa: Nguyen Van A, B23DCCN001.
6. Khi hỏi lời chào, nhấn Enter để gửi `Xin chao tu client Python MQTT` hoặc nhập lời chào của bạn.
7. Terminal 2 cần hiện đủ ba thông tin:

```text
Nhan duoc message:
Topic: iot/lab/message
Payload: Xin chao tu client Python MQTT - B23DCCN001 - Nguyen Van A
Time: 10:15:20
```

Tên, mã SV và thời gian sẽ khác ví dụ. Nhập thêm lời chào để thử gửi nhiều lần. Nhập EXIT ở publisher và nhấn Ctrl+C ở subscriber để dừng. Giữ broker chạy cho bài tiếp theo.

### Đọc code theo thứ tự

1. `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)` tạo một MQTT client.
2. `client.on_connect = on_connect` đăng ký hàm tự chạy khi broker trả kết quả kết nối.
3. `client.connect(BROKER, PORT, 60)` mở kết nối.
4. Publisher dùng `loop_start()` để xử lý MQTT ở luồng nền trong khi luồng chính chờ bàn phím.
5. `connected.wait(10)` đợi broker xác nhận kết nối, tối đa 10 giây.
6. `publish(TOPIC, payload, ...)` gửi nội dung lên topic.
7. Subscriber gọi `subscribe(TOPIC, ...)` sau khi kết nối thành công. `on_subscribe` báo khi broker đã xác nhận đăng ký.
8. Khi có bản tin, `on_message` tự chạy. Payload nhận là bytes, nên cần `.decode("utf-8")` để thành chữ.
9. `datetime.now()` ghi thời điểm nhận, đúng yêu cầu bài 1.

Mẫu dùng `retain=False`: chạy bên nhận trước khi gửi. Bản tin trước thời điểm đăng ký không tự xuất hiện lại.

## 5. Bài 2: Mô phỏng cảm biến

### Chạy bình thường

Terminal 2 chạy:

```powershell
.\.venv\Scripts\python.exe .\monitor_subscriber_bai2.py
```

Đợi `SAN SANG`. Terminal 3 chạy:

```powershell
.\.venv\Scripts\python.exe .\sensor_publisher_bai2.py
```

Cảm biến sinh nhiệt độ 20–40°C và độ ẩm 30–80%, làm tròn một chữ số thập phân. Mỗi vòng gửi JSON rồi đợi 3 giây trước lần gửi tiếp theo. JSON có đúng ba trường:

```json
{"device_id": "sensor01", "temperature": 28.5, "humidity": 65.2}
```

Monitor cần hiển thị device, temperature, humidity. Khi có giá trị phù hợp, xuất cảnh báo. Dừng sensor bằng Ctrl+C rồi thử chế độ kiểm tra dưới đây; monitor vẫn để chạy.

### Kiểm tra chắc chắn các cảnh báo

```powershell
.\.venv\Scripts\python.exe .\sensor_publisher_bai2.py --demo
```

Chế độ bổ sung này lặp lại năm mẫu, cách nhau khoảng 3 giây:

| Nhiệt độ | Độ ẩm | Kết quả cần thấy |
|---|---|---|
| 28.5 | 65.2 | Không cảnh báo |
| 36.1 | 65.2 | CANH BAO: Nhiet do cao |
| 28.5 | 38.7 | CANH BAO: Do am thap |
| 36.1 | 38.7 | Cả hai cảnh báo |
| 35.0 | 40.0 | Không cảnh báo |

35°C không vượt ngưỡng và 40% không thấp hơn ngưỡng. Phải dùng `> 35` và `< 40`, không dùng `>=` hoặc `<=`. Hai điều kiện dùng hai `if` riêng, để có thể in cả hai cảnh báo trong cùng một lần nhận.

### Đọc code

- `random.uniform(...)`: sinh số ngẫu nhiên trong khoảng đã chọn.
- `make_data(...)`: tạo dictionary Python với thông tin cảm biến.
- `json.dumps(...)`: chuyển dictionary thành chuỗi JSON để gửi.
- `time.sleep(3)`: đợi 3 giây trước vòng gửi kế tiếp; thời gian xử lý/gửi mạng làm chu kỳ thực tế dài hơn 3 giây một chút.
- Bên nhận dùng `json.loads(...)`: đọc JSON thành dictionary.
- Lấy dữ liệu bằng `data["temperature"]`, `data["humidity"]`, rồi kiểm tra ngưỡng.
- `try/except` giúp monitor báo payload sai thay vì dừng khi nhận JSON hỏng hoặc thiếu trường.

Sau khi kiểm tra, dừng cả sensor và monitor bằng Ctrl+C. Khi trình diễn dữ liệu ngẫu nhiên, chạy sensor không có `--demo`.

## 6. Bài 3: Điều khiển đèn hai chiều

### Chạy và kiểm tra

Terminal 2 chạy thiết bị trước:

```powershell
.\.venv\Scripts\python.exe .\device_bai3.py
```

Đợi `SAN SANG nhan lenh...`. Đèn ban đầu OFF. Terminal 3 chạy:

```powershell
.\.venv\Scripts\python.exe .\controller_bai3.py
```

Ở controller:

1. Nhập `ON` rồi Enter. Device phải in đèn ON; controller phải nhận JSON có `"status": "ON"`.
2. Nhập `OFF` rồi Enter. Cả hai phía phải thể hiện OFF.
3. Nhập `ON` hai lần. Thiết bị vẫn phải phản hồi sau mỗi lệnh hợp lệ, kể cả trạng thái không thay đổi.
4. Nhập `ABC`. Controller phải báo lệnh sai và không gửi lệnh này.
5. Nhập `EXIT` để thoát controller. Dừng device bằng Ctrl+C.

Ví dụ phản hồi:

```text
Trang thai nhan duoc:
{"device_id": "light01", "status": "ON"}
```

Dòng phản hồi có thể xen giữa lời nhắc nhập vì luồng MQTT và luồng bàn phím chạy đồng thời. Cứ nhập ON/OFF rồi Enter như bình thường.

### Đọc code

- Controller vừa publish topic `iot/lab/light01/cmd`, vừa subscribe topic `iot/lab/light01/status`.
- Device làm chiều ngược lại: subscribe `cmd`, publish `status`.
- Controller gửi chuỗi ON/OFF, không gửi JSON lệnh.
- Device đọc chuỗi, kiểm tra hợp lệ, gán `status = command`, rồi gửi JSON trạng thái.
- `global status` cho phép hàm xử lý bản tin cập nhật biến trạng thái của thiết bị.
- Device dùng `loop_forever()` vì công việc chính là chờ lệnh.
- Controller dùng `loop_start()` vì phải vừa chờ người dùng nhập vừa nhận phản hồi.
- Việc controller in "Đã gửi lệnh" chỉ xác nhận gửi qua broker; phản hồi JSON từ device mới cho biết thiết bị đã xử lý lệnh.

## 7. Các điểm kỹ thuật chung

- `qos=1`: yêu cầu broker xác nhận nhận bản tin. Có thể có bản tin trùng trong một số tình huống mạng; bài mô phỏng vẫn xử lý được.
- `wait_for_publish(timeout=10)` và `is_published()`: publisher kiểm tra việc gửi đã hoàn tất với broker trước khi báo đã gửi. Điều này không chứng minh subscriber đã xử lý bản tin.
- Không chờ `wait_for_publish()` trong callback của device, vì chính luồng đó phải tiếp tục xử lý MQTT để hoàn tất việc gửi.
- Sáu file tự chạy độc lập, không cần import file trợ giúp. Giữ nguyên topic theo đề.
- Chưa có kiểm tra trực tiếp với Mosquitto trên máy của bạn. Hãy hoàn thành các bước chạy và kiểm tra bên trên trước khi ghi kết quả đạt được hoặc nộp.

## 8. Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Không nhận ra lệnh py | Thử python; nếu cả hai không có, cài Python và mở lại terminal |
| No module named paho | Cài bằng `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`, chạy bằng cùng Python này |
| Không tìm thấy mosquitto.exe | Kiểm tra thư mục đã cài rồi sửa đường dẫn trong lệnh chạy |
| ConnectionRefusedError hoặc WinError 10061 | Broker chưa chạy, đã tắt, hoặc PORT sai; khởi động broker và thử lại |
| Address already in use hoặc cổng 1883 bị chiếm | Có broker/service khác đang chạy. Nếu là Mosquitto đã cài, có thể dùng broker đó. Nếu cần chạy cấu hình lab, mở services.msc, tìm Mosquitto Broker, dừng service rồi chạy lại lệnh lab |
| Đã gửi nhưng không thấy nhận | Đợi bên nhận báo SAN SANG trước, rồi gửi lại; đối chiếu BROKER, PORT và topic ở cả hai file |
| Không có cảnh báo bài 2 | Giá trị ngẫu nhiên chưa vượt ngưỡng; dùng --demo và kiểm tra đủ năm mẫu |
| Bài 3 đã gửi nhưng chưa nhận trạng thái | Chạy device trước, đợi SAN SANG; kiểm tra đúng hai topic cmd/status |
| Lỗi CallbackAPIVersion | Đang dùng paho-mqtt cũ hoặc sai môi trường; cài lại requirements bằng đúng Python .venv |
| Lệnh chạy báo không tìm thấy .py | Terminal đang ở sai thư mục; dùng dir để kiểm tra rồi mở lại terminal ở thư mục bài |

## 9. Ghi kết quả thực tế

Sau khi tự chạy, thay các dòng sau bằng kết quả thật. Không ghi đã đạt nếu chưa kiểm tra.

- Bài 1: [Ghi đã nhận đúng họ tên, mã SV, lời chào, topic và giờ nhận hay chưa.]
- Bài 2: [Ghi đã nhận JSON định kỳ và kết quả năm mẫu demo.]
- Bài 3: [Ghi phản hồi ON, OFF, lệnh lặp và xử lý lệnh sai.]
- Môi trường: [Ghi phiên bản Python, Mosquitto nếu có; paho-mqtt 2.1.0.]

Broker sử dụng: Eclipse Mosquitto, host `127.0.0.1`, port `1883`, MQTT TCP, không yêu cầu tài khoản trong cấu hình lab trên một máy. Cách cấu hình và chạy nằm ở mục 3.

## 10. Đưa lên GitHub và nộp

1. Điền họ tên/mã SV ở đầu README.md và README.txt, cập nhật kết quả thực tế ở mục 9.
2. Đăng nhập GitHub, chọn New repository, đặt tên ví dụ `python-mqtt-lab1`.
3. Chọn Public nếu lớp cần mở link mà không có quyền truy cập riêng. Bấm Create repository.
4. Tìm liên kết uploading an existing file trên trang repo mới hoặc Add file -> Upload files.
5. Tải lên sáu file .py, README.md, README.txt, requirements.txt, mosquitto.conf và .gitignore. Không tải .venv hoặc __pycache__.
6. Bấm Commit changes. Mở lại trang repo và kiểm tra các file hiện đầy đủ, README hiển thị rõ hướng dẫn.
7. Thử mở repo bằng cửa sổ ẩn danh nếu repo Public, để kiểm tra giảng viên có thể xem.
8. Sao chép link repo dạng `https://github.com/ten-tai-khoan/python-mqtt-lab1`, gửi vào nhóm Zalo lớp trước hạn trong đề.

Ảnh màn hình chạy bài có thể giúp minh họa nếu bạn muốn thêm; đề không ghi bắt buộc nộp ảnh. Gợi ý mở rộng như nhiều cảm biến hoặc nhiều thiết bị không phải phần bắt buộc.

## 11. Tài liệu chính thức

- Python cho Windows: https://www.python.org/downloads/windows/
- Paho MQTT Python: https://eclipse.dev/paho/clients/python/docs/
- Mosquitto tải về: https://mosquitto.org/download/
- Cấu hình Mosquitto: https://mosquitto.org/man/mosquitto-conf-5.html
- Lệnh chạy Mosquitto: https://mosquitto.org/man/mosquitto-8.html
