import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN', '8361266417:AAEfwm_4kJHnLopUyH_sA3nArNcb42CcRpQ')

# Database
DATABASE_PATH = 'fitness_tracker.db'

# User settings
DEFAULT_CALORIES_GOAL = 1800  # для похудения
DEFAULT_WATER_GOAL = 2000  # мл в день
DEFAULT_PROTEIN_GOAL = 120  # грамм в день
DEFAULT_CARBS_GOAL = 150  # грамм в день
DEFAULT_FAT_GOAL = 60  # грамм в день

# Food categories
FOOD_CATEGORIES = {
    'proteins': ['курица', 'индейка', 'рыба', 'яйца', 'творог', 'греческий йогурт'],
    'carbs': ['гречка', 'овсянка', 'рис', 'картофель', 'хлеб'],
    'fats': ['орехи', 'авокадо', 'оливковое масло', 'семечки'],
    'vegetables': ['брокколи', 'шпинат', 'морковь', 'огурцы', 'помидоры'],
    'fruits': ['яблоки', 'бананы', 'апельсины', 'ягоды'],
    'avoid': ['шоколад', 'чипсы', 'сладости', 'газировка', 'фастфуд']
}

# Exercise recommendations
EXERCISES = {
    'cardio': ['бег', 'велотренажер', 'эллипс', 'ходьба'],
    'strength': ['приседания', 'жим лежа', 'становая тяга', 'подтягивания'],
    'core': ['планка', 'скручивания', 'боковая планка']
}
