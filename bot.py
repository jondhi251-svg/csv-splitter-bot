import os
import csv
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a CSV file to split into two parts.")

async def split_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc or not doc.file_name.lower().endswith(".csv"):
        await update.message.reply_text("Please send a CSV file.")
        return

    file = await doc.get_file()
    await file.download_to_drive("input.csv")

    with open("input.csv", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    if not rows:
        await update.message.reply_text("The file is empty.")
        return

    header, data = rows[0], rows[1:]
    mid = (len(data) + 1) // 2

    for name, part in [("part1.csv", data[:mid]), ("part2.csv", data[mid:])]:
        with open(name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(part)
        await update.message.reply_document(document=open(name, "rb"))

def main():
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, split_csv))
    app.run_polling()

if __name__ == "__main__":
    main()
