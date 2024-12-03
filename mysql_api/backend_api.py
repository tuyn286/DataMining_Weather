from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import numpy as np
import pickle

app = Flask(__name__, template_folder='../front_end/template')

# MySQL Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'weather-db'
}

def get_trend():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT date, trend, seasonal FROM tbtrend")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data, columns=['date', 'trend', 'seasonal'])
    return df

def get_spider():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT season_cluster, day_count FROM tbcentroid")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data, columns=['season_cluster', 'day_count'])
    return df

def get_daily_weather():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT time, temperature, pressure, humidity FROM daily_weather")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data, columns=['time', 'temperature', 'pressure', 'humidity'])
    return df

def get_weekly_weather():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT time, temperature, pressure, humidity FROM weekly_weather")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data, columns=['time', 'temperature', 'pressure', 'humidity'])
    return df

def get_monthly_weather():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT time, temperature, pressure, humidity FROM monthly_weather")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data, columns=['time', 'temperature', 'pressure', 'humidity'])
    return df

def get_weather():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbweather")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data, columns=['time','temperature', 'pressure', 'wind_direction', 'humidity', 'cloud', 'visibility', 'wind_speed'])
    return df

def cal_percent(temp):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbcentroid")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data)
    # Cho temperature là tham số đầu vào của hàm
    distances = np.abs(temp - df['temperature'].values)
    # Tìm ra khoảng cách nhỏ nhất
    nearest_idx = np.argmin(distances)
    # Tìm ra chỉ số của khoảng cách nhỏ nhất
    nearest_temperature = df['temperature'].iloc[nearest_idx]
    max_distance = np.max(distances)

    # Tính độ chính xác dưới dạng tỷ lệ phần trăm
    accuracy_percentage = (1 - (distances / max_distance)) * 100

    season = df[df['temperature']==df['temperature'][nearest_idx]]['season_cluster'].values
    percent = accuracy_percentage[nearest_idx]

    return season, percent

def get_season():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT date, temperature, season_cluster FROM tbclustering")
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    df = pd.DataFrame(data, columns=['date', 'temperature', 'season_cluster'])
    return df

def predict():
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

        # Lấy model từ database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT model_blob FROM tbmodels WHERE model_name = %s", ("weather_prediction",))
    model_blob = cursor.fetchone()[0]
    model = pickle.loads(model_blob)
    cursor.close()
    connection.close()

        # Dự đoán cho ngày mai
    last_row = df.iloc[-1]
    next_day_features = np.array([[last_row['avg_pressure_7d'], last_row['avg_humidity_7d'], last_row['avg_temp_7d']]])
    predicted_temperature = model.predict(next_day_features)[0]

    return predicted_temperature

@app.route('/')
def index():
    temperature = predict()
    return render_template('index.html', temperature=temperature)

@app.route('/line')
def line_chart():
    daily = get_daily_weather()
    weekly = get_weekly_weather()
    monthly = get_monthly_weather()
    # Vẽ biểu đồ ngày
    daily_fig = px.line(
        daily,
        x='time', 
        y='temperature', 
        title='Daily Temperature',  
        labels={'Date': 'Date', 'Temperature': 'Temperature (°C)'} 
    )
    daily_html = pio.to_html(daily_fig, full_html=False)
    # Vẽ biểu đồ tuần
    weekyly_fig = px.line(
        weekly,
        x='time',  
        y='temperature',  
        title='Weekly Temperature',  
        labels={'Date': 'Date', 'Temperature': 'Temperature (°C)'}  
    )
    weekly_html = pio.to_html(weekyly_fig, full_html=False)
    # Vẽ biểu đồ tháng
    monthly_fig = px.line(
        monthly,
        x='time',  
        y='temperature',  
        title='Monthly Temperature',  
        labels={'Date': 'Date', 'Temperature': 'Temperature (°C)'}  
    )
    monthly_html = pio.to_html(monthly_fig, full_html=False)

    return render_template('line.html', weekly_html=weekly_html, daily_html=daily_html, monthly_html=monthly_html)

@app.route('/line-pressure')
def line_pressure_chart():
    daily = get_daily_weather()
    weekly = get_weekly_weather()
    monthly = get_monthly_weather()
    # Vẽ biểu đồ ngày
    daily_fig = px.line(
        daily,
        x='time', 
        y='pressure', 
        title='Daily Pressure',  
        labels={'Date': 'Date', 'Pressure': 'Pressure (Pa)'} 
    )
    daily_html = pio.to_html(daily_fig, full_html=False)
    # Vẽ biểu đồ tuần
    weekyly_fig = px.line(
        weekly,
        x='time',  
        y='pressure',  
        title='Weekly Pressure',  
        labels={'Date': 'Date', 'Pressure': 'Pressure (Pa)'}  
    )
    weekly_html = pio.to_html(weekyly_fig, full_html=False)
    # Vẽ biểu đồ tháng
    monthly_fig = px.line(
        monthly,
        x='time',  
        y='pressure',  
        title='Monthly Pressure',  
        labels={'Date': 'Date', 'Pressure': 'Pressure (Pa)'}  
    )
    monthly_html = pio.to_html(monthly_fig, full_html=False)

    return render_template('line-pressure.html', weekly_html=weekly_html, daily_html=daily_html, monthly_html=monthly_html)

