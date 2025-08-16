#!/usr/bin/env python3
"""
Проверка статуса бота
"""

import os
from config import BOT_TOKEN

def check_status():
    """Проверка конфигурации"""
    print("🔍 Проверка статуса бота...")
    
    # Проверка токена
    if BOT_TOKEN:
        print(f"✅ Токен бота: Установлен")
        print(f"   Токен: {BOT_TOKEN[:10]}...")
    else:
        print("❌ Токен бота: Не установлен")
    
    # Проверка переменных окружения
    env_token = os.getenv('BOT_TOKEN')
    if env_token:
        print(f"✅ Переменная окружения BOT_TOKEN: Установлена")
    else:
        print("⚠️ Переменная окружения BOT_TOKEN: Не установлена")
    
    print("🎯 Бот готов к запуску!")

if __name__ == '__main__':
    check_status()
