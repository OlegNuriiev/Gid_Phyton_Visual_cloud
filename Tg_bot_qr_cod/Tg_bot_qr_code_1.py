import telebot
from path import Path
from main import gen_qr_code


TOKEN = '6266569409:AAFMguAZSCtIuU9148KhfakQuDKGqY9XEQU'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Пришли мне сначала картинку, а потом текст и я сделаю из этого QR-Code!")


@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    global path_to_download
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = 'C:/Users/GameMax/Desktop/Visual_cloud_Python/Gid_Phyton_Visual_cloud' + message.document.file_name;
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        path_to_download = Path().joinpath(src)
        bot.reply_to(message, "Пожалуй, я сохраню это")
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler()
def send_text_based_qr(message):
    global path_to_download
    try:
        path_to_save = Path().joinpath("qr_code.png")
        print('path_to_save', path_to_save)
        gen_qr_code(message.text, path_to_download, path_to_save)
        bot.reply_to(message, 'Ваш текст принят!\nОжидайте.')
        with open('qr_code.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
            bot.send_message(message.chat.id, 'Ваш QR-Code готов!')
    except Exception:
        bot.reply_to(message, "Привет! Пришли мне сначала картинку, а потом текст и я сделаю из этого QR-Code!")


bot.polling(none_stop=True)
