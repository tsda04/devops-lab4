#!/usr/bin/env python3
from flask import Flask, jsonify
import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import time

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация базы данных PostgreSQL из переменных окружения
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'appdb')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'apppassword')

def get_db_connection():
    """Создание соединения с PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        return None

def init_db():
    """Инициализация базы данных"""
    max_retries = 5
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visits (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        ip VARCHAR(50)
                    )
                ''')
                conn.commit()
                conn.close()
                logger.info("База данных инициализирована")
                return True
        except Exception as e:
            logger.warning(f"Попытка {i+1}/{max_retries} - Ошибка инициализации БД: {e}")
            time.sleep(2)
    return False

def log_visit(ip="0.0.0.0"):
    """Логирование посещения"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO visits (ip) VALUES (%s) RETURNING id",
                (ip,)
            )
            conn.commit()
            visit_id = cursor.fetchone()['id']
            conn.close()
            return visit_id
    except Exception as e:
        logger.error(f"Ошибка записи в БД: {e}")
    return None

def get_visit_count():
    """Получение количества посещений"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM visits")
            count = cursor.fetchone()['count']
            conn.close()
            return count
    except Exception as e:
        logger.error(f"Ошибка чтения из БД: {e}")
    return 0

@app.route('/')
def health():
    # Логируем посещение
    visit_id = log_visit()
    
    # Получаем статистику
    visit_count = get_visit_count()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'visits': visit_count,
        'visit_id': visit_id,
        'message': 'Docker Compose с PostgreSQL работает!',
        'db_connected': visit_id is not None
    })

@app.route('/visits')
def visits():
    """Получить все посещения"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10")
            visits_data = cursor.fetchall()
            conn.close()
            
            return jsonify({
                'total_visits': get_visit_count(),
                'recent_visits': visits_data
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch visits'
        }), 500

@app.route('/health')
def health_check():
    """Health check для Docker Compose"""
    db_status = "connected" if get_db_connection() else "disconnected"
    return jsonify({
        'status': 'healthy',
        'service': 'web',
        'database': db_status
    })

@app.route('/db-status')
def db_status():
    """Проверка статуса базы данных"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()['version']
        conn.close()
        return jsonify({
            'status': 'connected',
            'database': 'PostgreSQL',
            'version': version
        })
    return jsonify({'status': 'disconnected'}), 500

if __name__ == '__main__':
    # Инициализируем БД при запуске
    if init_db():
        logger.info("Запуск Flask приложения на порту 8181")
        app.run(host='0.0.0.0', port=8181, debug=False)
    else:
        logger.error("Не удалось инициализировать БД. Приложение не запущено.")
