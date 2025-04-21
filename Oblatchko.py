import logging
import random
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import datetime
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
API_TOKEN = '8192410051:AAEz3lkLHgSGe0fEP5D-3JfT_wTQleQtZb8'
WEATHER_API_KEY = '1671cc601632c69396322d9c9849c65d'

# Инициализация бота с новым синтаксисом
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Состояния для FSM
class GameStates(StatesGroup):
    playing = State()



# Хранилище данных
user_data = {}

# Эмодзи и тексты
WEATHER_EMOJI = [
    "❄️ Ваш аккаунт покрылся инеем! Согрей его горячим чаем!",
    "🧊 Ледяная буря накрыла аккаунт! Спасайся мемами!",
    "🌨 Аккаунт в снежном плену! Растопи лед смехом!",
    "⛄️ Снеговики захватили аккаунт! Вызволяй срочно!",
    "🌬 Ледяной ветер с Севера! Включи обогреватель!"
]

THAW_PHRASES = [
    "🔥 Вы спасли аккаунт котиками! Температура +{}°C!",
    "☀️ Солнечные лучи прогрели страницу! +{}°C!",
    "🐧 Пингвины-спасатели прибыли! +{}°C!",
    "🎮 Геймерский чих растопил лед! +{}°C!",
    "💻 Прогресс бар загрузки согрел! +{}°C!"
]

FACT_EMOJI = ["🌪", "🌡", "🌀", "❄️", "🔥", "💧", "🌤", "⛈"]
WEATHER_FACTS = [
    "Самая высокая температура зафиксирована в Долине Смерти: +56.7°C!",
    "Самая крупная градина весила 1 кг и убила 92 человека в Бангладеш в 1986",
    "Молния может нагревать воздух до 30,000°C — в 5 раз горячее поверхности Солнца",
    "В Антарктиде есть места, где не было дождя 2 миллиона лет",
    "Каждую секунду на Земле происходит 100 ударов молний"
]


# Клавиатуры
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="🌤 Текущая погода"),
        types.KeyboardButton(text="🎮 Играть"),
        types.KeyboardButton(text="📊 Статистика"),
        types.KeyboardButton(text="❓ Помощь"),
        types.KeyboardButton(text="❄️ Заморозить Андрея"),
        types.KeyboardButton(text="🌍 Случайный факт")
    )
    builder.adjust(3, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def weather_menu():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="📍 Иркутск", callback_data="city_Иркутск"),
        types.InlineKeyboardButton(text="📍 Москва", callback_data="city_Москва"),
        types.InlineKeyboardButton(text="📍 СПб", callback_data="city_Санкт-Петербург"),
        types.InlineKeyboardButton(text="✏️ Другой город", callback_data="other_city")
    )
    builder.adjust(2)
    return builder.as_markup()


# Команды бота
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь")
    ]
    await bot.set_my_commands(commands)


# Обработчики
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            'score': 0,
            'games_played': 0,
            'freeze_attempts': 0,
            'facts_viewed': 0,
            'last_fact': None,
            'last_freeze': None
        }

    await message.answer(
        "🌍 Добро пожаловать в WeatherWizard!\n"
        "Я помогу вам с прогнозом погоды и развлеку интересной игрой!",
        reply_markup=main_menu()
    )


