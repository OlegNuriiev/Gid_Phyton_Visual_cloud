import logging
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Ваш токен Telegram бота
BOT_TOKEN = "7761288626:AAGFJ91X467G8mJcsQG-tH10eupSaiP54C8"

# Список криптовалют
CRYPTOCURRENCIES = [
    "XRPUSDT", "DOGEUSDT", "SOLUSDT", "SHIBUSDT", "THEUSDT",
    "ACXUSDT", "TONUSDT", "BONKUSDT", "DOGSUSDT", "SNXUSDT"
]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Получение курса криптовалют с Binance API
def get_crypto_prices():
    url = "https://api.binance.com/api/v3/ticker/price"
    prices = {}
    for symbol in CRYPTOCURRENCIES:
        try:
            response = requests.get(url, params={"symbol": symbol})
            response.raise_for_status()  # Поднимет исключение, если статус код не 200
            price = response.json().get("price", None)
            if price:
                prices[symbol] = float(price)
            else:
                prices[symbol] = "N/A"  # Если данные не получены
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса для {symbol}: {e}")
            prices[symbol] = "N/A"  # Если возникла ошибка
    logger.info(f"Полученные курсы: {prices}")
    return prices

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Привет! Я мониторю курс следующих криптовалют:\n" + ", ".join(
        CRYPTOCURRENCIES) + "\nКурс будет отправляться раз в 6 часов."
    await update.message.reply_text(message)

# Отправка курса в Telegram
async def send_scheduled_prices(application):
    logger.info("Запрос курса криптовалют...")
    prices = get_crypto_prices()

    if not prices:
        logger.warning("Курсы криптовалют не получены!")
        return

    # Форматируем вывод, чтобы избежать экспоненциальной записи и удалить 'USDT' из названия монеты
    formatted_prices = [
        f"{symbol.replace('USDT', '')}: {float(price):.8f} $" if isinstance(price, float) else f"{symbol.replace('USDT', '')}: {price} $"
        for symbol, price in prices.items()
    ]

    message = "\n".join(formatted_prices)

    if not message.strip():  # Проверка на пустое сообщение
        logger.warning("Сообщение пустое. Курсы криптовалют не получены.")
        return

    chat_id = "535261119"  # Укажите правильный ID чата
    await application.bot.send_message(chat_id=chat_id, text=f"Текущий курс:\n{message}")
    logger.info("Сообщение отправлено.")

# Запуск регулярной отправки курса
def schedule_crypto_updates(application):
    # Отправка первого сообщения сразу
    application.job_queue.run_once(lambda context: asyncio.create_task(send_scheduled_prices(application)), 0)

    # Регулярная отправка курса каждую минуту
    application.job_queue.run_repeating(lambda context: asyncio.create_task(send_scheduled_prices(application)),
                                        interval=60, first=0)

    logger.info("Планировщик настроен.")

def main():
    # Создание приложения
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавление обработчиков
    app.add_handler(CommandHandler("start", start))

    # Планирование обновлений
    schedule_crypto_updates(app)

    # Запуск бота
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
