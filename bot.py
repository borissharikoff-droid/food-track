import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from datetime import datetime, date
import json

from config import BOT_TOKEN, FOOD_CATEGORIES, EXERCISES
from database import Database
from food_database import get_food_info, calculate_meal_nutrition, get_food_recommendations, get_meal_suggestions

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

class FitnessBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.main_menu))
        
        # Питание
        self.application.add_handler(CommandHandler("food", self.food_menu))
        self.application.add_handler(CommandHandler("add_meal", self.add_meal_command))
        self.application.add_handler(CommandHandler("daily_food", self.daily_food_command))
        
        # Вода
        self.application.add_handler(CommandHandler("water", self.water_menu))
        self.application.add_handler(CommandHandler("add_water", self.add_water_command))
        
        # Тренировки
        self.application.add_handler(CommandHandler("workout", self.workout_menu))
        self.application.add_handler(CommandHandler("add_workout", self.add_workout_command))
        
        # Прогресс
        self.application.add_handler(CommandHandler("weight", self.weight_menu))
        self.application.add_handler(CommandHandler("add_weight", self.add_weight_command))
        self.application.add_handler(CommandHandler("progress", self.progress_command))
        
        # Рекомендации
        self.application.add_handler(CommandHandler("tips", self.tips_command))
        self.application.add_handler(CommandHandler("vitamins", self.vitamins_command))
        
        # Обработчики кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name)
        
        welcome_text = f"""
🎉 Привет, {user.first_name}! 

Я твой персональный фитнес-ассистент для похудения! 

Что я умею:
✅ Вести дневник питания и считать калории
✅ Напоминать пить воду
✅ Планировать тренировки
✅ Отслеживать прогресс
✅ Давать рекомендации по питанию и витаминам

Нажми /menu чтобы открыть главное меню!
        """
        
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📋 Доступные команды:

🍽 Питание:
/food - меню питания
/add_meal - добавить прием пищи
/daily_food - дневник питания за сегодня

💧 Вода:
/water - меню воды
/add_water - добавить выпитую воду

🏋️ Тренировки:
/workout - меню тренировок
/add_workout - добавить тренировку

📊 Прогресс:
/weight - меню веса
/add_weight - добавить вес
/progress - общий прогресс

💡 Рекомендации:
/tips - советы по питанию
/vitamins - рекомендации по витаминам

