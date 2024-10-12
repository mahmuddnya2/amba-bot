import os
from utils.model import bot, user_limits, query
from utils.utils import format_process, only_document, with_caption


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="gunakan command /query untuk menginputkan query atau langsung kirimkan file txt jika tidak ingin menggunakan query",
    )


@bot.message_handler(content_types=["document"])
def handle_document(message):
    if message.caption == None:
        only_document(message)
    else:
        with_caption(message)


# Fungsi untuk menangani teks yang dimasukkan pengguna
@bot.message_handler(func=lambda message: message.chat.id in user_limits)
def handle_limit_input(message):

    chat_id = message.chat.id

    if message.text == "/skip":
        with open(user_limits[chat_id][0], "r") as f:
            lines = f.readlines()
            limit = len(lines)
    elif message.text == "/default":
        limit = 10000
    else:
        limit = int(message.text)

    try:  # Mengonversi input ke integer
        file_name, _ = user_limits[chat_id]
        user_limits[chat_id] = (file_name, limit)

        print(query)

        if not query or query[chat_id] == ():
            print("tidak ada query")
            format_process(file_name, limit, chat_id)
        else:
            first = query[chat_id][0]
            second = query[chat_id][1]
            format_process(file_name, limit, chat_id, first, second)

        # Hapus entry pengguna setelah selesai
        del user_limits[chat_id]
    except ValueError:
        bot.reply_to(message, "Silakan masukkan angka yang valid.")


bot.infinity_polling()
