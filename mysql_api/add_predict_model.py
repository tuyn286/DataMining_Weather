import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import pickle
from sklearn.cluster import KMeans
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'weather-db'
}
def train_model():
    # Kết nối tới cơ sở dữ liệu
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE(time) as date, 
               AVG(temperature) as avg_temp, 
               AVG(pressure) as avg_pressure, 
               AVG(humidity) as avg_humidity 
        FROM tbweather 
        GROUP BY DATE(time)
    """)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Tính toán đặc trưng: trung bình 7 ngày
    df['avg_temp_7d'] = df['avg_temp'].rolling(window=7).mean()
    df['avg_pressure_7d'] = df['avg_pressure'].rolling(window=7).mean()
    df['avg_humidity_7d'] = df['avg_humidity'].rolling(window=7).mean()

    # Xóa các dòng không đủ dữ liệu
    df = df.dropna()

    # Tạo dữ liệu huấn luyện
    X = df[['avg_pressure_7d', 'avg_humidity_7d', 'avg_temp_7d']].values
    y = df['avg_temp'].values

    # Huấn luyện mô hình
    model = LinearRegression()
    model.fit(X, y)

    # Lưu mô hình vào database
    model_blob = pickle.dumps(model)
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tbmodels WHERE model_name = %s", ("weather_prediction",))  # Xóa model cũ nếu có
    cursor.execute("INSERT INTO tbmodels (model_name, model_blob) VALUES (%s, %s)", ("weather_prediction", model_blob))
    connection.commit()

    cursor.close()
    connection.close()
