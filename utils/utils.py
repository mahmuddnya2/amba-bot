from utils.model import bot, user_limits, query
import os

valid_input = ["/start", "/skip"]


def known_input(message):
    print(message.text)
    if message.text not in valid_input:
        bot.reply_to(message, "Input yang anda masukkan tidak Valid")


def format_process(file_name, limit, chat_id, first="", second=""):
    print(first)
    print(second)
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
            print()
            output_file.write("\n".join(formatted_lines))

    # Mengirimkan file yang telah diformat
    try:
        for output_file_name in output_file_names:
            with open(output_file_name, "rb") as output_file:
                bot.send_document(chat_id, document=output_file)
            # Menghapus file yang telah dikirim dari local
            os.remove(output_file_name)
    except ValueError:
        bot.send_message(chat_id, "bot gagal mengirim file")
        for output_file_name in output_file_names:
            os.remove(output_file_name)
        os.remove(file_name)

    # Menghapus file di local yang dikirim oleh user
    os.remove(file_name)
    query[chat_id] = ()

    bot.send_message(chat_id, text="silahkan cek hasilnya kembali")


def file_handler(message):
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
    return file_name


def only_document(message):

    file_name = file_handler(message)

    # Minta pengguna untuk memasukkan batas
    bot.reply_to(
        message,
        "Silakan masukkan batas jumlah baris per file (misal: 10000)\n/skip untuk langsung convert\n/default untuk per 10000",
    )

    # Simpan ID pengguna dan nama file untuk referensi selanjutnya
    user_limits[message.chat.id] = (file_name, None)


def with_caption(message):
    sparate_messsage = message.caption
    sparate_messsage = sparate_messsage.split("$")

    if len(sparate_messsage) < 2:
        bot.send_message(
            chat_id=message.chat.id,
            text="Gunakan karakter $ untuk memisahkan query, contoh : \n SELECT * FROM pelanggan WHERE kota IN ($);",
        )

    first = sparate_messsage[0]
    second = sparate_messsage[1]

    query[message.chat.id] = (first, second)

    file_name = file_handler(message)

    # Minta pengguna untuk memasukkan batas
    bot.reply_to(
        message,
        "Silakan masukkan batas jumlah baris per file (misal: 10000)\n/skip untuk langsung convert\n/default untuk per 10000",
    )

    # Simpan ID pengguna dan nama file untuk referensi selanjutnya
    user_limits[message.chat.id] = (file_name, None)