/menu - главное меню
        """
        await update.message.reply_text(help_text)
    
    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главное меню"""
        keyboard = [
            [InlineKeyboardButton("🍽 Питание", callback_data="food_menu")],
            [InlineKeyboardButton("💧 Вода", callback_data="water_menu")],
            [InlineKeyboardButton("🏋️ Тренировки", callback_data="workout_menu")],
            [InlineKeyboardButton("📊 Прогресс", callback_data="progress_menu")],
            [InlineKeyboardButton("💡 Советы", callback_data="tips_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 Главное меню\nВыберите раздел:",
            reply_markup=reply_markup
        )
    
    async def food_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню питания"""
        keyboard = [
            [InlineKeyboardButton("➕ Добавить прием пищи", callback_data="add_meal")],
            [InlineKeyboardButton("📋 Дневник питания", callback_data="daily_food")],
            [InlineKeyboardButton("💡 Рекомендации", callback_data="food_tips")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🍽 Меню питания\nЧто хотите сделать?",
            reply_markup=reply_markup
        )
    
    async def add_meal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление приема пищи"""
        await update.message.reply_text(
            "🍽 Добавление приема пищи\n\n"
            "Напишите в формате:\n"
            "тип_приема_пищи продукт граммы\n\n"
            "Например:\n"
            "завтрак овсянка 100\n"
            "обед курица грудка 150\n"
            "ужин творог 200\n\n"
            "Типы приемов пищи: завтрак, обед, ужин, перекус"
        )
    
    async def daily_food_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать дневник питания за сегодня"""
        user_id = update.effective_user.id
        meals = db.get_daily_meals(user_id)
        
        if not meals:
            await update.message.reply_text("📋 Сегодня еще нет записей о питании")
            return
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        report = "📋 Дневник питания за сегодня:\n\n"
        
        for meal in meals:
            meal_type, food_name, calories, protein, carbs, fat = meal[2], meal[3], meal[4], meal[5], meal[6], meal[7]
            report += f"🍽 {meal_type.title()}: {food_name}\n"
            report += f"   Калории: {calories}, Б: {protein}г, Ж: {fat}г, У: {carbs}г\n\n"
            
            total_calories += calories
            total_protein += protein
            total_carbs += carbs
            total_fat += fat
        
        report += f"📊 Итого за день:\n"
        report += f"Калории: {total_calories}\n"
        report += f"Белки: {total_protein:.1f}г\n"
        report += f"Жиры: {total_fat:.1f}г\n"
        report += f"Углеводы: {total_carbs:.1f}г"
        
        await update.message.reply_text(report)
    
    async def water_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню воды"""
        user_id = update.effective_user.id
        daily_water = db.get_daily_water(user_id)
        user = db.get_user(user_id)
        water_goal = user[5] if user else 2000
        
        keyboard = [
            [InlineKeyboardButton("💧 +200мл", callback_data="water_200")],
            [InlineKeyboardButton("💧 +300мл", callback_data="water_300")],
            [InlineKeyboardButton("💧 +500мл", callback_data="water_500")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        progress = (daily_water / water_goal) * 100
        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        
        text = f"💧 Трекер воды\n\n"
        text += f"Выпито сегодня: {daily_water}мл / {water_goal}мл\n"
        text += f"Прогресс: {progress_bar} {progress:.1f}%\n\n"
        text += f"Выберите количество воды:"
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def workout_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню тренировок"""
        keyboard = [
            [InlineKeyboardButton("➕ Добавить тренировку", callback_data="add_workout")],
            [InlineKeyboardButton("💪 Кардио", callback_data="workout_cardio")],
            [InlineKeyboardButton("🏋️ Силовые", callback_data="workout_strength")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🏋️ Меню тренировок\nВыберите тип тренировки:",
            reply_markup=reply_markup
        )
    
    async def weight_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню веса"""
        keyboard = [
            [InlineKeyboardButton("⚖️ Добавить вес", callback_data="add_weight")],
            [InlineKeyboardButton("📈 История веса", callback_data="weight_history")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚖️ Меню веса\nВыберите действие:",
            reply_markup=reply_markup
        )
    
    async def tips_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Советы по питанию"""
        recommendations = get_food_recommendations()
        meal_suggestions = get_meal_suggestions()
        
        text = "💡 Советы по питанию для похудения:\n\n"
        
        text += "✅ Рекомендуемые продукты:\n"
        text += "🥩 Белки: " + ", ".join(recommendations['recommended']['proteins'][:3]) + "\n"
        text += "🌾 Углеводы: " + ", ".join(recommendations['recommended']['carbs']) + "\n"
        text += "🥬 Овощи: " + ", ".join(recommendations['recommended']['vegetables'][:3]) + "\n"
        text += "🍎 Фрукты: " + ", ".join(recommendations['recommended']['fruits'][:3]) + "\n\n"
        
        text += "❌ Избегайте:\n"
        text += ", ".join(recommendations['avoid']) + "\n\n"
        
        text += "🍽 Примеры приемов пищи:\n"
        text += "🌅 Завтрак: " + meal_suggestions['breakfast'][0] + "\n"
        text += "🌞 Обед: " + meal_suggestions['lunch'][0] + "\n"
        text += "🌙 Ужин: " + meal_suggestions['dinner'][0] + "\n"
        text += "🍎 Перекус: " + meal_suggestions['snacks'][0]
        
        await update.message.reply_text(text)
    
    async def vitamins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Рекомендации по витаминам"""
        text = "💊 Рекомендации по витаминам для похудения:\n\n"
        
        text += "🔬 Основные витамины:\n"
        text += "• Витамин D - для обмена веществ\n"
        text += "• Витамин B12 - для энергии\n"
        text += "• Омега-3 - для жиросжигания\n"
        text += "• Магний - для мышц\n\n"
        
        text += "💡 Рекомендуемые добавки:\n"
        text += "• Рыбий жир (Омега-3)\n"
        text += "• Витамин D3 (2000-4000 МЕ)\n"
        text += "• Магний (200-400мг)\n"
        text += "• Витамин B-комплекс\n\n"
        
        text += "⚠️ Важно: перед приемом витаминов проконсультируйтесь с врачом!"
        
        await update.message.reply_text(text)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text.lower()
        user_id = update.effective_user.id
        
        # Обработка добавления приема пищи
        if any(word in text for word in ['завтрак', 'обед', 'ужин', 'перекус']):
            await self.process_meal_input(update, text)
        # Обработка добавления воды
        elif 'вода' in text or 'мл' in text:
            await self.process_water_input(update, text)
        # Обработка добавления веса
        elif 'вес' in text and any(char.isdigit() for char in text):
            await self.process_weight_input(update, text)
        else:
            await update.message.reply_text(
                "Не понимаю команду. Используйте /help для списка команд или /menu для главного меню."
            )
    
    async def process_meal_input(self, update: Update, text: str):
        """Обработка ввода приема пищи"""
        try:
            parts = text.split()
            if len(parts) >= 3:
                meal_type = parts[0]
                food_name = parts[1]
                grams = int(parts[2])
                
                nutrition = calculate_meal_nutrition(food_name, grams)
                if nutrition:
                    user_id = update.effective_user.id
                    db.add_meal(user_id, meal_type, food_name, 
                               nutrition['calories'], nutrition['protein'], 
                               nutrition['carbs'], nutrition['fat'])
                    
                    await update.message.reply_text(
                        f"✅ Добавлен {meal_type}: {food_name} ({grams}г)\n"
                        f"Калории: {nutrition['calories']}, "
                        f"Б: {nutrition['protein']}г, "
                        f"Ж: {nutrition['fat']}г, "
                        f"У: {nutrition['carbs']}г"
                    )
                else:
                    await update.message.reply_text(
                        f"❌ Продукт '{food_name}' не найден в базе данных.\n"
                        f"Попробуйте другой продукт или добавьте его вручную."
                    )
            else:
                await update.message.reply_text(
                    "❌ Неверный формат. Используйте: тип_приема_пищи продукт граммы"
                )
        except ValueError:
            await update.message.reply_text("❌ Неверный формат. Укажите количество в граммах.")
    
    async def process_water_input(self, update: Update, text: str):
        """Обработка ввода воды"""
        try:
            # Извлечение числа из текста
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                amount = int(numbers[0])
                user_id = update.effective_user.id
                db.add_water(user_id, amount)
                
                daily_water = db.get_daily_water(user_id)
                await update.message.reply_text(
                    f"✅ Добавлено {amount}мл воды\n"
                    f"Всего за день: {daily_water}мл"
                )
            else:
                await update.message.reply_text("❌ Укажите количество воды в миллилитрах.")
        except ValueError:
            await update.message.reply_text("❌ Неверный формат. Укажите количество в миллилитрах.")
    
    async def process_weight_input(self, update: Update, text: str):
        """Обработка ввода веса"""
        try:
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            if numbers:
                weight = float(numbers[0])
                user_id = update.effective_user.id
                db.add_weight(user_id, weight)
                
                await update.message.reply_text(f"✅ Вес {weight}кг добавлен!")
            else:
                await update.message.reply_text("❌ Укажите вес в килограммах.")
        except ValueError:
            await update.message.reply_text("❌ Неверный формат. Укажите вес в килограммах.")
    
    async def add_water_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление выпитой воды"""
        await update.message.reply_text(
            "💧 Добавление воды\n\n"
            "Напишите количество выпитой воды в миллилитрах\n"
            "Например: 300"
        )
    
    async def add_workout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление тренировки"""
        await update.message.reply_text(
            "🏋️ Добавление тренировки\n\n"
            "Напишите в формате:\n"
            "тип_тренировки упражнения минуты\n\n"
            "Например:\n"
            "кардио бег 30\n"
            "силовые приседания жим_лежа 45\n\n"
            "Типы: кардио, силовые, растяжка"
        )
    
    async def add_weight_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление веса"""
        await update.message.reply_text(
            "⚖️ Добавление веса\n\n"
            "Напишите ваш вес в килограммах\n"
            "Например: 75.5"
        )
    
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Общий прогресс"""
        user_id = update.effective_user.id
        
        # Получаем данные за сегодня
        meals = db.get_daily_meals(user_id)
        daily_water = db.get_daily_water(user_id)
        weight_history = db.get_weight_history(user_id, 1)
        
        text = "📊 Ваш прогресс за сегодня:\n\n"
        
        # Калории
        total_calories = sum(meal[4] for meal in meals) if meals else 0
        text += f"🍽 Калории: {total_calories}\n"
        
        # Вода
        text += f"💧 Вода: {daily_water}мл\n"
        
        # Вес
        if weight_history:
            current_weight = weight_history[0][0]
            text += f"⚖️ Текущий вес: {current_weight}кг\n"
        
        text += "\n💡 Используйте /menu для полного управления"
        
        await update.message.reply_text(text)
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "main_menu":
            await self.main_menu(update, context)
        elif query.data == "food_menu":
            await self.food_menu(update, context)
        elif query.data == "water_menu":
            await self.water_menu(update, context)
        elif query.data == "workout_menu":
            await self.workout_menu(update, context)
        elif query.data == "progress_menu":
            await self.weight_menu(update, context)
        elif query.data == "tips_menu":
            await self.tips_command(update, context)
        elif query.data.startswith("water_"):
            amount = int(query.data.split("_")[1])
            user_id = update.effective_user.id
            db.add_water(user_id, amount)
            await self.water_menu(update, context)
        elif query.data == "daily_food":
            await self.daily_food_command(update, context)
        elif query.data == "food_tips":
            await self.tips_command(update, context)
        elif query.data == "add_meal":
            await self.add_meal_command(update, context)
        elif query.data == "add_workout":
            await update.callback_query.message.reply_text(
                "🏋️ Добавление тренировки\n\n"
                "Напишите в формате:\n"
                "тип_тренировки упражнения минуты\n\n"
                "Например:\n"
                "кардио бег 30\n"
                "силовые приседания жим_лежа 45\n\n"
                "Типы: кардио, силовые, растяжка"
            )
        elif query.data == "add_weight":
            await update.callback_query.message.reply_text(
                "⚖️ Добавление веса\n\n"
                "Напишите ваш вес в килограммах\n"
                "Например: 75.5"
            )
        elif query.data == "weight_history":
            user_id = update.effective_user.id
            history = db.get_weight_history(user_id, 7)
            
            if history:
                text = "📈 История веса за последние 7 дней:\n\n"
                for weight, weight_date in history:
                    text += f"{weight_date}: {weight}кг\n"
                await update.callback_query.message.reply_text(text)
            else:
                await update.callback_query.message.reply_text("📈 История веса пуста")
    
    def run(self):
        """Запуск бота"""
        print("🤖 Бот запущен...")
        self.application.run_polling()

if __name__ == '__main__':
    bot = FitnessBot()
    bot.run()
