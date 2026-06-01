# F1 Race Management System - Configuration
import os

class Config:
    SECRET_KEY = os.urandom(24)
    # MySQL connection config — adjust host/port/user/password to your environment
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = 'Qyy-750229'
    DB_NAME = 'f1_race_control'
    DB_CHARSET = 'utf8mb4'
