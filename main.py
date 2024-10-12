import os
import telebot
import io

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

user_limits = {}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="bot masih dalam masa percobaan dan hanya bisa menjadi format (1, '')\nlangsung saja kirimkan file txtnya",
    )


@bot.message_handler(content_types=["document"])
def handle_document(message):

    file_name = message.document.file_name
    file_extension = os.path.splitext(file_name)[1]

    if file_extension.lower() != ".txt":
        bot.reply_to(message, "selain .txt gk boleh yh")
        return

    document_id = message.document.file_id

    # Gunakan ID file untuk mendapatkan informasi file
    file_info = bot.get_file(document_id)

    # Unduh file menggunakan jalur file
    downloaded_file = bot.download_file(file_info.file_path)

    # Simpan file ke sistem file lokal
    with open(file_name, "wb") as new_file:
        new_file.write(downloaded_file)

    # Minta pengguna untuk memasukkan batas
    bot.reply_to(
        message,
        "Silakan masukkan batas jumlah baris per file (misal: 10000)\n/skip untuk langsung convert",
    )

    # Simpan ID pengguna dan nama file untuk referensi selanjutnya
    user_limits[message.chat.id] = (file_name, None)


# Fungsi untuk menangani teks yang dimasukkan pengguna
@bot.message_handler(func=lambda message: message.chat.id in user_limits)
def handle_limit_input(message):

    if message.text == "/skip":
        with open(user_limits[message.chat.id][0], "r") as f:
            lines = f.readlines()
            limit = len(lines)
    else:
        limit = int(message.text)

    try:  # Mengonversi input ke integer
        file_name, _ = user_limits[message.chat.id]
        user_limits[message.chat.id] = (file_name, limit)

        process_file(file_name, limit, message.chat.id)

        # Hapus entry pengguna setelah selesai
        del user_limits[message.chat.id]
    except ValueError:
        bot.reply_to(message, "Silakan masukkan angka yang valid.")


def process_file(file_name, limit, chat_id):
    # Membaca konten file
    with open(file_name, "r") as f:
        lines = f.readlines()  # Baca semua baris sekaligus

    # Memisahkan baris menjadi beberapa file jika lebih dari batas yang ditentukan
    num_lines = len(lines)
    num_files = (num_lines + limit - 1) // limit  # Hitung jumlah file yang dibutuhkan

    output_file_names = []  # List untuk menyimpan nama file output
    for i in range(num_files):
        start_index = i * limit
        end_index = min(start_index + limit, num_lines)
        # Mengambil baris untuk file saat ini
        current_lines = lines[start_index:end_index]

        # Membuat nama file output
        output_file_name = f"formatted_output_{i + 1}.txt"
        output_file_names.append(output_file_name)

        # Menyimpan hasil format ke file baru
        formatted_lines = []
        for line in current_lines:
            formatted_line = f"(1, '{line.strip()}'),"
            formatted_lines.append(formatted_line)

        if formatted_lines:
            formatted_lines[-1] = formatted_lines[-1][:-1]

        with open(output_file_name, "w") as output_file:
            output_file.write("\n".join(formatted_lines))

    for output_file_name in output_file_names:
        with open(output_file_name, "rb") as output_file:
            bot.send_document(chat_id=chat_id, document=output_file)
        os.remove(output_file_name)

    os.remove(file_name)

    bot.send_message(chat_id, text="silahkan cek hasilnya kembali")

bot.infinity_polling()
