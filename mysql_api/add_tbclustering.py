import mysql.connector
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'weather-db'
}
def customize_kmean_label(season_cluster, half_year):
    if season_cluster in [0, 1]:  # Kiểm tra season_cluster là 0 hoặc 1
        return 0 if half_year == 'H1' else 1
    return season_cluster  # Giữ nguyên nếu không phải 0 hoặc 1
def insert_tbclustering():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT time, temperature FROM tbweather")
    data = cursor.fetchall()

    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)  
    df_daily = df.resample('D').median()
    # Xây dựng kmeans, chọn temp làm input
    X = df_daily[[ 'temperature']].values
    kmeans = KMeans(n_clusters=4, random_state=42)
    df_daily['season_cluster'] = kmeans.fit_predict(X)
    # Tính half year 
    df_daily['half_year'] = df_daily.index.month.map(lambda x: 'H1' if x <= 6 else 'H2')
    # Tính lại season cluster
    df_daily['season_cluster']=df_daily[['season_cluster', 'half_year']].apply(lambda x: customize_kmean_label(x['season_cluster'], x['half_year']), axis =1)


    # Sắp xếp lại trung bình nhiệt độ tăng dần để gán mùa cho đúng
    cluster_avg_temp = df_daily.groupby('season_cluster')['temperature'].mean()
    sorted_clusters = cluster_avg_temp.sort_values().index.tolist()
    season_map = {sorted_clusters[0]: 'Winter',  
                sorted_clusters[1]: 'Spring',
                sorted_clusters[2]: 'Autumn',
                sorted_clusters[3]: 'Summer'}
    df_daily['season_cluster'] = df_daily['season_cluster'].map(season_map)

    df_daily_reset = df_daily.reset_index()

    tuples = df_daily_reset[['time', 'temperature', 'season_cluster', 'half_year']].values.tolist()
    insert_query = """
                INSERT IGNORE INTO tbclustering (date, temperature, season_cluster, half_year)
                VALUES (%s, %s, %s, %s)
                """
    cursor.executemany(insert_query, tuples)


    # Lấy ra centroid
    centroids = kmeans.cluster_centers_
    centroids_df = pd.DataFrame(centroids, columns=[ 'temperature'])
    # Đếm số ngày theo từng cụm
    cluster_counts = df_daily['season_cluster'].value_counts()
    centroids_df = centroids_df.sort_values(by='temperature')
    centroids_df['season_cluster'] = range(len(centroids))
    # Map giá trị
    season_map = {0: 'Winter', 1: 'Spring', 2: 'Autumn', 3: 'Summer'}
    centroids_df['season_cluster'] = centroids_df['season_cluster'].map(season_map)
    centroids_df['day_count'] = centroids_df['season_cluster'].map(cluster_counts)

    # Xóa data trước khi insert (tại vì mình tính lại giá trị)
    delete_query = """delete from tbcentroid"""
    cursor.execute(delete_query)
    tuples = centroids_df[['temperature', 'season_cluster', 'day_count']].values.tolist()
    insert_query = """
                INSERT IGNORE INTO tbcentroid (temperature, season_cluster, day_count)
                VALUES (%s, %s, %s)
                """
    cursor.executemany(insert_query, tuples)
    connection.commit()
    cursor.close()
    connection.close()
