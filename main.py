import os
from utils.model import bot, user_limits, query
from utils.utils import format_process, only_document, with_caption


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="*===== Cara Penggunaan =====*\n\nKirimkan file txt dengan caption query dan format untuk membungkus isi dari file txtnya, *Contoh : *\n\nSELECT order, customer FROM orders WHERE status IN ($); format (1, $)\n\ndan misal file yang anda inputkan hanya berisi 1 kata yaitu *contoh isi file*\n*Maka Outputnya akan seperti dibawah ini*\n\nSELECT order, customer FROM orders WHERE status IN (1, 'contoh isi file');\n\nJangan menggunakan *Enter* untuk memisahkan query dan format, misalnya\n\nSELECT order, customer FROM orders WHERE status IN ($);\nformat (1, $)\n\n==== Note ====\n\n- Jangan lupa untuk memberikan keyword *$* pada query dan pada format\n- Anda bisa juga mengirimkan file tanpa caption namun formatnya menggunakan default format",
        parse_mode="Markdown",
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

        if not query or query[chat_id] == ():
            format_process(file_name, limit, chat_id)
        else:
            first = query[chat_id][0]
            second = query[chat_id][1]
            first_format = query[chat_id][2]
            second_format = query[chat_id][3]
            format_process(
                file_name, limit, chat_id, first, second, first_format, second_format
            )

        # Hapus entry pengguna setelah selesai
        del user_limits[chat_id]
    except ValueError:
        bot.reply_to(message, "Silakan masukkan angka yang valid.")


bot.infinity_polling()
