#!/usr/bin/env python3
"""
Альтернативный запуск только бота для Railway
"""

import os
import sys
from bot import FitnessBot

def main():
    """Запуск только Telegram бота"""
    try:
        print("🚀 Запуск фитнес-бота...")
        print(f"🤖 Токен: {'Установлен' if os.getenv('BOT_TOKEN') else 'Не найден'}")
        
        bot = FitnessBot()
        print("✅ Бот инициализирован")
        print("🤖 Бот запущен...")
        
        bot.run()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
