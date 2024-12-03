import mysql.connector
import pandas as pd

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'weather-db'
}

def insert_tbtrend():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT time, temperature FROM tbweather")
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    # Resample theo ngày
    df_daily = df.resample('D').median()
    window_size = 24
    half_window = window_size // 2

    df_daily['trend'] = (
        df_daily['temperature']
        .rolling(window=window_size, center=True)
        .mean()
    )
    df_daily['seasonal'] = df_daily['temperature'] - df_daily['trend']
    df_daily = df_daily.dropna(subset=['trend'])
    df_daily_reset = df_daily.reset_index()

    # Xóa data trước khi insert (tại vì mình tính lại giá trị)
    delete_query = """delete from tbtrend"""
    cursor.execute(delete_query)
    tuples = df_daily_reset[['time', 'temperature', 'trend', 'seasonal']].values.tolist()
    insert_query = """
                INSERT IGNORE INTO tbtrend (date, temperature, trend, seasonal)
                VALUES (%s, %s, %s, %s)
                """
    cursor.executemany(insert_query, tuples)

    connection.commit()
    cursor.close()
    connection.close()
