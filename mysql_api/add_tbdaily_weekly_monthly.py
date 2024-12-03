import mysql.connector
from mysql.connector import Error
import pandas as pd


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'weather-db'
}
def save_weather_data():
    # Kết nối đến cơ sở dữ liệu
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    try:
        if connection.is_connected():
            print("Connected to MySQL database")

            # Thực hiện truy vấn để lấy dữ liệu
            cursor.execute("SELECT time, temperature, pressure, wind_direction, humidity, rain, cloud, visibility, wind_speed FROM tbweather")
            data = cursor.fetchall()

            cursor.close()
            connection.close()

            # Chuyển đổi dữ liệu thành DataFrame
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'])  # Chuyển đổi cột 'time' thành định dạng datetime
            df.set_index('time', inplace=True)  # Đặt cột 'time' làm chỉ số

            # Tính toán gộp theo ngày
            daily_data = df.resample('D').mean().reset_index()
            

            # Tính toán gộp theo tuần
            weekly_data = df.resample('W').mean().reset_index()
            

            # Tính toán gộp theo tháng
            monthly_data = df.resample('ME').mean().reset_index()
            

            # Kết nối lại để lưu dữ liệu vào các bảng
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Chuẩn bị dữ liệu để chèn vào database
            daily_data['time'] = daily_data['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            weekly_data['time'] = weekly_data['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            monthly_data['time'] = monthly_data['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Chuẩn bị dữ liệu để chèn vào database
            daily_tuples = daily_data[['time', 'temperature', 'pressure', 'wind_direction', 'humidity', 'rain', 'cloud', 'visibility', 'wind_speed']].values.tolist()
            weekly_tuples = weekly_data[['time', 'temperature', 'pressure', 'wind_direction', 'humidity', 'rain', 'cloud', 'visibility', 'wind_speed']].values.tolist()
            monthly_tuples = monthly_data[['time', 'temperature', 'pressure', 'wind_direction', 'humidity', 'rain', 'cloud', 'visibility', 'wind_speed']].values.tolist()
            # Tạo cursor để thực hiện các lệnh SQL
            cursor = connection.cursor()

            # Câu lệnh SQL để chèn dữ liệu
            insert_daily_query = """
            INSERT IGNORE INTO daily_weather (time, temperature, pressure, wind_direction, humidity, rain, cloud, visibility, wind_speed) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Chèn toàn bộ các record từ DataFrame vào bảng daily_weather
            cursor.executemany(insert_daily_query, daily_tuples)

            # Câu lệnh SQL để chèn dữ liệu vào bảng weekly_weather
            insert_weekly_query = """
            INSERT IGNORE INTO weekly_weather (time, temperature, pressure, wind_direction, humidity, rain, cloud, visibility, wind_speed) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Chèn toàn bộ các record từ DataFrame vào bảng weekly_weather
            cursor.executemany(insert_weekly_query, weekly_tuples)

            # Câu lệnh SQL để chèn dữ liệu vào bảng monthly_weather
            insert_monthly_query = """
            INSERT IGNORE INTO monthly_weather (time, temperature, pressure, wind_direction, humidity, rain, cloud, visibility, wind_speed) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Chèn toàn bộ các record từ DataFrame vào bảng monthly_weather
            cursor.executemany(insert_monthly_query, monthly_tuples)

            # Commit các thay đổi và đóng kết nối
            connection.commit()
            cursor.close()
            connection.close()
        else:
            print("Failed to connect to MySQL database")

    except Error as e:
        print("Error while interacting with MySQL:", e)

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")
