import sqlite3
import json
from datetime import datetime, date
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                calories_goal INTEGER DEFAULT 1800,
                water_goal INTEGER DEFAULT 2000,
                protein_goal INTEGER DEFAULT 120,
                carbs_goal INTEGER DEFAULT 150,
                fat_goal INTEGER DEFAULT 60,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица приемов пищи
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                meal_type TEXT,
                food_name TEXT,
                calories INTEGER,
                protein REAL,
                carbs REAL,
                fat REAL,
                meal_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица воды
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                drink_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица тренировок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                workout_type TEXT,
                exercises TEXT,
                duration INTEGER,
                workout_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица веса
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                weight REAL,
                weight_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name):
        """Добавление нового пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """Получение данных пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def add_meal(self, user_id, meal_type, food_name, calories, protein, carbs, fat):
        """Добавление приема пищи"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO meals (user_id, meal_type, food_name, calories, protein, carbs, fat, meal_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_type, food_name, calories, protein, carbs, fat, date.today()))
        
        conn.commit()
        conn.close()
    
    def get_daily_meals(self, user_id, meal_date=None):
        """Получение приемов пищи за день"""
        if meal_date is None:
            meal_date = date.today()
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM meals 
            WHERE user_id = ? AND meal_date = ?
            ORDER BY created_at
        ''', (user_id, meal_date))
        
        meals = cursor.fetchall()
        conn.close()
        return meals
    
    def add_water(self, user_id, amount):
        """Добавление выпитой воды"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO water (user_id, amount, drink_date)
            VALUES (?, ?, ?)
        ''', (user_id, amount, date.today()))
        
        conn.commit()
        conn.close()
    
    def get_daily_water(self, user_id, drink_date=None):
        """Получение выпитой воды за день"""
        if drink_date is None:
            drink_date = date.today()
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(amount) FROM water 
            WHERE user_id = ? AND drink_date = ?
        ''', (user_id, drink_date))
        
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] else 0
    
    def add_workout(self, user_id, workout_type, exercises, duration):
        """Добавление тренировки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        exercises_json = json.dumps(exercises)
        cursor.execute('''
            INSERT INTO workouts (user_id, workout_type, exercises, duration, workout_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, workout_type, exercises_json, duration, date.today()))
        
        conn.commit()
        conn.close()
    
    def add_weight(self, user_id, weight):
        """Добавление веса"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weight (user_id, weight, weight_date)
            VALUES (?, ?, ?)
        ''', (user_id, weight, date.today()))
        
        conn.commit()
        conn.close()
    
    def get_weight_history(self, user_id, days=7):
        """Получение истории веса"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT weight, weight_date FROM weight 
            WHERE user_id = ? 
            ORDER BY weight_date DESC 
            LIMIT ?
        ''', (user_id, days))
        
        history = cursor.fetchall()
        conn.close()
        return history
