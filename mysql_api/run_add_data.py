from flask import Flask
from add_tbtrend import insert_tbtrend 
from add_raw_tbweather import insert_weather_hourly
from add_predict_model import train_model
from add_tbclustering import insert_tbclustering
from add_tbdaily_weekly_monthly import save_weather_data
import schedule 
import time as tm


app = Flask(__name__)
def add_data():
    try:
        insert_weather_hourly()
        print('tbweather success')
    except Exception as e:
        print(f'Error in add_raw_tbweather: {e}')

    try:
        save_weather_data()
        print('tbdaily weekly monthly success')
    except Exception as e:
        print(f'Error in save_weather_data: {e}')

    try:
        insert_tbtrend()
        print('tbtrend success')
    except Exception as e:
        print(f'Error in insert_tbtrend: {e}')

    try:
        insert_tbclustering()
        print('tbclustering success')
    except Exception as e:
        print(f'Error in insert_tbclustering: {e}')

    try:
        train_model()
        print('tbmodel success')
    except Exception as e:
        print(f'Error in train_model: {e}')

    return "Data added successfully!"

    
if __name__ == '__main__':
    app.run(port=5001, debug=True)
    add_data()
    schedule.every().day.at("00:00").do(add_data)
    while True:
        schedule.run_pending()
        tm.sleep(1)