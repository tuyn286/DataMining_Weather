CREATE DATABASE `weather-db`;

USE `weather-db`;

CREATE TABLE `tbweather` (
    `time` DATETIME primary key,
    `temperature` FLOAT NOT NULL,
    `pressure` float not null,
    `wind_direction` float not null,
    `humidity` float not null,
    `rain` float not null,
    `cloud` float not null,
    `visibility` float not null,
    `wind_speed` float not null
);
CREATE TABLE `daily_weather` (
    `time` DATETIME primary key,
    `temperature` FLOAT NOT NULL,
    `pressure` float not null,
    `wind_direction` float not null,
    `humidity` float not null,
    `rain` float not null,
    `cloud` float not null,
    `visibility` float not null,
    `wind_speed` float not null
);

CREATE TABLE `weekly_weather` (
    `time` DATETIME primary key,
    `temperature` FLOAT NOT NULL,
    `pressure` float not null,
    `wind_direction` float not null,
    `humidity` float not null,
    `rain` float not null,
    `cloud` float not null,
    `visibility` float not null,
    `wind_speed` float not null
);

CREATE TABLE `monthly_weather` (
    `time` DATETIME primary key,
    `temperature` FLOAT NOT NULL,
    `pressure` float not null,
    `wind_direction` float not null,
    `humidity` float not null,
    `rain` float not null,
    `cloud` float not null,
    `visibility` float not null,
    `wind_speed` float not null
);

CREATE TABLE `tbclustering` (
    `date` date primary key,
    `temperature` FLOAT NOT NULL,
    `season_cluster` nvarchar(255) not null,
    `half_year` nvarchar(255) not null
);

CREATE TABLE `tbcentroid` (
    `id` int primary key auto_increment,
    `temperature` FLOAT NOT NULL,
    `season_cluster` nvarchar(255) not null,
    `day_count` int not null
);

CREATE TABLE tbmodels (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `model_name` VARCHAR(255) UNIQUE NOT NULL,
    `model_blob` BLOB NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);