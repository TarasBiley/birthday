import telebot
from telebot import types
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# =============== НАСТРОЙКИ =====================

TOKEN = "8589937617:AAGG3nV0VWs-ejrskJvrSnQaXkv8pgdMUKU"

birthdays = [
    # ----- ЯНВАРЬ -----
    {"name": "Мама Эльдара", "date": "10.01"},
    {"name": "Никита", "date": "15.01"},
    {"name": "Саша(Полина Смоголюк)", "date": "23.01"},

    # ----- ФЕВРАЛЬ -----
    {"name": "Стас", "date": "08.02"},
    {"name": "Паша Белых", "date": "10.02"},
    {"name": "Милана", "date": "12.02"},
    {"name": "Максим Кисин", "date": "17.02"},

    # ----- МАРТ -----
    # (нет дней рождения)

    # ----- АПРЕЛЬ -----
    {"name": "Женя", "date": "15.04"},
    {"name": "Бабушка", "date": "16.04"},
    {"name": "Папа", "date": "18.04"},
    {"name": "Катя", "date": "23.04"},
    {"name": "Соня", "date": "27.04"},

    # ----- МАЙ -----
    {"name": "Линар", "date": "10.05"},
    {"name": "Лиза(Дамир)", "date": "14.05"},
    {"name": "Руслан Баккасов", "date": "17.05"},
    {"name": "Миша Иванов", "date": "25.05"},

    # ----- ИЮНЬ -----
    {"name": "Рамиль", "date": "09.06"},
    {"name": "Дима Пхукет", "date": "11.06"},
    {"name": "Дима Дубков", "date": "22.06"},

    # ----- ИЮЛЬ -----
    {"name": "Егорчик", "date": "02.07"},
    {"name": "Гавр", "date": "03.07"},
    {"name": "Пашик", "date": "05.07"},
    {"name": "Гриша Вязников", "date": "06.07"},

    # ----- АВГУСТ -----
    {"name": "Ефик", "date": "08.08"},

    # ----- СЕНТЯБРЬ -----
    {"name": "Слава Бабин", "date": "19.09"},
    {"name": "Мама", "date": "29.09"},

    # ----- ОКТЯБРЬ -----
    {"name": "Тетя Галя", "date": "05.10"},

    # ----- НОЯБРЬ -----
    {"name": "Камиля", "date": "03.11"},
    {"name": "Аня Кострова", "date": "06.11"},
    {"name": "Тетя Ирина", "date": "21.11"},
    {"name": "Слава", "date": "22.11"},
    {"name": "Абика", "date": "26.11"},

    # ----- ДЕКАБРЬ -----
    {"name": "Тетя Леня", "date": "01.12"},
    {"name": "Игнат", "date": "05.12"},
    {"name": "Кирилл Пхукет", "date": "08.12"},
    {"name": "Дамир", "date": "10.12"},
    {"name": "Вадик Владик", "date": "15.12"},
    {"name": "Дима", "date": "16.12"},
    {"name": "Олег протектор", "date": "20.12"},
    {"name": "Васева Лера", "date": "21.12"},
    {"name": "Гошик", "date": "23.12"}
]



# ===============================================

bot = telebot.TeleBot(TOKEN)
chat_ids = set()   # храним всех пользователей, которые сделали /start


# ---------- УТИЛИТЫ ----------

def get_birthdays_for(date_str):
    """Возвращает всех людей, у кого ДР в указанную дату (ДД.ММ)."""
    return [p["name"] for p in birthdays if p["date"] == date_str]


def get_birthdays_for_month(month_int):
    """
    Возвращает список строк вида 'ДД.ММ — Имя'
    для указанного месяца (1–12).
    """
    month_str = f"{month_int:02d}"  # '1' -> '01'
    result = []
    for person in birthdays:
        day, month = person["date"].split(".")
        if month == month_str:
            result.append(f"{day}.{month} — {person['name']}")
    return result


