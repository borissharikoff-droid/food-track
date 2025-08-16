import threading
import os
from bot import FitnessBot
from web_server import app

def run_bot():
    """Запуск Telegram бота"""
    bot = FitnessBot()
    bot.run()

def run_web():
    """Запуск веб-сервера"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем веб-сервер в основном потоке
    run_web()
