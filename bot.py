import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode

logging.basicConfig(level=logging.INFO)

bot = Bot("8187537776:AAFLKIMCLu9hP65zDq6xsdl5bxhtw-8W_dU", parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ============================
# ХРАНИЛКА ДАННЫХ
# ============================

state = {
    "rate": 0,          # курс руб/доллар
    "percent": 0,       # % посредника
    "accepted_rub": 0,  # принято в рублях (основная сумма)
    "accepted_today": 0,# принято за день (не сбрасывается reset)
    "last_ops": []      # список последних операций
}


# ============================
# ПОДСЧЁТ И ВЫВОД
# ============================

def format_output():
    if state["rate"] == 0:
        return "Курс не установлен. Используйте: /set <курс> <процент>"

    usd = state["accepted_rub"] / state["rate"]
    payout = usd * (1 - state["percent"] / 100)

    last_ops_text = "\n".join(state["last_ops"][-3:]) if state["last_ops"] else "Нет операций"

    return (
        f"<b>Принято:</b> {state['accepted_rub']} руб / {usd:.2f} $\n"
        f"<b>К выплате:</b> {payout:.2f} $\n\n"
        f"{last_ops_text}\n\n"
        f"<b>Принято за день:</b> {state['accepted_today']} руб"
    )


# ============================
# КОМАНДА /set
# ============================

@dp.message(Command("set"))
async def cmd_set(message: Message):
    try:
        _, rate, percent = message.text.split()
        state["rate"] = float(rate)
        state["percent"] = float(percent)
        await message.reply(f"Установлено: курс = {rate}, процент = {percent}%")
    except:
        await message.reply("Использование: /set <курс> <процент>")


# ============================
# ОБРАБОТКА +100 / -50
# ============================

@dp.message(F.text.regexp(r"^[+-]\d+"))
async def add_or_sub(message: Message):
    val = int(message.text)
    state["accepted_rub"] += val
    state["accepted_today"] += max(val, 0)

    # добавляем в список операций
    state["last_ops"].append(message.text)
    if len(state["last_ops"]) > 3:
        state["last_ops"] = state["last_ops"][-3:]

    await message.reply(format_output())


# ============================
# /reset – обнулить 1 и 2 сумму
# ============================

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    state["accepted_rub"] = 0
    state["last_ops"] = []
    await message.reply("Основные суммы обнулены.\n" + format_output())


# ============================
# /null – полная очистка
# ============================

@dp.message(Command("null"))
async def cmd_null(message: Message):
    for key in state:
        if isinstance(state[key], list):
            state[key] = []
        else:
            state[key] = 0

    await message.reply("Все суммы полностью обнулены.")


# ============================
# СТАРТ
# ============================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
