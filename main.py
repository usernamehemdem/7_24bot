import json
import os
import asyncio
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Ortam değişkenleri
TOKEN = os.getenv("7833501671:AAFnHrXf4Wu3yjMWXu_rbXOu5FYapmrJRwU")
ADMIN_ID = int(os.getenv("5330851495"))

DATA_FILE = "data.json"

# Veri dosyasını yükle / oluştur
def load_data():
    if not os.path.exists(DATA_FILE):
        default = {
            "channel": "@YOUR_CHANNEL",
            "interval": 3600,   # saniye cinsinden, örn 3600 = 1 saat
            "days": 1,
            "posts": [],
            "last_message_id": None,
            "is_posting": False,
            "start_time": None,
            "current_index": 0
        }
        with open(DATA_FILE, "w") as f:
            json.dump(default, f, indent=2)
        return default
    else:
        with open(DATA_FILE, "r") as f:
            return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

async def post_next(app: Application):
    if not data["is_posting"]:
        return
    
    now = datetime.utcnow()
    start = datetime.fromisoformat(data["start_time"])
    elapsed = (now - start).total_seconds()
    if elapsed >= data["days"] * 86400:
        data["is_posting"] = False
        save_data(data)
        await app.bot.send_message(ADMIN_ID, "✅ Gönderim süresi tamamlandı, otomatik gönderim durduruldu.")
        return
    
    chat_id = data["channel"]
    idx = data["current_index"] % len(data["posts"])
    text = data["posts"][idx]

    # Eski mesajı sil
    if data["last_message_id"] is not None:
        try:
            await app.bot.delete_message(chat_id, data["last_message_id"])
        except Exception as e:
            print(f"Mesaj silinemedi: {e}")

    # Yeni mesaj gönder
    msg = await app.bot.send_message(chat_id, text)
    data["last_message_id"] = msg.message_id
    data["current_index"] += 1
    save_data(data)

async def schedule_posting(app: Application):
    while True:
        if data["is_posting"]:
            await post_next(app)
        await asyncio.sleep(data["interval"])

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            await update.message.reply_text("🚫 Yetkiniz yok.")
            return
        await func(update, context)
    return wrapper

@admin_only
async def setchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Kullanım: /setchannel @kanaladi")
        return
    data["channel"] = context.args[0]
    save_data(data)
    await update.message.reply_text(f"✅ Kanal ayarlandı: {data['channel']}")

@admin_only
async def setinterval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Kullanım: /setinterval dakika_sayisi (örn: /setinterval 60)")
        return
    try:
        dakika = int(context.args[0])
        data["interval"] = dakika * 60
        save_data(data)
        await update.message.reply_text(f"✅ Gönderim aralığı {dakika} dakika olarak ayarlandı.")
    except:
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")

@admin_only
async def setdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Kullanım: /setdays gün_sayisi (örn: /setdays 3)")
        return
    try:
        gun = int(context.args[0])
        data["days"] = gun
        save_data(data)
        await update.message.reply_text(f"✅ Gönderilecek gün sayısı {gun} olarak ayarlandı.")
    except:
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")

@admin_only
async def addpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.partition(" ")[2]
    if not text:
        await update.message.reply_text("Kullanım: /addpost Mesaj içeriği")
        return
    data["posts"].append(text)
    save_data(data)
    await update.message.reply_text(f"✅ Mesaj eklendi. Toplam {len(data['posts'])} mesaj var.")

@admin_only
async def removepost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Kullanım: /removepost mesaj_no (örn: /removepost 2)")
        return
    try:
        idx = int(context.args[0]) - 1
        if 0 <= idx < len(data["posts"]):
            removed = data["posts"].pop(idx)
            save_data(data)
            await update.message.reply_text(f"✅ Mesaj silindi: {removed}")
        else:
            await update.message.reply_text("Geçersiz mesaj numarası.")
    except:
        await update.message.reply_text("Geçersiz kullanım.")

@admin_only
async def startposting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(data["posts"]) == 0:
        await update.message.reply_text("❌ En az 1 mesaj eklemelisiniz.")
        return
    data["is_posting"] = True
    data["current_index"] = 0
    data["start_time"] = datetime.utcnow().isoformat()
    save_data(data)
    await update.message.reply_text("🚀 Otomatik gönderim başladı.")

@admin_only
async def stopposting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data["is_posting"] = False
    save_data(data)
    await update.message.reply_text("⏸ Otomatik gönderim durduruldu.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot hazır! Komutlar:\n"
                                    "/setchannel @kanaladi\n"
                                    "/setinterval dakika\n"
                                    "/setdays gun_sayisi\n"
                                    "/addpost mesaj\n"
                                    "/removepost mesaj_no\n"
                                    "/startposting\n"
                                    "/stopposting")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setchannel", setchannel))
    app.add_handler(CommandHandler("setinterval", setinterval))
    app.add_handler(CommandHandler("setdays", setdays))
    app.add_handler(CommandHandler("addpost", addpost))
    app.add_handler(CommandHandler("removepost", removepost))
    app.add_handler(CommandHandler("startposting", startposting))
    app.add_handler(CommandHandler("stopposting", stopposting))

    app.job_queue.run_repeating(lambda ctx: asyncio.create_task(post_next(app)), interval=1, first=1)

    print("Bot başlatıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
