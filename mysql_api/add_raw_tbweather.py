import mysql.connector
from mysql.connector import Error
import requests
from datetime import datetime

def insert_weather_hourly():
    # Kết nối đến cơ sở dữ liệu
    cnx = mysql.connector.connect(user='root', password='123456', port='3306', host='localhost', database='weather-db')

    try:
        if cnx.is_connected():
            print("Connected to MySQL database")

            # Gửi request đến API crawl_weather
            response = requests.get("http://127.0.0.1:5000/crawl_weather_hourly")
            response_data = response.json()

            # Trích xuất dữ liệu từ JSON trả về
            times = response_data['hourly']['time']
            temperatures = response_data['hourly']['temperature_2m']
            pressures = response_data['hourly']['surface_pressure']
            wind_direction = response_data['hourly']['wind_direction_10m']
            humidity = response_data['hourly']['relative_humidity_2m']
            rain = response_data['hourly']['rain']
            cloud = response_data['hourly']['cloud_cover']
            visibility = response_data['hourly']['visibility']
            wind_speed = response_data['hourly']['wind_speed_10m']

            # Chuẩn bị dữ liệu để chèn vào database
            weather_data = []
            for time, temp, pressure, wd, humi, r, cl, vis, ws in zip(times, temperatures, pressures, wind_direction, humidity, rain,cloud,visibility,wind_speed):
                formatted_time = datetime.strptime(time, "%Y-%m-%dT%H:%M") 
                weather_data.append((formatted_time, temp, pressure, wd, humi, r, cl, vis, ws))

            # Tạo cursor để thực hiện các lệnh SQL
            cursor = cnx.cursor()

            # Thêm dữ liệu vào bảng `tbweather` bỏ qua nếu trùng lặp
            insert_query = """
            INSERT IGNORE INTO tbweather (time, temperature, pressure, wind_direction, humidity, rain, cloud, visibility, wind_speed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, weather_data)

            # Commit dữ liệu và đóng kết nối
            cnx.commit()
            print(f"{cursor.rowcount} rows were inserted into `tbweather`.")

            cursor.close()
        else:
            print("Failed to connect to MySQL database")

    except Error as e:
        print("Error while interacting with MySQL:", e)

    finally:
        if cnx.is_connected():
            cnx.close()

