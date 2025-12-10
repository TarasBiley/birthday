import telebot
from telebot import types
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# =============== НАСТРОЙКИ =====================

TOKEN = "8589937617:AAGG3nV0VWs-ejrskJvrSnQaXkv8pgdMUKU"  # <--- ВСТАВЬ НОВЫЙ ТОКЕН!!!
OWNER_CHAT_ID = 370839075      # <--- ВСТАВЬ СВОЙ TELEGRAM ID!!!

# ===============================================

birthdays = [
    {"name": "Мама Эльдара", "date": "10.01"},
    {"name": "Никита", "date": "15.01"},
    {"name": "Саша(Полина Смоголюк)", "date": "23.01"},

    {"name": "Стас", "date": "08.02"},
    {"name": "Паша Белых", "date": "10.02"},
    {"name": "Милана", "date": "12.02"},
    {"name": "Максим Кисин", "date": "17.02"},

    {"name": "Женя", "date": "15.04"},
    {"name": "Бабушка", "date": "16.04"},
    {"name": "Папа", "date": "18.04"},
    {"name": "Катя", "date": "23.04"},
    {"name": "Соня", "date": "27.04"},

    {"name": "Линар", "date": "10.05"},
    {"name": "Лиза(Дамир)", "date": "14.05"},
    {"name": "Руслан Баккасов", "date": "17.05"},
    {"name": "Миша Иванов", "date": "25.05"},

    {"name": "Рамиль", "date": "09.06"},
    {"name": "Нандо", "date": "08.06"},
    {"name": "Дима Пхукет", "date": "11.06"},
    {"name": "Дима Дубков", "date": "22.06"},

    {"name": "Егорчик", "date": "02.07"},
    {"name": "Гавр", "date": "03.07"},
    {"name": "Пашик", "date": "05.07"},
    {"name": "Гриша Вязников", "date": "06.07"},

    {"name": "Ефик", "date": "08.08"},

    {"name": "Слава Бабин", "date": "19.09"},
    {"name": "Мама", "date": "29.09"},

    {"name": "Тетя Галя", "date": "05.10"},

    {"name": "Камиля", "date": "03.11"},
    {"name": "Аня Кострова", "date": "06.11"},
    {"name": "Тетя Ирина", "date": "11.12"},
    {"name": "Слава", "date": "22.11"},
    {"name": "Абика", "date": "26.11"},

    {"name": "Тетя Леня", "date": "01.12"},
    {"name": "Игнат", "date": "05.12"},
    {"name": "Кирилл Пхукет", "date": "08.12"},
    {"name": "Андрей Пхукет", "date": "08.12"},
    {"name": "Дамир", "date": "10.12"},
    {"name": "Вадик Владик", "date": "15.12"},
    {"name": "Дима", "date": "16.12"},
    {"name": "Олег протектор", "date": "20.12"},
    {"name": "Васева Лера", "date": "21.12"},
    {"name": "Гошик", "date": "23.12"}
]

# ===============================================

bot = telebot.TeleBot(TOKEN)

# ---------- УТИЛИТЫ ----------

def get_birthdays_for(date_str):
    return [p["name"] for p in birthdays if p["date"] == date_str]


def get_birthdays_for_month(month_int):
    month_str = f"{month_int:02d}"
    result = []
    for person in birthdays:
        day, month = person["date"].split(".")
        if month == month_str:
            result.append(f"{day}.{month} — {person['name']}")
    return result


# ---------- УВЕДОМЛЕНИЯ ТОЛЬКО ТЕБЕ ----------

def send_today():
    today = datetime.now().strftime("%d.%m")
    names = get_birthdays_for(today)
    if not names:
        return

    bot.send_message(
        OWNER_CHAT_ID,
        "🎉 Сегодня день рождения:\n" + "\n".join(f"🎂 {n}" for n in names)
    )


def send_tomorrow():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    names = get_birthdays_for(tomorrow)
    if not names:
        return

    bot.send_message(
        OWNER_CHAT_ID,
        "⏰ Напоминание!\nЗавтра день рождения у:\n" + "\n".join(f"🎂 {n}" for n in names)
    )


# ---------- КОНСТАНТНАЯ КЛАВИАТУРА ----------

def month_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row1 = [types.KeyboardButton(str(i)) for i in range(1, 7)]
    row2 = [types.KeyboardButton(str(i)) for i in range(7, 13)]
    markup.add(*row1)
    markup.add(*row2)
    return markup


# ---------- ОБРАБОТКА ТОЛЬКО ТВОИХ СООБЩЕНИЙ ----------

def is_owner(message):
    return message.chat.id == OWNER_CHAT_ID


@bot.message_handler(commands=['start'])
def cmd_start(message):
    if not is_owner(message):
        return  # игнорируем чужих

    bot.send_message(
        OWNER_CHAT_ID,
        "Привет! 👋\n"
        "Я напомню тебе о днях рождения:\n"
        "• СЕГОДНЯ 🎉\n"
        "• ЗАВТРА ⏰\n\n"
        "Снизу кнопки 1–12 — выбери месяц.\n\n"
        "Показываю ближайшие:",
        reply_markup=month_keyboard()
    )

    send_today()
    send_tomorrow()


@bot.message_handler(commands=['today'])
def cmd_today(message):
    if is_owner(message):
        send_today()


@bot.message_handler(commands=['tomorrow'])
def cmd_tomorrow(message):
    if is_owner(message):
        send_tomorrow()


@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def cmd_month(message):
    if not is_owner(message):
        return

    num = int(message.text)
    if not (1 <= num <= 12):
        return

    entries = get_birthdays_for_month(num)
    if entries:
        bot.reply_to(message, f"🎂 Дни рождения в месяце {num}:\n" + "\n".join(entries))
    else:
        bot.reply_to(message, f"В месяце {num} нет дней рождения.")


# ---------- ПЛАНИРОВЩИК ----------

scheduler = BackgroundScheduler(timezone=timezone("Europe/Moscow"))

scheduler.add_job(send_tomorrow, 'cron', hour=9, minute=0)
scheduler.add_job(send_today, 'cron', hour=9, minute=5)

scheduler.start()

print("Бот запущен…")
bot.infinity_polling()
