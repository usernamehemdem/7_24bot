from keep_alive import keep_alive
keep_alive()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json

with open('ulanyjylar.json', 'r') as file:
    ulanyjylar = json.load(file)

with open('kanallar.json', 'r') as file:
    kanallar = json.load(file)

TOKEN = "6722132156:AAGqWZzUsYC1EGnH3uLD1P65XBhnm_3h6D0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ulanyjylar:
        ulanyjylar.append(user_id)
        with open('ulanyjylar.json', 'w') as file:
            json.dump(ulanyjylar, file)
    await update.message.reply_text("Botdan doly peýdalanmak üçin aşakdaky kanallara agza boluň. Soňra /vpn ýaz:\n\n"
                                    + "\n".join(kanallar['ADMIN_KANALLAR'] + kanallar['BEÝLEKI_KANALLAR']))

async def vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ulanyjylar:
        await update.message.reply_text("Kod: `1234567890`", parse_mode='Markdown')
    else:
        await update.message.reply_text("Ilki bilen /start ýaz")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("vpn", vpn))
app.run_polling()