# ---------- РАССЫЛКА ВСЕМ ----------

def send_today_all():
    today = datetime.now().strftime("%d.%m")
    names = get_birthdays_for(today)

    if not names:
        return

    text = "🎉 Сегодня день рождения:\n" + "\n".join(f"🎂 {n}" for n in names)
    for cid in list(chat_ids):
        bot.send_message(cid, text)


def send_tomorrow_all():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    names = get_birthdays_for(tomorrow)

    if not names:
        return

    text = "⏰ Напоминание!\nЗавтра день рождения у:\n" + "\n".join(f"🎂 {n}" for n in names)
    for cid in list(chat_ids):
        bot.send_message(cid, text)


# ---------- ОТПРАВКА ОДНОМУ ----------

def send_today_one(cid):
    today = datetime.now().strftime("%d.%m")
    names = get_birthdays_for(today)

    if not names:
        bot.send_message(cid, "Сегодня в списке нет дней рождения.")
        return

    bot.send_message(cid, "Сегодня день рождения:\n" + "\n".join(f"🎂 {n}" for n in names))


def send_tomorrow_one(cid):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    names = get_birthdays_for(tomorrow)

    if not names:
        bot.send_message(cid, "На завтра нет дней рождения.")
        return

    bot.send_message(cid, "Напоминание!\nЗавтра день рождения у:\n" + "\n".join(f"🎂 {n}" for n in names))


# ---------- КНОПКИ МЕСЯЦЕВ ----------

def month_keyboard():
    """Клавиатура с кнопками 1–12."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row1 = [types.KeyboardButton(str(i)) for i in range(1, 7)]   # 1 2 3 4 5 6
    row2 = [types.KeyboardButton(str(i)) for i in range(7, 13)]  # 7 8 9 10 11 12
    markup.add(*row1)
    markup.add(*row2)
    return markup


# ---------- КОМАНДЫ ----------

@bot.message_handler(commands=['start'])
def start(message):
    chat_ids.add(message.chat.id)

    bot.send_message(
        message.chat.id,
        "Привет! 👋\n"
        "Я буду напоминать:\n"
        "• кто празднует ДР СЕГОДНЯ 🎉\n"
        "• кто празднует ЗАВТРА ⏰\n\n"
        "Также снизу есть кнопки с номерами месяцев (1–12).\n"
        "Нажми, чтобы посмотреть все дни рождения в выбранном месяце.\n\n"
        "Показываю ближайшие:",
        reply_markup=month_keyboard()
    )

    send_today_one(message.chat.id)
    send_tomorrow_one(message.chat.id)


@bot.message_handler(commands=['today'])
def cmd_today(message):
    send_today_one(message.chat.id)


@bot.message_handler(commands=['tomorrow'])
def cmd_tomorrow(message):
    send_tomorrow_one(message.chat.id)


# ---------- ОБРАБОТКА НАЖАТИЯ КНОПОК МЕСЯЦЕВ ----------

@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and 1 <= int(m.text) <= 12)
def handle_month_buttons(message):
    month_num = int(message.text)
    entries = get_birthdays_for_month(month_num)

    if entries:
        text = f"Дни рождения в месяце {month_num}:\n" + "\n".join(f"🎂 {line}" for line in entries)
    else:
        text = f"В месяце {month_num} нет дней рождения в списке."

    bot.reply_to(message, text)


# ---------- ПЛАНИРОВЩИК (ПО ВРЕМЕНИ СЕРВЕРА) ----------

scheduler = BackgroundScheduler()

# Каждый день в 09:00 — напоминание за день
scheduler.add_job(send_tomorrow_all, 'cron', hour=9, minute=0)

# Каждый день в 09:05 — напоминание на сегодня
scheduler.add_job(send_today_all, 'cron', hour=9, minute=5)

scheduler.start()

print("Бот запущен...")
bot.infinity_polling()