@dp.message(F.text == "🌍 Случайный факт")
async def weather_fact(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await start(message)
        return

    last_fact = user_data[user_id].get('last_fact')
    available_facts = [f for f in WEATHER_FACTS if f != last_fact] or WEATHER_FACTS

    selected_fact = random.choice(available_facts)
    user_data[user_id]['facts_viewed'] += 1
    user_data[user_id]['last_fact'] = selected_fact

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🎲 Ещё факт", callback_data="another_fact"))

    await message.answer(
        f"{random.choice(FACT_EMOJI)} <b>Знаете ли вы?</b>\n\n"
        f"{selected_fact}\n\n"
        f"🌀 Всего просмотрено фактов: {user_data[user_id]['facts_viewed']}",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "another_fact")
async def another_fact(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data:
        await callback.answer("Сначала нажмите /start")
        return

    last_fact = user_data[user_id].get('last_fact')
    available_facts = [f for f in WEATHER_FACTS if f != last_fact] or WEATHER_FACTS

    selected_fact = random.choice(available_facts)
    user_data[user_id]['facts_viewed'] += 1
    user_data[user_id]['last_fact'] = selected_fact

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🎲 Ещё факт", callback_data="another_fact"))

    await callback.message.edit_text(
        f"{random.choice(FACT_EMOJI)} <b>Знаете ли вы?</b>\n\n"
        f"{selected_fact}\n\n"
        f"🌀 Всего просмотрено фактов: {user_data[user_id]['facts_viewed']}",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.message(F.text == "❄️ Заморозить Андрея")
async def freeze_andrew(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await start(message)
        return

    target_user = "@AndrewBezotchestvo"
    last_freeze = user_data[user_id].get('last_freeze')

    if last_freeze and (datetime.now() - last_freeze).seconds < 60:
        await message.answer("🛑 Слишком часто! Попробуй через минуту")
        return

    user_data[user_id]['freeze_attempts'] += 1
    user_data[user_id]['last_freeze'] = datetime.now()

    freeze_msg = random.choice(WEATHER_EMOJI)
    thaw_temp = random.randint(1, 15)
    thaw_msg = random.choice(THAW_PHRASES).format(thaw_temp)

    response = (
        f"{freeze_msg}\n\n"
        f"{target_user} {thaw_msg}\n"
        f"🌀 Всего попыток заморозки: {user_data[user_id]['freeze_attempts']}"
    )

    await message.answer(response)


@dp.message(F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await start(message)
        return

    user = user_data[user_id]
    stats_msg = (
        f"📈 <b>Ваша статистика:</b>\n"
        f"🏆 Очков: {user['score']}\n"
        f"🎮 Сыграно игр: {user['games_played']}\n"
        f"❄️ Заморозок Андрея: {user['freeze_attempts']}\n"
        f"🌐 Просмотрено фактов: {user['facts_viewed']}"
    )

    await message.answer(stats_msg)


@dp.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    await message.answer(
        "🌀 <b>Доступные команды:</b>\n"
        "🌤 Текущая погода - получить прогноз\n"
        "🎮 Играть - начать игру 'Угадай температуру'\n"
        "📊 Статистика - показать вашу статистику\n\n"
        "<i>Используйте кнопки для навигации</i>"
    )


@dp.message(F.text == "🌤 Текущая погода")
async def weather_handler(message: types.Message):
    await message.answer("Выберите город:", reply_markup=weather_menu())


@dp.callback_query(F.data.startswith("city_"))
async def city_selected(callback: types.CallbackQuery):
    city = callback.data.split("_")[1]
    await get_and_send_weather(callback.message, city)
    await callback.answer()


async def get_and_send_weather(message: types.Message, city: str):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if response['cod'] != 200:
            raise Exception()

        weather_emoji = WEATHER_EMOJI[0]
        temp = response['main']['temp']

        await message.answer(
            f"{weather_emoji} <b>Погода в {city}:</b>\n"
            f"🌡 Температура: {temp}°C\n"
            f"💧 Влажность: {response['main']['humidity']}%\n"
            f"🌀 Давление: {response['main']['pressure']} гПа\n"
            f"🌬 Ветер: {response['wind']['speed']} м/с"
        )
    except Exception as e:
        logger.error(f"Ошибка получения погоды: {e}")
        await message.answer("⚠️ Не удалось получить данные. Попробуйте другой город.")


@dp.message(F.text == "🎮 Играть")
async def start_game(message: types.Message, state: FSMContext):
    cities = ['Москва', 'Иркутск', 'Сочи', 'Владивосток', 'Калининград']
    target_city = random.choice(cities)

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={target_city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if response['cod'] != 200:
            raise Exception()

        await state.update_data(
            target_temp=round(response['main']['temp']),
            attempts=3,
            city=target_city
        )

        await message.answer(
            f"🎮 <b>Угадай температуру!</b>\n"
            f"В городе {target_city} сейчас температура...\n"
            f"У тебя 3 попытки! Введи число:"
        )
        await state.set_state(GameStates.playing)
    except Exception as e:
        logger.error(f"Ошибка запуска игры: {e}")
        await message.answer("⚠️ Игра временно недоступна")


@dp.message(GameStates.playing)
async def game_process(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        user_guess = int(message.text)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="🎮 Играть снова", callback_data="play_again"))

        if user_guess == data['target_temp']:
            user_data[message.from_user.id]['score'] += 10
            await message.answer(
                f"🎉 <b>Правильно!</b>\n"
                f"Температура в {data['city']}: {data['target_temp']}°C\n"
                f"+10 очков! Твой счет: {user_data[message.from_user.id]['score']}",
                reply_markup=builder.as_markup()
            )
            await state.clear()
            return

        data['attempts'] -= 1
        await state.update_data(attempts=data['attempts'])

        if data['attempts'] > 0:
            hint = "🔼 Теплее!" if user_guess < data['target_temp'] else "🔽 Холоднее!"
            await message.answer(
                f"{hint}\n"
                f"Осталось попыток: {data['attempts']}"
            )
        else:
            user_data[message.from_user.id]['score'] -= 5
            await message.answer(
                f"💥 <b>Игра окончена!</b>\n"
                f"Правильный ответ: {data['target_temp']}°C\n"
                f"-5 очков. Твой счет: {user_data[message.from_user.id]['score']}",
                reply_markup=builder.as_markup()
            )
            await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    except Exception as e:
        logger.error(f"Ошибка в игре: {e}")
        await message.answer("⚠️ Произошла ошибка, игра прервана")
        await state.clear()


@dp.callback_query(F.data == "play_again")
async def play_again(callback: types.CallbackQuery, state: FSMContext):
    await start_game(callback.message, state)
    await callback.answer()
# Запуск и завершение работы
async def on_startup():
    await set_bot_commands()
    logger.info("Бот успешно запущен!")


async def on_shutdown():
    logger.info("Бот корректно завершает работу...")
    await bot.session.close()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот завершил работу по запросу пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
