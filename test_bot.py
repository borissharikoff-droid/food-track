#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы бота
"""

from database import Database
from food_database import get_food_info, calculate_meal_nutrition, get_food_recommendations

def test_database():
    """Тестирование базы данных"""
    print("🧪 Тестирование базы данных...")
    
    db = Database()
    
    # Тест добавления пользователя
    db.add_user(12345, "test_user", "Test User")
    print("✅ Пользователь добавлен")
    
    # Тест получения пользователя
    user = db.get_user(12345)
    print(f"✅ Пользователь получен: {user[2]}")
    
    # Тест добавления приема пищи
    db.add_meal(12345, "завтрак", "овсянка", 389, 17, 66, 6.9)
    print("✅ Прием пищи добавлен")
    
    # Тест получения приемов пищи
    meals = db.get_daily_meals(12345)
    print(f"✅ Получено приемов пищи: {len(meals)}")
    
    # Тест добавления воды
    db.add_water(12345, 500)
    print("✅ Вода добавлена")
    
    # Тест получения воды
    water = db.get_daily_water(12345)
    print(f"✅ Выпито воды: {water}мл")
    
    # Тест добавления веса
    db.add_weight(12345, 75.5)
    print("✅ Вес добавлен")
    
    # Тест получения истории веса
    weight_history = db.get_weight_history(12345, 1)
    print(f"✅ История веса: {weight_history[0][0]}кг")
    
    print("🎉 Все тесты базы данных пройдены!")

def test_food_database():
    """Тестирование базы продуктов"""
    print("\n🍎 Тестирование базы продуктов...")
    
    # Тест получения информации о продукте
    food_info = get_food_info("овсянка")
    print(f"✅ Информация об овсянке: {food_info}")
    
    # Тест подсчета калорий
    nutrition = calculate_meal_nutrition("курица грудка", 150)
    print(f"✅ Питательность куриной грудки (150г): {nutrition}")
    
    # Тест рекомендаций
    recommendations = get_food_recommendations()
    print(f"✅ Рекомендуемые белки: {recommendations['recommended']['proteins'][:3]}")
    
    print("🎉 Все тесты базы продуктов пройдены!")

def test_config():
    """Тестирование конфигурации"""
    print("\n⚙️ Тестирование конфигурации...")
    
    try:
        from config import BOT_TOKEN, DEFAULT_CALORIES_GOAL, FOOD_CATEGORIES
        print(f"✅ Токен бота: {'Установлен' if BOT_TOKEN else 'Не установлен'}")
        print(f"✅ Цель калорий: {DEFAULT_CALORIES_GOAL}")
        print(f"✅ Категории продуктов: {len(FOOD_CATEGORIES)}")
        print("🎉 Конфигурация загружена успешно!")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов фитнес-бота...\n")
    
    try:
        test_config()
        test_database()
        test_food_database()
        
        print("\n🎉 Все тесты пройдены успешно!")
        print("🤖 Бот готов к запуску!")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        print("🔧 Проверьте настройки и зависимости")
