import requests
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/crawl_weather_hourly", methods=["GET"])
def crawl_weather():
    try:
        # Thiết lập headers tùy chỉnh cho request
        headers = requests.utils.default_headers()
        headers.update(
            {
                'User-Agent': 'My Weather Client 1.0',
            }
        )
        # Lấy ngày hiện tại
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Gửi request đến API Open-Meteo
        url = "https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=20.4737&longitude=106.0229&start_date=2021-03-23&end_date={today}&hourly=temperature_2m,relative_humidity_2m,rain,surface_pressure,cloud_cover,visibility,wind_speed_10m,wind_direction_10m"
        response = requests.get(url, headers=headers)
        
        # Trả về dữ liệu JSON nhận được từ API
        return jsonify(response.json())

    except requests.exceptions.RequestException as e:
        # Xử lý lỗi khi request gặp sự cố
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