@app.route('/line-humidity')
def line_humidity_chart():
    daily = get_daily_weather()
    weekly = get_weekly_weather()
    monthly = get_monthly_weather()
    # Vẽ biểu đồ ngày
    daily_fig = px.line(
        daily,
        x='time', 
        y='humidity', 
        title='Daily humidity',  
        labels={'Date': 'Date', 'humidity': 'humidity (%)'} 
    )
    daily_html = pio.to_html(daily_fig, full_html=False)
    # Vẽ biểu đồ tuần
    weekyly_fig = px.line(
        weekly,
        x='time',  
        y='humidity',  
        title='Weekly humidity',  
        labels={'Date': 'Date', 'humidity': 'humidity (%)'}  
    )
    weekly_html = pio.to_html(weekyly_fig, full_html=False)
    # Vẽ biểu đồ tháng
    monthly_fig = px.line(
        monthly,
        x='time',  
        y='humidity',  
        title='Monthly humidity',  
        labels={'Date': 'Date', 'humidity': 'humidity (%)'}  
    )
    monthly_html = pio.to_html(monthly_fig, full_html=False)

    return render_template('line-humidity.html', weekly_html=weekly_html, daily_html=daily_html, monthly_html=monthly_html)


@app.route('/trend')
def trend_chart():
    df = get_trend()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['trend'], mode='lines+markers', name='trend'))
    fig.update_layout(
        title="Biểu đồ xu hướng",
        xaxis_title="Thời gian",
        yaxis_title="Nhiệt độ",
        template="plotly_white"
    )
    plot_html = pio.to_html(fig, full_html=False)

    sea_fig = go.Figure()
    sea_fig.add_trace(go.Scatter(x=df['date'], y=df['seasonal'], mode='lines+markers', name='seasonal'))
    sea_fig.update_layout(
        title="Biểu đồ seasonal",
        xaxis_title="Thời gian",
        yaxis_title="Độ lệch",
        template="plotly_white"
    )
    sea_html = pio.to_html(sea_fig, full_html=False)

    return render_template('trend.html', plot_html=plot_html, sea_html=sea_html)

@app.route('/correlation')
def correlation_chart():
    df = get_weather()

    correlation_matrix = df[['temperature', 'pressure', 'wind_direction', 'humidity', 'cloud', 'visibility', 'wind_speed']].corr()
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,  
        x=correlation_matrix.columns,  
        y=correlation_matrix.index, 
        colorscale='RdBu',  
        zmin=-1, zmax=1 
    ))

    # Tùy chỉnh layout
    fig.update_layout(
        title='Correlation Matrix of Weather Data',
        xaxis_title="Features",
        yaxis_title="Features"
    )
    plot_html = pio.to_html(fig, full_html=False)

    return render_template('correlation.html', plot_html=plot_html)

@app.route('/spider')
def spider_chart():
    df = get_spider()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=df['day_count'] ,
        theta=df['season_cluster'] ,
        fill='toself',  # Tô màu vùng bên trong
        name='Performance'
    ))

    # Cài đặt layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,500])  # Cài đặt phạm vi trục
        ),
        title="Spider Chart Example"
    )

    # Convert biểu đồ sang HTML
    plot_html = pio.to_html(fig, full_html=False)

    return render_template('spider.html', plot_html=plot_html)

@app.route('/input-temperature')
def input_temperature():
    return render_template('form_temperature.html')

@app.route('/percent', methods=['POST'])
def process():
    input = request.form.get('temp')
    temperature = float(input)
    season, percent = cal_percent(temperature)
    df = get_season()
    fig = px.scatter(
        df,
        x='date',  # Trục X: Ngày
        y='temperature',  # Trục Y: Nhiệt độ
        color='season_cluster',  # Màu sắc theo mùa
        title='Temperature Over Time by Season',  # Tiêu đề biểu đồ
        labels={'Temperature': 'Temperature (°C)', 'Date': 'Date'},  # Đặt nhãn cho trục
    )

    plot_html = pio.to_html(fig, full_html=False)
    return render_template('season.html', plot_html=plot_html, season=season, percent=percent)

if __name__ == '__main__':
    app.run(port=5002, debug=True)