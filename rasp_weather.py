import requests
from datetime import datetime
import RPi.GPIO as GPIO
import time

# ===== 1. Cấu hình LED =====
LED_XANH_PIN  = 17   # GPIO17: LED xanh
LED_VANG_PIN  = 27   # GPIO27: LED vàng
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_XANH_PIN, GPIO.OUT)
GPIO.setup(LED_VANG_PIN, GPIO.OUT)

# ===== 2. Tọa độ Đà Nẵng =====
lat, lon = 16.0471, 108.2068

# ===== 3. API URL  =====
url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}"
    "&current_weather=true"
    "&hourly=temperature_2m,relativehumidity_2m,precipitation,precipitation_probability"
    "&timezone=Asia%2FHo_Chi_Minh"
)

# ===== 4. Bảng mã weathercode =====
weather_map = {
    0: "Trời quang", 1: "Chủ yếu quang", 2: "Ít mây", 3: "U ám",
    45: "Sương mù", 48: "Sương đóng băng",
    51: "Mưa phùn nhẹ", 53: "Mưa phùn vừa", 55: "Mưa phùn dày",
    56: "Mưa phùn đóng băng nhẹ", 57: "Mưa phùn đóng băng dày",
    61: "Mưa nhẹ", 63: "Mưa vừa", 65: "Mưa to",
    66: "Mưa đóng băng nhẹ", 67: "Mưa đóng băng to",
    71: "Tuyết nhẹ", 73: "Tuyết vừa", 75: "Tuyết to", 77: "Hạt tuyết",
    80: "Mưa rào nhẹ", 81: "Mưa rào vừa", 82: "Mưa rào mạnh",
    85: "Mưa tuyết rào nhẹ", 86: "Mưa tuyết rào mạnh",
    95: "Dông nhẹ/vừa", 96: "Dông kèm mưa đá nhẹ", 99: "Dông kèm mưa đá mạnh",
}

try:
    # ===== 5. Gọi API =====
    resp = requests.get(url, timeout=10)
    data = resp.json()
    if resp.status_code != 200:
        print("Lỗi:", data)
        raise SystemExit

    # ===== 6. Thời tiết hiện tại =====
    current = data["current_weather"]
    code = current["weathercode"]
    desc = weather_map.get(code, f"Mã {code}")

    print("=== Thời tiết hiện tại Đà Nẵng ===")
    print(f"Nhiệt độ  : {current['temperature']} °C")
    print(f"Gió       : {current['windspeed']} km/h")
    print(f"Trạng thái: {desc}")

    # ===== 7. Dự báo 5 giờ tới =====
    print("\n=== Dự báo 5 giờ tới (nhiệt độ, lượng mưa, xác suất mưa) ===")
    times  = data["hourly"]["time"][:5]
    temps  = data["hourly"]["temperature_2m"][:5]
    rains  = data["hourly"]["precipitation"][:5]
    probs  = data["hourly"]["precipitation_probability"][:5]
    for t, temp, rain, prob in zip(times, temps, rains, probs):
        print(f"{t}: {temp:.1f} °C | Lượng mưa: {rain:.1f} mm | Khả năng mưa: {prob}%")

    # ===== 8. Trung bình khả năng mưa hôm nay =====
    today = datetime.now().strftime("%Y-%m-%d")
    all_times = data["hourly"]["time"]
    all_probs = data["hourly"]["precipitation_probability"]
    today_probs = [p for t, p in zip(all_times, all_probs) if t.startswith(today)]

    if today_probs:
        avg_prob = sum(today_probs) / len(today_probs)
        print(f"\n=== Khả năng mưa trung bình hôm nay: {avg_prob:.1f}% ===")
    else:
        avg_prob = 0
        print("\nKhông có dữ liệu xác suất mưa cho hôm nay.")

    # ===== 9. Điều khiển LED =====
    if avg_prob > 50:
        GPIO.output(LED_XANH_PIN, GPIO.HIGH)
        GPIO.output(LED_VANG_PIN, GPIO.LOW)
        print("Trời có khả năng mưa >50% → Bật LED XANH")
    else:
        GPIO.output(LED_XANH_PIN, GPIO.LOW)
        GPIO.output(LED_VANG_PIN, GPIO.HIGH)
        print("Khả năng mưa ≤50% → Bật LED VÀNG")

    time.sleep(30)

finally:
    GPIO.cleanup()
    print("Kết thúc chương trình, tắt LED và dọn dẹp GPIO.")